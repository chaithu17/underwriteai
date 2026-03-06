'use client';

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import { Metrics } from '@/lib/types';

export function RatiosChart({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) {
    return <p className='text-sm text-muted-foreground'>Submit borrower profile to render ratios chart.</p>;
  }

  const data = [
    { name: 'DTI', value: Number((metrics.dti * 100).toFixed(2)), fill: '#0ea5e9' },
    { name: 'LTV', value: Number((metrics.ltv * 100).toFixed(2)), fill: '#14b8a6' },
    { name: 'Utilization', value: Number((metrics.credit_utilization * 100).toFixed(2)), fill: '#f59e0b' }
  ];

  return (
    <div className='h-64 w-full'>
      <ResponsiveContainer width='100%' height='100%'>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray='3 3' opacity={0.2} />
          <XAxis dataKey='name' />
          <YAxis unit='%' />
          <Tooltip formatter={(value: number) => [`${value}%`, 'Ratio']} />
          <Bar dataKey='value' radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
