from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.borrower_profile import BorrowerProfile
from app.models.document import Document
from app.models.financial_metric import FinancialMetric
from app.models.loan_decision import LoanDecision
from app.services.report_generation import generate_underwriting_pdf

router = APIRouter(prefix='/reports', tags=['reports'])


@router.get('/{loan_decision_id}/pdf')
def download_underwriting_report(loan_decision_id: int, db: Session = Depends(get_db)) -> StreamingResponse:
    decision = db.get(LoanDecision, loan_decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail='Loan decision not found')

    profile = db.get(BorrowerProfile, decision.borrower_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail='Borrower profile not found')

    metrics = db.get(FinancialMetric, decision.financial_metrics_id)
    if not metrics:
        raise HTTPException(status_code=404, detail='Financial metrics not found')

    documents = (
        db.execute(select(Document).where(Document.borrower_profile_id == profile.id).order_by(Document.created_at.desc()))
        .scalars()
        .all()
    )

    reasoning = decision.reasoning_json or {}

    pdf_bytes = generate_underwriting_pdf(
        borrower_profile={
            'annual_income': profile.annual_income,
            'credit_score': profile.credit_score,
            'monthly_debts': profile.monthly_debts,
            'assets': profile.assets,
            'loan_amount': profile.loan_amount,
            'down_payment': profile.down_payment,
        },
        metrics={
            'dti': metrics.dti,
            'ltv': metrics.ltv,
            'credit_utilization': metrics.credit_utilization,
            'risk_score': metrics.risk_score,
            'risk_band': metrics.risk_band,
        },
        decision={
            'decision': decision.decision,
            'risk_category': decision.risk_category,
            'approval_probability': decision.approval_probability,
            'explanation': decision.explanation,
            'conditions': reasoning.get('conditions', []),
        },
        documents=[
            {
                'filename': doc.filename,
                'document_type': doc.document_type,
            }
            for doc in documents
        ],
    )

    file_like = BytesIO(pdf_bytes)
    headers = {'Content-Disposition': f'attachment; filename="underwriting-report-{loan_decision_id}.pdf"'}
    return StreamingResponse(file_like, media_type='application/pdf', headers=headers)
