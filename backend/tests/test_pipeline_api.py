from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / 'underwrite_test.db'
    uploads_dir = tmp_path / 'uploads'
    chroma_dir = tmp_path / 'chroma_db'

    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db_path}')
    monkeypatch.setenv('CREATE_TABLES_ON_STARTUP', 'true')
    monkeypatch.setenv('LLM_PROVIDER', 'disabled')
    monkeypatch.setenv('ENABLE_VECTOR_STORE', 'false')
    monkeypatch.setenv('UPLOADS_DIR', str(uploads_dir))
    monkeypatch.setenv('VECTOR_DB_PATH', str(chroma_dir))

    for mod in list(sys.modules):
        if mod == 'app' or mod.startswith('app.'):
            del sys.modules[mod]

    main_module = importlib.import_module('app.main')
    docs_route = importlib.import_module('app.api.routes.documents')
    schema_module = importlib.import_module('app.schemas.document')

    monkeypatch.setattr(
        docs_route.processing_service,
        'extract_text',
        lambda _path: 'Employer: Acme Corp\nAnnual Income: 95,000\nBank Balance: 28,000',
    )
    monkeypatch.setattr(
        docs_route.processing_service,
        'extract_structured_data',
        lambda _raw: schema_module.DocumentFinancialData(
            employer='Acme Corp',
            annual_income=95000,
            bank_balance=28000,
            pay_frequency='bi-weekly',
            detected_debts=1200,
        ),
    )

    with TestClient(main_module.app) as test_client:
        yield test_client


def test_pipeline_create_update_document_evaluate_simulate_report(client: TestClient) -> None:
    borrower_payload = {
        'annual_income': 95000,
        'credit_score': 720,
        'monthly_debts': 2800,
        'assets': 45000,
        'loan_amount': 340000,
        'down_payment': 60000,
        'credit_used': 2500,
        'credit_limit': 10000,
    }

    create_resp = client.post('/api/v1/borrowers', json=borrower_payload)
    assert create_resp.status_code == 200
    create_data = create_resp.json()
    borrower_id = create_data['borrower_profile']['id']
    assert borrower_id > 0

    eval_initial_resp = client.post('/api/v1/underwriting/evaluate', json={'borrower_profile_id': borrower_id})
    assert eval_initial_resp.status_code == 200
    eval_initial = eval_initial_resp.json()
    initial_probability = eval_initial['decision']['approval_probability']

    update_payload = {
        'annual_income': 95000,
        'credit_score': 720,
        'monthly_debts': 4200,
        'assets': 45000,
        'loan_amount': 340000,
        'down_payment': 60000,
        'credit_used': 6000,
        'credit_limit': 10000,
    }
    update_resp = client.put(f'/api/v1/borrowers/{borrower_id}', json=update_payload)
    assert update_resp.status_code == 200

    upload_resp = client.post(
        '/api/v1/documents/upload',
        data={'borrower_profile_id': str(borrower_id), 'document_type': 'W2'},
        files={'file': ('w2.pdf', b'%PDF-1.4 test', 'application/pdf')},
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data['extracted_data']['employer'] == 'Acme Corp'

    eval_updated_resp = client.post('/api/v1/underwriting/evaluate', json={'borrower_profile_id': borrower_id})
    assert eval_updated_resp.status_code == 200
    eval_updated = eval_updated_resp.json()
    updated_probability = eval_updated['decision']['approval_probability']
    updated_decision_id = eval_updated['decision']['id']

    assert updated_probability != initial_probability

    scenario_resp = client.post(
        '/api/v1/scenarios/simulate',
        json={
            'borrower_profile_id': borrower_id,
            'scenario_name': 'Higher income + lower debt + higher down payment',
            'overrides': {
                'annual_income': 150000,
                'monthly_debts': 2200,
                'loan_amount': 300000,
                'down_payment': 120000,
            },
        },
    )
    assert scenario_resp.status_code == 200
    scenario_data = scenario_resp.json()

    scenario_probability = scenario_data['projected_decision']['approval_probability']
    assert scenario_probability > updated_probability

    report_resp = client.get(f'/api/v1/reports/{updated_decision_id}/pdf')
    assert report_resp.status_code == 200
    assert report_resp.headers['content-type'].startswith('application/pdf')
    assert report_resp.content.startswith(b'%PDF')
