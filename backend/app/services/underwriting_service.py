from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.agents.orchestrator import UnderwritingAgentOrchestrator
from app.models.borrower_profile import BorrowerProfile
from app.models.document import Document
from app.models.financial_metric import FinancialMetric
from app.models.loan_decision import LoanDecision
from app.rag.vector_store import VectorStoreService
from app.schemas.underwriting import UnderwritingDecisionOutput
from app.services.risk_engine import compute_risk_metrics


class UnderwritingService:
    def __init__(self) -> None:
        self.agent_orchestrator = UnderwritingAgentOrchestrator()
        self.vector_store = VectorStoreService()

    def compute_and_store_metrics(self, db: Session, borrower_profile: BorrowerProfile) -> FinancialMetric:
        metrics = compute_risk_metrics(
            annual_income=borrower_profile.annual_income,
            monthly_debts=borrower_profile.monthly_debts,
            loan_amount=borrower_profile.loan_amount,
            property_value=borrower_profile.property_value,
            credit_used=borrower_profile.credit_used,
            credit_limit=borrower_profile.credit_limit,
            credit_score=borrower_profile.credit_score,
        )

        metric_row = FinancialMetric(
            borrower_profile_id=borrower_profile.id,
            dti=metrics.dti,
            ltv=metrics.ltv,
            credit_utilization=metrics.credit_utilization,
            risk_score=metrics.risk_score,
            risk_band=metrics.risk_band,
        )

        db.add(metric_row)
        db.commit()
        db.refresh(metric_row)

        self.vector_store.upsert_text(
            text=(
                f"Financial metrics for borrower {borrower_profile.id}: "
                f"DTI {metric_row.dti:.2f}, LTV {metric_row.ltv:.2f}, "
                f"credit utilization {metric_row.credit_utilization:.2f}, "
                f"risk score {metric_row.risk_score:.2f}, risk band {metric_row.risk_band}."
            ),
            metadata={
                'entity': 'financial_metric',
                'borrower_profile_id': borrower_profile.id,
                'financial_metric_id': metric_row.id,
            },
        )
        return metric_row

    def evaluate_and_store_decision(
        self,
        *,
        db: Session,
        borrower_profile: BorrowerProfile,
        financial_metric: FinancialMetric,
    ) -> LoanDecision:
        docs = (
            db.execute(
                select(Document)
                .where(Document.borrower_profile_id == borrower_profile.id)
                .order_by(desc(Document.created_at))
                .limit(10)
            )
            .scalars()
            .all()
        )

        profile_payload = {
            'annual_income': borrower_profile.annual_income,
            'credit_score': borrower_profile.credit_score,
            'monthly_debts': borrower_profile.monthly_debts,
            'assets': borrower_profile.assets,
            'loan_amount': borrower_profile.loan_amount,
            'down_payment': borrower_profile.down_payment,
            'property_value': borrower_profile.property_value,
            'credit_used': borrower_profile.credit_used,
            'credit_limit': borrower_profile.credit_limit,
        }
        metrics_payload = {
            'dti': financial_metric.dti,
            'ltv': financial_metric.ltv,
            'credit_utilization': financial_metric.credit_utilization,
            'risk_score': financial_metric.risk_score,
            'risk_band': financial_metric.risk_band,
        }
        doc_payloads = [
            {
                'filename': d.filename,
                'document_type': d.document_type,
                'raw_text': d.raw_text[:3000],
                'extracted_json': d.extracted_json,
            }
            for d in docs
        ]

        rag_query = (
            f"Borrower with credit score {borrower_profile.credit_score}, DTI {financial_metric.dti:.2f}, "
            f"LTV {financial_metric.ltv:.2f}: retrieve related underwriting context"
        )
        rag_context = self.vector_store.retrieve(rag_query)

        decision_output: UnderwritingDecisionOutput = self.agent_orchestrator.run(
            profile=profile_payload,
            metrics=metrics_payload,
            documents=doc_payloads,
            rag_context=rag_context,
        )

        reasoning_json = decision_output.model_dump()

        decision_row = LoanDecision(
            borrower_profile_id=borrower_profile.id,
            financial_metrics_id=financial_metric.id,
            decision=decision_output.decision.value,
            risk_category=decision_output.risk_category.value,
            approval_probability=decision_output.approval_probability,
            explanation=decision_output.explanation,
            reasoning_json=reasoning_json,
        )

        db.add(decision_row)
        db.commit()
        db.refresh(decision_row)

        self.vector_store.upsert_text(
            text=(
                f"Decision {decision_row.decision}; risk {decision_row.risk_category}; "
                f"explanation {decision_row.explanation}"
            ),
            metadata={
                'entity': 'loan_decision',
                'borrower_profile_id': borrower_profile.id,
                'loan_decision_id': decision_row.id,
            },
        )

        return decision_row
