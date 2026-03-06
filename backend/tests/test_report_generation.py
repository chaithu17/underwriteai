from app.services.report_generation import generate_underwriting_pdf


def test_generate_underwriting_pdf_returns_pdf_bytes() -> None:
    pdf = generate_underwriting_pdf(
        borrower_profile={
            'annual_income': 95000,
            'credit_score': 720,
            'monthly_debts': 2800,
            'assets': 45000,
            'loan_amount': 340000,
            'down_payment': 60000,
        },
        metrics={
            'dti': 0.35,
            'ltv': 0.85,
            'credit_utilization': 0.25,
            'risk_score': 41.7,
            'risk_band': 'MODERATE',
        },
        decision={
            'decision': 'CONDITIONALLY_APPROVED',
            'risk_category': 'MODERATE',
            'approval_probability': 0.63,
            'explanation': 'Conditional approval with verification conditions.',
            'conditions': ['Provide updated pay stubs'],
        },
        documents=[{'filename': 'w2.pdf', 'document_type': 'W2'}],
    )

    assert isinstance(pdf, bytes)
    assert pdf.startswith(b'%PDF')
    assert len(pdf) > 500
