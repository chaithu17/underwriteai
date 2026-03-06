# Testing and Verification Guide

## Automated Backend Tests

Run backend tests in an environment with dependencies installed:

```bash
cd backend
pytest -q
```

Key files:

- `tests/test_risk_engine.py`
- `tests/test_orchestrator_fallback.py`
- `tests/test_document_intelligence.py`
- `tests/test_report_generation.py`
- `tests/test_pipeline_api.py`

## Manual Pipeline Verification (UI)

1. Create borrower profile from dashboard.
2. Edit borrower input values and click **Save Borrower Changes**.
3. Run underwriting and verify decision/probability updates.
4. Upload a document (W-2 or statement) and verify extracted JSON appears in **Documents Processed**.
5. Run underwriting again and verify explanation/conditions are updated.
6. Open **Scenario Simulator**, change at least one field, run simulation, and confirm projected probability differs from baseline.
7. Export PDF report and verify borrower profile, metrics, decision, and explanation are present.

## Regression Checklist

- Changing borrower profile inputs should change stored profile and metrics.
- Underwriting should not silently reuse stale values after form edits.
- Scenario simulator should require at least one changed field.
- `approval_probability` should vary across materially different borrower cases.
- Report endpoint should return valid PDF bytes.
