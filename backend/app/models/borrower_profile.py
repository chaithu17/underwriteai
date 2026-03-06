from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BorrowerProfile(Base):
    __tablename__ = 'borrower_profiles'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)

    annual_income: Mapped[float] = mapped_column(Float, nullable=False)
    credit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_debts: Mapped[float] = mapped_column(Float, nullable=False)
    assets: Mapped[float] = mapped_column(Float, nullable=False)
    loan_amount: Mapped[float] = mapped_column(Float, nullable=False)
    down_payment: Mapped[float] = mapped_column(Float, nullable=False)
    property_value: Mapped[float] = mapped_column(Float, nullable=False)
    credit_used: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    credit_limit: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship('User', back_populates='borrower_profiles')
    documents = relationship('Document', back_populates='borrower_profile', cascade='all, delete-orphan')
    financial_metrics = relationship('FinancialMetric', back_populates='borrower_profile', cascade='all, delete-orphan')
    loan_decisions = relationship('LoanDecision', back_populates='borrower_profile', cascade='all, delete-orphan')
    simulation_scenarios = relationship('SimulationScenario', back_populates='borrower_profile', cascade='all, delete-orphan')
