'use client';

import { useEffect, useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export type ScenarioState = {
  annual_income: number;
  monthly_debts: number;
  loan_amount: number;
  down_payment: number;
};

export function ScenarioSimulator({
  disabled,
  initial,
  onSimulate
}: {
  disabled: boolean;
  initial: ScenarioState;
  onSimulate: (payload: { scenarioName: string; overrides: Partial<ScenarioState> }) => Promise<void>;
}) {
  const [scenarioName, setScenarioName] = useState('Higher Down Payment');
  const [values, setValues] = useState<ScenarioState>(initial);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setValues(initial);
  }, [initial]);

  const changes = useMemo(() => {
    return {
      annual_income: values.annual_income !== initial.annual_income ? values.annual_income : undefined,
      monthly_debts: values.monthly_debts !== initial.monthly_debts ? values.monthly_debts : undefined,
      loan_amount: values.loan_amount !== initial.loan_amount ? values.loan_amount : undefined,
      down_payment: values.down_payment !== initial.down_payment ? values.down_payment : undefined
    };
  }, [initial, values]);

  const hasChanges = Object.values(changes).some((value) => value !== undefined);

  const handleRun = async () => {
    setLoading(true);
    try {
      await onSimulate({ scenarioName, overrides: changes });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Scenario Simulator</CardTitle>
        <CardDescription>Tune key inputs to project approval impact in real time.</CardDescription>
      </CardHeader>
      <CardContent className='grid gap-4 md:grid-cols-2'>
        <div className='grid gap-2 md:col-span-2'>
          <Label>Scenario Name</Label>
          <Input value={scenarioName} onChange={(e) => setScenarioName(e.target.value)} />
        </div>
        <ScenarioField
          label='Annual Income'
          value={values.annual_income}
          onChange={(value) => setValues((prev) => ({ ...prev, annual_income: value }))}
        />
        <ScenarioField
          label='Monthly Debts'
          value={values.monthly_debts}
          onChange={(value) => setValues((prev) => ({ ...prev, monthly_debts: value }))}
        />
        <ScenarioField
          label='Loan Amount'
          value={values.loan_amount}
          onChange={(value) => setValues((prev) => ({ ...prev, loan_amount: value }))}
        />
        <ScenarioField
          label='Down Payment'
          value={values.down_payment}
          onChange={(value) => setValues((prev) => ({ ...prev, down_payment: value }))}
        />

        <div className='md:col-span-2'>
          {!hasChanges && <p className='mb-2 text-xs text-muted-foreground'>Adjust at least one value to run a scenario.</p>}
          <Button disabled={disabled || loading || !hasChanges} onClick={handleRun}>
            {loading ? 'Running Simulation...' : 'Run Simulation'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function ScenarioField({
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
      <Input type='number' value={value} onChange={(e) => onChange(Number(e.target.value))} />
    </div>
  );
}
