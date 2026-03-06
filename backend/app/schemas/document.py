from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentFinancialData(BaseModel):
    employer: str | None = None
    annual_income: float | None = None
    bank_balance: float | None = None
    pay_frequency: str | None = None
    detected_debts: float | None = None


class DocumentRead(BaseModel):
    id: int
    borrower_profile_id: int
    filename: str
    document_type: str
    raw_text: str
    extracted_json: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    extracted_data: DocumentFinancialData
