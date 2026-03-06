'use client';

import { AlertTriangle, CheckCircle2, FileText } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { UnderwritingDecision } from '@/lib/types';

export function DecisionPanel({ decision }: { decision: UnderwritingDecision | null }) {
  if (!decision) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>AI Underwriting Decision</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-sm text-muted-foreground'>Run underwriting evaluation after borrower intake and document upload.</p>
        </CardContent>
      </Card>
    );
  }

  const isApproved = decision.decision === 'APPROVED';

  return (
    <Card>
      <CardHeader>
        <CardTitle className='flex items-center gap-2'>
          {isApproved ? <CheckCircle2 className='h-5 w-5 text-emerald-500' /> : <AlertTriangle className='h-5 w-5 text-amber-500' />}
          AI Underwriting Decision
        </CardTitle>
      </CardHeader>
      <CardContent className='space-y-4'>
        <div className='flex flex-wrap items-center gap-2'>
          <Badge>{decision.decision}</Badge>
          <Badge>{decision.risk_category}</Badge>
          <Badge>{(decision.approval_probability * 100).toFixed(1)}% probability</Badge>
        </div>

        <div className='rounded-lg border border-border/70 bg-muted/20 p-4'>
          <p className='text-sm leading-relaxed'>{decision.explanation}</p>
        </div>

        {!!decision.reasoning_json?.conditions?.length && (
          <div>
            <p className='mb-2 flex items-center gap-2 text-sm font-semibold'>
              <FileText className='h-4 w-4' /> Conditions
            </p>
            <ul className='space-y-1 text-sm text-muted-foreground'>
              {decision.reasoning_json.conditions.map((condition, idx) => (
                <li key={`${condition}-${idx}`}>- {condition}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
