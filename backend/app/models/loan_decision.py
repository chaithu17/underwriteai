from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LoanDecision(Base):
    __tablename__ = 'loan_decisions'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    borrower_profile_id: Mapped[int] = mapped_column(ForeignKey('borrower_profiles.id'), nullable=False, index=True)
    financial_metrics_id: Mapped[int] = mapped_column(ForeignKey('financial_metrics.id'), nullable=False)

    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    risk_category: Mapped[str] = mapped_column(String(50), nullable=False)
    approval_probability: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    borrower_profile = relationship('BorrowerProfile', back_populates='loan_decisions')
    financial_metric = relationship('FinancialMetric', back_populates='loan_decisions')
