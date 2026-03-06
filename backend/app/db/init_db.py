from app.db.base import Base
from app.db.session import engine
from app.models import borrower_profile, document, financial_metric, loan_decision, simulation_scenario, user  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
