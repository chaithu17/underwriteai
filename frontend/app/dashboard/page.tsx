'use client';

import { useMemo, useState } from 'react';
import { Download, Play } from 'lucide-react';

import { ThemeToggle } from '@/components/layout/theme-toggle';
import { ApprovalChart } from '@/components/charts/approval-chart';
import { RatiosChart } from '@/components/charts/ratios-chart';
import { ScenarioChart } from '@/components/charts/scenario-chart';
import { BorrowerForm, BorrowerFormData } from '@/components/underwriting/borrower-form';
import { DecisionPanel } from '@/components/underwriting/decision-panel';
import { DocumentUpload } from '@/components/underwriting/document-upload';
import { ScenarioSimulator } from '@/components/underwriting/scenario-simulator';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  createBorrowerProfile,
  evaluateUnderwriting,
  getReportDownloadUrl,
  simulateScenario,
  updateBorrowerProfile,
  uploadDocument
} from '@/lib/api';
import { Metrics, ScenarioOutput, UnderwritingDecision } from '@/lib/types';

const initialForm: BorrowerFormData = {
  annual_income: 95000,
  credit_score: 720,
  monthly_debts: 2800,
  assets: 45000,
  loan_amount: 340000,
  down_payment: 60000,
  credit_used: 2500,
  credit_limit: 10000
};

