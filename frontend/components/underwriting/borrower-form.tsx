'use client';

import { FormEvent } from 'react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Metrics } from '@/lib/types';

export type BorrowerFormData = {
  annual_income: number;
  credit_score: number;
  monthly_debts: number;
  assets: number;
  loan_amount: number;
  down_payment: number;
  credit_used: number;
  credit_limit: number;
};

export function BorrowerForm({
  values,
  previewMetrics,
  submitting,
  onChange,
  onSubmit
}: {
  values: BorrowerFormData;
  previewMetrics: Metrics;
  submitting: boolean;
  onChange: (name: keyof BorrowerFormData, value: number) => void;
  onSubmit: () => void;
}) {
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Borrower Intake</CardTitle>
        <CardDescription>Capture applicant financial profile and monitor core metrics in real time.</CardDescription>
      </CardHeader>
      <CardContent>
        <form className='grid gap-4 md:grid-cols-2' onSubmit={handleSubmit}>
          <Field
            label='Annual Income ($)'
            value={values.annual_income}
            onChange={(value) => onChange('annual_income', value)}
          />
          <Field label='Credit Score' value={values.credit_score} onChange={(value) => onChange('credit_score', value)} />
          <Field
            label='Monthly Debts ($)'
            value={values.monthly_debts}
            onChange={(value) => onChange('monthly_debts', value)}
          />
          <Field label='Assets ($)' value={values.assets} onChange={(value) => onChange('assets', value)} />
          <Field
            label='Loan Amount Requested ($)'
            value={values.loan_amount}
            onChange={(value) => onChange('loan_amount', value)}
          />
          <Field
            label='Down Payment ($)'
            value={values.down_payment}
            onChange={(value) => onChange('down_payment', value)}
          />
          <Field
            label='Credit Used ($)'
            value={values.credit_used}
            onChange={(value) => onChange('credit_used', value)}
          />
          <Field
            label='Credit Limit ($)'
            value={values.credit_limit}
            onChange={(value) => onChange('credit_limit', value)}
          />

          <div className='col-span-full rounded-lg border border-border/60 bg-muted/30 p-4 text-sm'>
            <p className='font-medium'>Real-Time Metrics</p>
            <div className='mt-2 grid gap-2 sm:grid-cols-3'>
              <p>DTI: {(previewMetrics.dti * 100).toFixed(2)}%</p>
              <p>LTV: {(previewMetrics.ltv * 100).toFixed(2)}%</p>
              <p>Credit Utilization: {(previewMetrics.credit_utilization * 100).toFixed(2)}%</p>
            </div>
          </div>

          <div className='col-span-full'>
            <Button type='submit' disabled={submitting}>
              {submitting ? 'Submitting...' : 'Create Borrower Profile'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

function Field({
  label,
  value,
  onChange
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className='grid gap-2'>
      <Label>{label}</Label>
      <Input type='number' value={Number.isFinite(value) ? value : 0} onChange={(e) => onChange(Number(e.target.value))} />
    </div>
  );
}
