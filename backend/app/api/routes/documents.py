from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.borrower_profile import BorrowerProfile
from app.models.document import Document
from app.rag.vector_store import VectorStoreService
from app.schemas.document import DocumentUploadResponse
from app.services.document_intelligence import DocumentProcessingService

router = APIRouter(prefix='/documents', tags=['documents'])
processing_service = DocumentProcessingService()
vector_store = VectorStoreService()
settings = get_settings()


@router.post('/upload', response_model=DocumentUploadResponse)
def upload_document(
    borrower_profile_id: int = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentUploadResponse:
    borrower = db.get(BorrowerProfile, borrower_profile_id)
    if not borrower:
        raise HTTPException(status_code=404, detail='Borrower profile not found')

    file_ext = Path(file.filename).suffix or '.bin'
    target_dir = Path(settings.uploads_dir) / str(borrower_profile_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{file_ext}"
    destination = target_dir / filename

    with destination.open('wb') as fh:
        fh.write(file.file.read())

    raw_text = processing_service.extract_text(destination)
    extracted = processing_service.extract_structured_data(raw_text)

    document_row = Document(
        borrower_profile_id=borrower_profile_id,
        filename=file.filename,
        document_type=document_type,
        storage_path=str(destination),
        raw_text=raw_text,
        extracted_json=extracted.model_dump(),
    )

    db.add(document_row)
    db.commit()
    db.refresh(document_row)

    vector_store.upsert_text(
        text=raw_text,
        metadata={
            'entity': 'document',
            'borrower_profile_id': borrower_profile_id,
            'document_id': document_row.id,
            'document_type': document_type,
        },
    )

    return DocumentUploadResponse(document=document_row, extracted_data=extracted)
