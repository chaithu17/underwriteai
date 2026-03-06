from fastapi import APIRouter

from app.api.routes import borrowers, documents, health, reports, scenarios, underwriting

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(borrowers.router)
api_router.include_router(documents.router)
api_router.include_router(underwriting.router)
api_router.include_router(scenarios.router)
api_router.include_router(reports.router)
