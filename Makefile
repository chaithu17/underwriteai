.PHONY: backend frontend test docker-up docker-down

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest -q

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
