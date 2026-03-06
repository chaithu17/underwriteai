import { BorrowerInput } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

async function throwApiError(response: Response, fallbackMessage: string): Promise<never> {
  let detail: string | null = null;
  try {
    const payload = await response.json();
    detail =
      typeof payload?.detail === 'string'
        ? payload.detail
        : Array.isArray(payload?.detail)
          ? payload.detail.map((item: { msg?: string }) => item.msg).filter(Boolean).join(', ')
          : null;
  } catch {
    detail = null;
  }
  throw new Error(detail || fallbackMessage);
}

export async function createBorrowerProfile(payload: BorrowerInput) {
  const response = await fetch(`${API_BASE}/borrowers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return throwApiError(response, 'Failed to create borrower profile');
  }

  return response.json();
}

export async function updateBorrowerProfile(borrowerProfileId: number, payload: BorrowerInput) {
  const response = await fetch(`${API_BASE}/borrowers/${borrowerProfileId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return throwApiError(response, 'Failed to update borrower profile');
  }

  return response.json();
}

export async function uploadDocument(params: {
  borrowerProfileId: number;
  documentType: string;
  file: File;
}) {
  const formData = new FormData();
  formData.append('borrower_profile_id', String(params.borrowerProfileId));
  formData.append('document_type', params.documentType);
  formData.append('file', params.file);

  const response = await fetch(`${API_BASE}/documents/upload`, {
    method: 'POST',
    body: formData
  });

  if (!response.ok) {
    return throwApiError(response, 'Failed to upload document');
  }

  return response.json();
}

export async function evaluateUnderwriting(borrowerProfileId: number) {
  const response = await fetch(`${API_BASE}/underwriting/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ borrower_profile_id: borrowerProfileId })
  });

  if (!response.ok) {
    return throwApiError(response, 'Failed to evaluate underwriting');
  }

  return response.json();
}

export async function simulateScenario(payload: {
  borrower_profile_id: number;
  scenario_name: string;
  overrides: {
    annual_income?: number;
    monthly_debts?: number;
    loan_amount?: number;
    down_payment?: number;
  };
}) {
  const response = await fetch(`${API_BASE}/scenarios/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    return throwApiError(response, 'Failed to simulate scenario');
  }

  return response.json();
}

export function getReportDownloadUrl(decisionId: number) {
  return `${API_BASE}/reports/${decisionId}/pdf`;
}
