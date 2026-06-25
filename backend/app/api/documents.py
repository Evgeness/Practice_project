from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_elasticsearch, require_user
from app.core.config import Settings, get_settings
from app.models.database import get_db
from app.models.document import Document
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.chunking import chunk_text
from app.services.document_parser import DocumentValidationError, parse_document, validate_upload
from app.services.elasticsearch_service import ElasticsearchService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    elasticsearch: ElasticsearchService = Depends(get_elasticsearch),
    settings: Settings = Depends(get_settings),
    _username: str = Depends(require_user),
) -> Document:
    """Validate, parse, chunk and index one PDF or DOCX document."""
    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    try:
        safe_name, file_type = validate_upload(file.filename, data, settings.max_upload_mb)
    except DocumentValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document = Document(
        id=str(uuid4()),
        file_name=safe_name,
        file_type=file_type,
        file_size=len(data),
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        pages = parse_document(safe_name, data)
        chunks: list[dict[str, object]] = []
        chunk_number = 0
        for page_number, page_text in pages:
            for text in chunk_text(page_text, settings.chunk_size, settings.chunk_overlap):
                chunk_number += 1
                chunks.append(
                    {
                        "document_id": document.id,
                        "chunk_id": f"{document.id}:{chunk_number}",
                        "file_name": safe_name,
                        "page_number": page_number,
                        "text": text,
                    }
                )

        if not chunks:
            raise DocumentValidationError("Документ не содержит индексируемого текста")

        elasticsearch.index_chunks(chunks)
        document.status = "ready"
        document.chunks_count = len(chunks)
        document.error_message = None
        db.commit()
        db.refresh(document)
        return document
    except DocumentValidationError as exc:
        document.status = "error"
        document.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        document.status = "error"
        document.error_message = "Ошибка индексации"
        db.commit()
        raise HTTPException(status_code=500, detail="Не удалось обработать документ") from exc


@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _username: str = Depends(require_user),
) -> DocumentListResponse:
    """Return uploaded document metadata ordered by newest first."""
    total = db.scalar(select(func.count()).select_from(Document)) or 0
    items = list(
        db.scalars(
            select(Document)
            .order_by(Document.uploaded_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
    )
    return DocumentListResponse(total=total, items=items)
