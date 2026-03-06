from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.borrower_profile import BorrowerProfile
from app.models.simulation_scenario import SimulationScenario
from app.schemas.scenario import ScenarioSimulationRequest, ScenarioSimulationResponse
from app.services.risk_engine import compute_risk_metrics
from app.services.underwriting_service import UnderwritingService

router = APIRouter(prefix='/scenarios', tags=['scenarios'])
underwriting_service = UnderwritingService()


@router.post('/simulate', response_model=ScenarioSimulationResponse)
def simulate_scenario(payload: ScenarioSimulationRequest, db: Session = Depends(get_db)) -> ScenarioSimulationResponse:
    borrower = db.get(BorrowerProfile, payload.borrower_profile_id)
    if not borrower:
        raise HTTPException(status_code=404, detail='Borrower profile not found')

    annual_income = payload.overrides.annual_income if payload.overrides.annual_income is not None else borrower.annual_income
    monthly_debts = payload.overrides.monthly_debts if payload.overrides.monthly_debts is not None else borrower.monthly_debts
    loan_amount = payload.overrides.loan_amount if payload.overrides.loan_amount is not None else borrower.loan_amount
    down_payment = payload.overrides.down_payment if payload.overrides.down_payment is not None else borrower.down_payment
    property_value = loan_amount + down_payment

    metrics = compute_risk_metrics(
        annual_income=annual_income,
        monthly_debts=monthly_debts,
        loan_amount=loan_amount,
        property_value=property_value,
        credit_used=borrower.credit_used,
        credit_limit=borrower.credit_limit,
        credit_score=borrower.credit_score,
    )

    decision = underwriting_service.agent_orchestrator.run(
        profile={
            'annual_income': annual_income,
            'credit_score': borrower.credit_score,
            'monthly_debts': monthly_debts,
            'assets': borrower.assets,
            'loan_amount': loan_amount,
            'down_payment': down_payment,
            'property_value': property_value,
            'credit_used': borrower.credit_used,
            'credit_limit': borrower.credit_limit,
        },
        metrics={
            'dti': metrics.dti,
            'ltv': metrics.ltv,
            'credit_utilization': metrics.credit_utilization,
            'risk_score': metrics.risk_score,
            'risk_band': metrics.risk_band,
        },
        documents=[],
        rag_context=[],
    )

    scenario_row = SimulationScenario(
        borrower_profile_id=borrower.id,
        scenario_name=payload.scenario_name,
        input_json=payload.model_dump(),
        output_json={
            'metrics': {
                'dti': metrics.dti,
                'ltv': metrics.ltv,
                'credit_utilization': metrics.credit_utilization,
                'risk_score': metrics.risk_score,
                'risk_band': metrics.risk_band,
            },
            'decision': decision.model_dump(mode='json'),
        },
    )

    db.add(scenario_row)
    db.commit()
    db.refresh(scenario_row)

    return ScenarioSimulationResponse(scenario=scenario_row, projected_decision=decision)
