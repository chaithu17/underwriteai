from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BorrowerProfileCreate(BaseModel):
    user_id: int | None = None
    annual_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    monthly_debts: float = Field(..., ge=0)
    assets: float = Field(..., ge=0)
    loan_amount: float = Field(..., gt=0)
    down_payment: float = Field(..., ge=0)
    property_value: float | None = Field(default=None, gt=0)
    credit_used: float = Field(default=0, ge=0)
    credit_limit: float = Field(default=1, gt=0)


class BorrowerProfileRead(BorrowerProfileCreate):
    id: int
    property_value: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BorrowerProfileUpdate(BaseModel):
    annual_income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    monthly_debts: float = Field(..., ge=0)
    assets: float = Field(..., ge=0)
    loan_amount: float = Field(..., gt=0)
    down_payment: float = Field(..., ge=0)
    property_value: float | None = Field(default=None, gt=0)
    credit_used: float = Field(default=0, ge=0)
    credit_limit: float = Field(default=1, gt=0)
