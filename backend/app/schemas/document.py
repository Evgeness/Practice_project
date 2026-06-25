from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Public metadata returned for an uploaded document."""

    id: str
    file_name: str
    file_type: str
    file_size: int
    status: str
    chunks_count: int
    error_message: str | None = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Paginated list of uploaded documents."""

    total: int
    items: list[DocumentResponse]
