from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SimulationScenario(Base):
    __tablename__ = 'simulation_scenarios'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    borrower_profile_id: Mapped[int] = mapped_column(ForeignKey('borrower_profiles.id'), nullable=False, index=True)

    scenario_name: Mapped[str] = mapped_column(String(120), nullable=False)
    input_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    output_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    borrower_profile = relationship('BorrowerProfile', back_populates='simulation_scenarios')
