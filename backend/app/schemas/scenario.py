from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.underwriting import UnderwritingDecisionOutput


class ScenarioOverride(BaseModel):
    annual_income: float | None = Field(default=None, gt=0)
    monthly_debts: float | None = Field(default=None, ge=0)
    loan_amount: float | None = Field(default=None, gt=0)
    down_payment: float | None = Field(default=None, ge=0)


class ScenarioSimulationRequest(BaseModel):
    borrower_profile_id: int
    scenario_name: str = Field(min_length=2, max_length=120)
    overrides: ScenarioOverride


class ScenarioSimulationRead(BaseModel):
    id: int
    borrower_profile_id: int
    scenario_name: str
    input_json: dict
    output_json: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScenarioSimulationResponse(BaseModel):
    scenario: ScenarioSimulationRead
    projected_decision: UnderwritingDecisionOutput
