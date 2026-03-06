from dataclasses import dataclass


@dataclass
class RiskMetrics:
    dti: float
    ltv: float
    credit_utilization: float
    risk_score: float
    risk_band: str


def calculate_dti(total_monthly_debt: float, annual_income: float) -> float:
    monthly_income = annual_income / 12
    if monthly_income <= 0:
        return 1.0
    return total_monthly_debt / monthly_income


def calculate_ltv(loan_amount: float, property_value: float) -> float:
    if property_value <= 0:
        return 1.0
    return loan_amount / property_value


def calculate_credit_utilization(credit_used: float, credit_limit: float) -> float:
    if credit_limit <= 0:
        return 1.0
    return credit_used / credit_limit


def calculate_risk_score(dti: float, ltv: float, credit_utilization: float, credit_score: int) -> tuple[float, str]:
    dti_component = min(max(dti, 0) / 0.50, 1) * 40
    ltv_component = min(max(ltv, 0) / 0.95, 1) * 35
    utilization_component = min(max(credit_utilization, 0) / 0.80, 1) * 15

    bounded_credit_score = min(max(credit_score, 300), 850)
    credit_component = ((850 - bounded_credit_score) / 550) * 10

    risk_score = round(dti_component + ltv_component + utilization_component + credit_component, 2)

    if risk_score < 30:
        risk_band = 'LOW'
    elif risk_score < 60:
        risk_band = 'MODERATE'
    else:
        risk_band = 'HIGH'

    return risk_score, risk_band


def compute_risk_metrics(
    *,
    annual_income: float,
    monthly_debts: float,
    loan_amount: float,
    property_value: float,
    credit_used: float,
    credit_limit: float,
    credit_score: int,
) -> RiskMetrics:
    dti = round(calculate_dti(monthly_debts, annual_income), 4)
    ltv = round(calculate_ltv(loan_amount, property_value), 4)
    credit_utilization = round(calculate_credit_utilization(credit_used, credit_limit), 4)
    risk_score, risk_band = calculate_risk_score(dti, ltv, credit_utilization, credit_score)

    return RiskMetrics(
        dti=dti,
        ltv=ltv,
        credit_utilization=credit_utilization,
        risk_score=risk_score,
        risk_band=risk_band,
    )