export default function DashboardPage() {
  const [form, setForm] = useState<BorrowerFormData>(initialForm);
  const [savedBorrower, setSavedBorrower] = useState<BorrowerFormData | null>(null);
  const [borrowerId, setBorrowerId] = useState<number | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [decision, setDecision] = useState<UnderwritingDecision | null>(null);
  const [scenario, setScenario] = useState<ScenarioOutput | null>(null);
  const [uploadedDocs, setUploadedDocs] = useState<Array<{ filename: string; type: string; extracted: Record<string, unknown> }>>(
    []
  );
  const [isCreating, setIsCreating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [lastEvaluationAt, setLastEvaluationAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const previewMetrics = useMemo(() => {
    return computeMetrics(form);
  }, [form]);

  const hasUnsavedChanges = useMemo(() => {
    if (!savedBorrower) {
      return false;
    }
    return !isBorrowerEqual(form, savedBorrower);
  }, [form, savedBorrower]);

  const onCreateBorrower = async () => {
    setError(null);
    setIsCreating(true);
    try {
      const result = await createBorrowerProfile(form);
      setBorrowerId(result.borrower_profile.id);
      setMetrics(result.metrics);
      setSavedBorrower({ ...form });
      setDecision(null);
      setScenario(null);
      setLastEvaluationAt(null);
      setUploadedDocs([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create borrower profile.');
    } finally {
      setIsCreating(false);
    }
  };

  const persistBorrowerChanges = async () => {
    if (!borrowerId || !hasUnsavedChanges) {
      return;
    }

    setIsSaving(true);
    try {
      const result = await updateBorrowerProfile(borrowerId, form);
      setMetrics(result.metrics);
      setSavedBorrower({ ...form });
      setDecision(null);
      setScenario(null);
      setLastEvaluationAt(null);
    } finally {
      setIsSaving(false);
    }
  };

  const onUploadDocument = async ({ documentType, file }: { documentType: string; file: File }) => {
    if (!borrowerId) {
      return;
    }

    setError(null);
    try {
      const result = await uploadDocument({ borrowerProfileId: borrowerId, documentType, file });
      setUploadedDocs((prev) => [
        ...prev,
        {
          filename: result.document.filename,
          type: result.document.document_type,
          extracted: result.extracted_data
        }
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to upload document.');
    }
  };

  const onEvaluate = async () => {
    if (!borrowerId) {
      setError('Create a borrower profile first.');
      return;
    }

    setError(null);
    setIsEvaluating(true);
    try {
      if (hasUnsavedChanges) {
        await persistBorrowerChanges();
      }
      const result = await evaluateUnderwriting(borrowerId);
      setMetrics(result.metrics);
      setDecision(result.decision);
      setLastEvaluationAt(new Date().toLocaleString());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Underwriting evaluation failed.');
    } finally {
      setIsEvaluating(false);
    }
  };

  const onSimulate = async ({
    scenarioName,
    overrides
  }: {
    scenarioName: string;
    overrides: Partial<{ annual_income: number; monthly_debts: number; loan_amount: number; down_payment: number }>;
  }) => {
    if (!borrowerId) {
      setError('Create a borrower profile before running scenarios.');
      return;
    }

    setError(null);
    try {
      if (hasUnsavedChanges) {
        await persistBorrowerChanges();
      }
      const result = await simulateScenario({
        borrower_profile_id: borrowerId,
        scenario_name: scenarioName,
        overrides
      });

      setScenario({
        metrics: result.scenario.output_json.metrics,
        decision: result.projected_decision
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scenario simulation failed.');
    }
  };

  return (
    <main className='min-h-screen bg-grid px-4 py-8 md:px-8'>
      <div className='mx-auto flex w-full max-w-7xl flex-col gap-6'>
        <header className='flex flex-wrap items-center justify-between gap-3'>
          <div>
            <p className='font-mono text-xs uppercase tracking-[0.25em] text-muted-foreground'>Fintech AI Platform</p>
            <h1 className='font-heading text-3xl font-semibold md:text-4xl'>UnderwriteAI Dashboard</h1>
          </div>
          <div className='flex items-center gap-2'>
            <ThemeToggle />
            <Badge>Next.js + FastAPI + LangChain</Badge>
          </div>
        </header>

        {error && (
          <Card className='border-rose-500/50'>
            <CardContent className='p-4 text-sm text-rose-600 dark:text-rose-300'>{error}</CardContent>
          </Card>
        )}

        <section className='grid gap-6 xl:grid-cols-[1.3fr_1fr]'>
          <BorrowerForm
            values={form}
            previewMetrics={previewMetrics}
            submitting={isCreating}
            onChange={(name, value) => setForm((prev) => ({ ...prev, [name]: value }))}
            onSubmit={onCreateBorrower}
          />

          <div className='space-y-6'>
            <DocumentUpload borrowerProfileId={borrowerId} onUpload={onUploadDocument} />

            <Card>
              <CardHeader>
                <CardTitle>Actions</CardTitle>
              </CardHeader>
              <CardContent className='flex flex-wrap gap-3'>
                <Button onClick={onEvaluate} disabled={!borrowerId || isEvaluating || isSaving}>
                  <Play className='mr-2 h-4 w-4' />
                  {isEvaluating ? 'Evaluating...' : 'Run Underwriting Agent'}
                </Button>
                <Button variant='outline' onClick={persistBorrowerChanges} disabled={!borrowerId || !hasUnsavedChanges || isSaving}>
                  {isSaving ? 'Saving...' : 'Save Borrower Changes'}
                </Button>
                {decision?.id && (
                  <a href={getReportDownloadUrl(decision.id)} target='_blank' rel='noreferrer'>
                    <Button variant='outline'>
                      <Download className='mr-2 h-4 w-4' />
                      Export PDF Report
                    </Button>
                  </a>
                )}
                {hasUnsavedChanges && (
                  <p className='w-full text-xs text-amber-600 dark:text-amber-300'>
                    Unsaved borrower edits detected. Underwriting will auto-save these values.
                  </p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Pipeline Status</CardTitle>
              </CardHeader>
              <CardContent className='space-y-2 text-sm'>
                <p>{borrowerId ? '1. Borrower profile saved' : '1. Borrower profile pending'}</p>
                <p>{uploadedDocs.length > 0 ? `2. Documents processed (${uploadedDocs.length})` : '2. Document upload pending'}</p>
                <p>{decision ? '3. Underwriting decision generated' : '3. Decision pending'}</p>
                <p>{scenario ? '4. Scenario simulation completed' : '4. Scenario simulation pending'}</p>
                {lastEvaluationAt && <p className='text-xs text-muted-foreground'>Last underwriting run: {lastEvaluationAt}</p>}
              </CardContent>
            </Card>
          </div>
        </section>

        <section className='grid gap-4 sm:grid-cols-2 lg:grid-cols-4'>
          <MetricCard label='Credit Score' value={form.credit_score.toString()} />
          <MetricCard label='Debt-To-Income' value={`${((metrics?.dti ?? previewMetrics.dti) * 100).toFixed(2)}%`} />
          <MetricCard label='Loan-To-Value' value={`${((metrics?.ltv ?? previewMetrics.ltv) * 100).toFixed(2)}%`} />
          <MetricCard label='Risk Score' value={(metrics?.risk_score ?? previewMetrics.risk_score).toFixed(2)} />
        </section>

        <section className='grid gap-6 xl:grid-cols-2'>
          <Card>
            <CardHeader>
              <CardTitle>Financial Ratios</CardTitle>
            </CardHeader>
            <CardContent>
              <RatiosChart metrics={metrics} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Approval Probability</CardTitle>
            </CardHeader>
            <CardContent>
              <ApprovalChart probability={decision?.approval_probability ?? null} />
            </CardContent>
          </Card>
        </section>

        <section className='grid gap-6 xl:grid-cols-[1.2fr_1fr]'>
          <DecisionPanel decision={decision} />

          <Card>
            <CardHeader>
              <CardTitle>Documents Processed</CardTitle>
            </CardHeader>
            <CardContent>
              {uploadedDocs.length === 0 ? (
                <p className='text-sm text-muted-foreground'>No documents uploaded yet.</p>
              ) : (
                <ul className='space-y-3 text-sm'>
                  {uploadedDocs.map((doc, idx) => (
                    <li key={`${doc.filename}-${idx}`} className='rounded-lg border border-border/60 bg-muted/20 p-3'>
                      <p className='font-medium'>
                        {doc.filename} <span className='text-muted-foreground'>({doc.type})</span>
                      </p>
                      <p className='mt-1 font-mono text-xs text-muted-foreground'>{JSON.stringify(doc.extracted)}</p>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </section>

        <section className='grid gap-6 xl:grid-cols-2'>
          <ScenarioSimulator disabled={!borrowerId || isSaving} initial={savedBorrower ?? form} onSimulate={onSimulate} />
          <Card>
            <CardHeader>
              <CardTitle>Scenario Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <ScenarioChart baseline={metrics} scenario={scenario} />
              {scenario && (
                <div className='mt-4 rounded-lg border border-border/60 bg-muted/20 p-4 text-sm'>
                  <p className='font-semibold'>Projected Decision: {scenario.decision.decision}</p>
                  <p className='mt-1 text-muted-foreground'>{scenario.decision.explanation}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <Card>
      <CardContent className='p-4'>
        <p className='text-xs uppercase tracking-wide text-muted-foreground'>{label}</p>
        <p className='mt-2 font-heading text-2xl font-semibold'>{value}</p>
      </CardContent>
    </Card>
  );
}

function computeMetrics(form: BorrowerFormData): Metrics {
  const monthlyIncome = form.annual_income / 12;
  const propertyValue = form.loan_amount + form.down_payment;

  const dti = monthlyIncome > 0 ? form.monthly_debts / monthlyIncome : 1;
  const ltv = propertyValue > 0 ? form.loan_amount / propertyValue : 1;
  const creditUtilization = form.credit_limit > 0 ? form.credit_used / form.credit_limit : 1;

  const dtiRisk = Math.min(dti / 0.5, 1) * 40;
  const ltvRisk = Math.min(ltv / 0.95, 1) * 35;
  const utilizationRisk = Math.min(creditUtilization / 0.8, 1) * 15;
  const creditRisk = ((850 - Math.max(300, Math.min(form.credit_score, 850))) / 550) * 10;

  return {
    dti,
    ltv,
    credit_utilization: creditUtilization,
    risk_score: Number((dtiRisk + ltvRisk + utilizationRisk + creditRisk).toFixed(2)),
    risk_band: dti <= 0.36 && ltv <= 0.8 ? 'LOW' : dti <= 0.45 ? 'MODERATE' : 'HIGH'
  };
}

function isBorrowerEqual(a: BorrowerFormData, b: BorrowerFormData): boolean {
  return (
    a.annual_income === b.annual_income &&
    a.credit_score === b.credit_score &&
    a.monthly_debts === b.monthly_debts &&
    a.assets === b.assets &&
    a.loan_amount === b.loan_amount &&
    a.down_payment === b.down_payment &&
    a.credit_used === b.credit_used &&
    a.credit_limit === b.credit_limit
  );
}
