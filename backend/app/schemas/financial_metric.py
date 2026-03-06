from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FinancialMetricRead(BaseModel):
    id: int
    borrower_profile_id: int
    dti: float
    ltv: float
    credit_utilization: float
    risk_score: float
    risk_band: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
