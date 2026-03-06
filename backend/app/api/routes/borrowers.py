from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.borrower_profile import BorrowerProfile
from app.models.financial_metric import FinancialMetric
from app.models.loan_decision import LoanDecision
from app.schemas.borrower import BorrowerProfileCreate, BorrowerProfileRead, BorrowerProfileUpdate
from app.services.underwriting_service import UnderwritingService

router = APIRouter(prefix='/borrowers', tags=['borrowers'])
underwriting_service = UnderwritingService()


@router.post('', response_model=dict)
def create_borrower_profile(payload: BorrowerProfileCreate, db: Session = Depends(get_db)) -> dict:
    property_value = payload.property_value or (payload.loan_amount + payload.down_payment)

    profile = BorrowerProfile(
        user_id=payload.user_id,
        annual_income=payload.annual_income,
        credit_score=payload.credit_score,
        monthly_debts=payload.monthly_debts,
        assets=payload.assets,
        loan_amount=payload.loan_amount,
        down_payment=payload.down_payment,
        property_value=property_value,
        credit_used=payload.credit_used,
        credit_limit=payload.credit_limit,
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    metrics = underwriting_service.compute_and_store_metrics(db, profile)

    return {
        'borrower_profile': BorrowerProfileRead.model_validate(profile),
        'metrics': {
            'dti': metrics.dti,
            'ltv': metrics.ltv,
            'credit_utilization': metrics.credit_utilization,
            'risk_score': metrics.risk_score,
            'risk_band': metrics.risk_band,
        },
    }


@router.put('/{borrower_profile_id}', response_model=dict)
def update_borrower_profile(
    borrower_profile_id: int,
    payload: BorrowerProfileUpdate,
    db: Session = Depends(get_db),
) -> dict:
    profile = db.get(BorrowerProfile, borrower_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Borrower profile not found')

    property_value = payload.property_value or (payload.loan_amount + payload.down_payment)

    profile.annual_income = payload.annual_income
    profile.credit_score = payload.credit_score
    profile.monthly_debts = payload.monthly_debts
    profile.assets = payload.assets
    profile.loan_amount = payload.loan_amount
    profile.down_payment = payload.down_payment
    profile.property_value = property_value
    profile.credit_used = payload.credit_used
    profile.credit_limit = payload.credit_limit

    db.add(profile)
    db.commit()
    db.refresh(profile)

    metrics = underwriting_service.compute_and_store_metrics(db, profile)
    return {
        'borrower_profile': BorrowerProfileRead.model_validate(profile),
        'metrics': {
            'dti': metrics.dti,
            'ltv': metrics.ltv,
            'credit_utilization': metrics.credit_utilization,
            'risk_score': metrics.risk_score,
            'risk_band': metrics.risk_band,
        },
    }


@router.get('/{borrower_profile_id}', response_model=dict)
def get_borrower_snapshot(borrower_profile_id: int, db: Session = Depends(get_db)) -> dict:
    profile = db.get(BorrowerProfile, borrower_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Borrower profile not found')

    latest_metrics = (
        db.execute(
            select(FinancialMetric)
            .where(FinancialMetric.borrower_profile_id == borrower_profile_id)
            .order_by(desc(FinancialMetric.created_at))
            .limit(1)
        )
        .scalars()
        .first()
    )
    latest_decision = (
        db.execute(
            select(LoanDecision)
            .where(LoanDecision.borrower_profile_id == borrower_profile_id)
            .order_by(desc(LoanDecision.created_at))
            .limit(1)
        )
        .scalars()
        .first()
    )

    return {
        'borrower_profile': BorrowerProfileRead.model_validate(profile),
        'latest_metrics': {
            'dti': latest_metrics.dti,
            'ltv': latest_metrics.ltv,
            'credit_utilization': latest_metrics.credit_utilization,
            'risk_score': latest_metrics.risk_score,
            'risk_band': latest_metrics.risk_band,
        }
        if latest_metrics
        else None,
        'latest_decision': {
            'decision': latest_decision.decision,
            'risk_category': latest_decision.risk_category,
            'approval_probability': latest_decision.approval_probability,
            'explanation': latest_decision.explanation,
            'reasoning_json': latest_decision.reasoning_json,
        }
        if latest_decision
        else None,
    }
