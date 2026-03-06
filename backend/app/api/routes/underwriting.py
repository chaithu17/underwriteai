from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.borrower_profile import BorrowerProfile
from app.schemas.underwriting import UnderwritingEvaluationRequest, UnderwritingEvaluationResponse
from app.services.underwriting_service import UnderwritingService

router = APIRouter(prefix='/underwriting', tags=['underwriting'])
underwriting_service = UnderwritingService()


@router.post('/evaluate', response_model=UnderwritingEvaluationResponse)
def evaluate_underwriting(
    payload: UnderwritingEvaluationRequest,
    db: Session = Depends(get_db),
) -> UnderwritingEvaluationResponse:
    borrower = db.get(BorrowerProfile, payload.borrower_profile_id)
    if not borrower:
        raise HTTPException(status_code=404, detail='Borrower profile not found')

    metrics = underwriting_service.compute_and_store_metrics(db, borrower)
    decision = underwriting_service.evaluate_and_store_decision(
        db=db,
        borrower_profile=borrower,
        financial_metric=metrics,
    )

    return UnderwritingEvaluationResponse(metrics=metrics, decision=decision)
