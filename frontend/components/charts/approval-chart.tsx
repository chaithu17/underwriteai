'use client';

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

export function ApprovalChart({ probability }: { probability: number | null }) {
  if (probability === null) {
    return <p className='text-sm text-muted-foreground'>Underwriting decision required to show approval probability.</p>;
  }

  const pct = Number((probability * 100).toFixed(1));
  const data = [
    { name: 'Approval', value: pct },
    { name: 'Remaining', value: 100 - pct }
  ];

  return (
    <div className='h-64 w-full'>
      <ResponsiveContainer width='100%' height='100%'>
        <PieChart>
          <Pie
            data={data}
            dataKey='value'
            innerRadius={70}
            outerRadius={100}
            startAngle={90}
            endAngle={-270}
            paddingAngle={1}
          >
            <Cell fill='#0ea5e9' />
            <Cell fill='#334155' />
          </Pie>
          <Tooltip formatter={(value: number) => `${value}%`} />
        </PieChart>
      </ResponsiveContainer>
      <div className='-mt-36 text-center'>
        <p className='font-heading text-3xl font-semibold'>{pct}%</p>
        <p className='text-sm text-muted-foreground'>Approval Probability</p>
      </div>
    </div>
  );
}
