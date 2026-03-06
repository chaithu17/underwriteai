from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.financial_metric import FinancialMetricRead


class DecisionEnum(str, Enum):
    approved = 'APPROVED'
    conditional = 'CONDITIONALLY_APPROVED'
    denied = 'DENIED'


class RiskCategoryEnum(str, Enum):
    low = 'LOW'
    moderate = 'MODERATE'
    high = 'HIGH'


class UnderwritingEvaluationRequest(BaseModel):
    borrower_profile_id: int


class UnderwritingDecisionOutput(BaseModel):
    decision: DecisionEnum
    risk_category: RiskCategoryEnum
    approval_probability: float = Field(..., ge=0, le=1)
    explanation: str
    key_risks: list[str] = Field(default_factory=list)
    mitigants: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)


class LoanDecisionRead(BaseModel):
    id: int
    borrower_profile_id: int
    financial_metrics_id: int
    decision: str
    risk_category: str
    approval_probability: float
    explanation: str
    reasoning_json: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnderwritingEvaluationResponse(BaseModel):
    metrics: FinancialMetricRead
    decision: LoanDecisionRead
