from app.services.document_intelligence import DocumentProcessingService


def test_regex_extraction_basic_fields() -> None:
    sample_text = (
        'Employer: Amazon Web Services\n'
        'Annual Income: $95,000\n'
        'Bank Balance: $28,500\n'
    )

    data = DocumentProcessingService._regex_extract(sample_text)

    assert data.employer == 'Amazon Web Services'
    assert data.annual_income == 95000
    assert data.bank_balance == 28500


def test_regex_extraction_handles_missing_values() -> None:
    sample_text = 'Pay Stub\nGross Pay Period Amount\n'

    data = DocumentProcessingService._regex_extract(sample_text)

    assert data.employer is None
    assert data.annual_income is None
    assert data.bank_balance is None
