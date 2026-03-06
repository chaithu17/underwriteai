from app.services.risk_engine import calculate_credit_utilization, calculate_dti, calculate_ltv, compute_risk_metrics


def test_calculate_dti() -> None:
    assert calculate_dti(2000, 120000) == 0.2


def test_calculate_ltv() -> None:
    assert calculate_ltv(300000, 400000) == 0.75


def test_calculate_credit_utilization() -> None:
    assert calculate_credit_utilization(3000, 10000) == 0.3


def test_compute_risk_metrics_band() -> None:
    metrics = compute_risk_metrics(
        annual_income=180000,
        monthly_debts=1500,
        loan_amount=250000,
        property_value=400000,
        credit_used=1000,
        credit_limit=10000,
        credit_score=780,
    )
    assert metrics.risk_band == 'LOW'
    assert metrics.risk_score < 30


def test_compute_risk_metrics_band_high_risk_case() -> None:
    metrics = compute_risk_metrics(
        annual_income=85000,
        monthly_debts=4200,
        loan_amount=380000,
        property_value=390000,
        credit_used=18000,
        credit_limit=20000,
        credit_score=610,
    )
    assert metrics.risk_band == 'HIGH'
    assert metrics.risk_score >= 60


def test_compute_risk_metrics_handles_zero_credit_limit() -> None:
    metrics = compute_risk_metrics(
        annual_income=120000,
        monthly_debts=2000,
        loan_amount=260000,
        property_value=360000,
        credit_used=2000,
        credit_limit=0,
        credit_score=700,
    )
    assert metrics.credit_utilization == 1
