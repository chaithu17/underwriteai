'use client';

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { Metrics, ScenarioOutput } from '@/lib/types';

export function ScenarioChart({ baseline, scenario }: { baseline: Metrics | null; scenario: ScenarioOutput | null }) {
  if (!baseline || !scenario) {
    return <p className='text-sm text-muted-foreground'>Run a scenario simulation to compare baseline and projected metrics.</p>;
  }

  const data = [
    {
      metric: 'DTI',
      baseline: Number((baseline.dti * 100).toFixed(2)),
      scenario: Number((scenario.metrics.dti * 100).toFixed(2))
    },
    {
      metric: 'LTV',
      baseline: Number((baseline.ltv * 100).toFixed(2)),
      scenario: Number((scenario.metrics.ltv * 100).toFixed(2))
    },
    {
      metric: 'Utilization',
      baseline: Number((baseline.credit_utilization * 100).toFixed(2)),
      scenario: Number((scenario.metrics.credit_utilization * 100).toFixed(2))
    }
  ];

  return (
    <div className='h-64 w-full'>
      <ResponsiveContainer width='100%' height='100%'>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray='3 3' opacity={0.2} />
          <XAxis dataKey='metric' />
          <YAxis unit='%' />
          <Tooltip formatter={(value: number) => `${value}%`} />
          <Line type='monotone' dataKey='baseline' stroke='#64748b' strokeWidth={2} />
          <Line type='monotone' dataKey='scenario' stroke='#f97316' strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
