from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FinancialMetric(Base):
    __tablename__ = 'financial_metrics'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    borrower_profile_id: Mapped[int] = mapped_column(ForeignKey('borrower_profiles.id'), nullable=False, index=True)

    dti: Mapped[float] = mapped_column(Float, nullable=False)
    ltv: Mapped[float] = mapped_column(Float, nullable=False)
    credit_utilization: Mapped[float] = mapped_column(Float, nullable=False)

    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_band: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    borrower_profile = relationship('BorrowerProfile', back_populates='financial_metrics')
    loan_decisions = relationship('LoanDecision', back_populates='financial_metric')
