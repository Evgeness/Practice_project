.PHONY: up down logs test lint build reset init

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f app front

test:
	cd backend && pytest --cov=app.services --cov=app.api --cov-report=term-missing

lint:
	cd backend && ruff check app tests
	cd frontend && npm run lint

build:
	docker compose build

reset:
	docker compose down -v

init:
	./init.sh
