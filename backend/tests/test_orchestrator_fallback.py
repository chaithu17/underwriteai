import os

os.environ['LLM_PROVIDER'] = 'disabled'

from app.agents.orchestrator import UnderwritingAgentOrchestrator
from app.core.config import get_settings


def test_rule_based_decision_varies_with_profile_strength() -> None:
    get_settings.cache_clear()
    orchestrator = UnderwritingAgentOrchestrator()

    metrics = {
        'dti': 0.38,
        'ltv': 0.82,
        'credit_utilization': 0.29,
        'risk_score': 37.0,
        'risk_band': 'MODERATE',
    }

    strong_profile = {
        'annual_income': 165000,
        'credit_score': 785,
        'monthly_debts': 3000,
        'assets': 120000,
        'loan_amount': 310000,
    }
    weak_profile = {
        'annual_income': 95000,
        'credit_score': 620,
        'monthly_debts': 3800,
        'assets': 12000,
        'loan_amount': 360000,
    }

    strong_result = orchestrator.run(profile=strong_profile, metrics=metrics, documents=[], rag_context=[])
    weak_result = orchestrator.run(profile=weak_profile, metrics=metrics, documents=[], rag_context=[])

    assert strong_result.approval_probability > weak_result.approval_probability
    assert strong_result.decision != weak_result.decision


def test_rule_based_decision_penalizes_income_mismatch() -> None:
    get_settings.cache_clear()
    orchestrator = UnderwritingAgentOrchestrator()

    profile = {
        'annual_income': 100000,
        'credit_score': 740,
        'monthly_debts': 2200,
        'assets': 60000,
        'loan_amount': 280000,
    }
    metrics = {
        'dti': 0.30,
        'ltv': 0.78,
        'credit_utilization': 0.18,
        'risk_score': 24.0,
        'risk_band': 'LOW',
    }

    matched_docs = [{'extracted_json': {'annual_income': 101000}}]
    mismatch_docs = [{'extracted_json': {'annual_income': 62000}}]

    matched_result = orchestrator.run(profile=profile, metrics=metrics, documents=matched_docs, rag_context=[])
    mismatch_result = orchestrator.run(profile=profile, metrics=metrics, documents=mismatch_docs, rag_context=[])

    assert mismatch_result.approval_probability < matched_result.approval_probability
    assert any('income' in risk.lower() for risk in mismatch_result.key_risks)
