import Link from 'next/link';
import type { ReactNode } from 'react';
import { ArrowRight, BarChart3, FileCheck2, ShieldCheck } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  return (
    <main className='relative min-h-screen overflow-hidden bg-grid px-4 py-8 md:px-8'>
      <div className='mx-auto flex w-full max-w-7xl flex-col gap-10'>
        <header className='flex items-center justify-between rounded-xl border border-border/60 bg-card/70 px-4 py-3 backdrop-blur md:px-6'>
          <div>
            <p className='font-mono text-xs uppercase tracking-[0.25em] text-muted-foreground'>UnderwriteAI</p>
            <p className='font-heading text-lg font-semibold'>Autonomous Mortgage Intelligence</p>
          </div>
          <Link href='/dashboard'>
            <Button>Open Dashboard</Button>
          </Link>
        </header>

        <section className='grid gap-6 lg:grid-cols-[1.2fr_1fr]'>
          <Card className='border-border/60 bg-card/80'>
            <CardHeader>
              <Badge className='w-fit'>AI Underwriting Workspace</Badge>
              <CardTitle className='text-3xl md:text-5xl'>Smarter loan decisions with transparent risk signals</CardTitle>
              <CardDescription className='max-w-2xl text-base'>
                Collect borrower data, process uploaded income documents, evaluate DTI/LTV/utilization, and generate an explainable
                underwriting decision in one workflow.
              </CardDescription>
            </CardHeader>
            <CardContent className='space-y-6'>
              <div className='flex flex-wrap gap-3'>
                <Link href='/dashboard'>
                  <Button size='lg'>
                    Launch Underwriting
                    <ArrowRight className='ml-2 h-4 w-4' />
                  </Button>
                </Link>
                <Badge className='px-3 py-2 text-xs'>OCR + AI Extraction</Badge>
                <Badge className='px-3 py-2 text-xs'>Scenario Simulator</Badge>
                <Badge className='px-3 py-2 text-xs'>PDF Report Export</Badge>
              </div>

              <div className='grid gap-3 sm:grid-cols-3'>
                <MetricTile label='Core Ratios' value='DTI / LTV / Utilization' />
                <MetricTile label='Decision Outputs' value='Approve / Conditional / Deny' />
                <MetricTile label='Risk Context' value='Key Risks + Mitigants' />
              </div>
            </CardContent>
          </Card>

          <Card className='border-border/60 bg-card/80'>
            <CardHeader>
              <CardTitle>Pipeline Preview</CardTitle>
              <CardDescription>How each file moves from intake to final decision</CardDescription>
            </CardHeader>
            <CardContent className='space-y-3'>
              <Stage label='1. Borrower Intake' detail='Financial profile captured with real-time ratios' />
              <Stage label='2. Document Intelligence' detail='OCR + structured extraction from W-2/pay stubs/statements' />
              <Stage label='3. Risk & Decision Engine' detail='Agent reasoning + deterministic guardrails' />
              <Stage label='4. Report Generation' detail='Downloadable underwriting summary in PDF format' />
            </CardContent>
          </Card>
        </section>

        <section className='grid gap-4 md:grid-cols-3'>
          <FeatureCard
            icon={<FileCheck2 className='h-5 w-5' />}
            title='Document Understanding'
            description='Converts uploaded borrower files into reusable financial attributes for downstream underwriting logic.'
          />
          <FeatureCard
            icon={<BarChart3 className='h-5 w-5' />}
            title='Scenario Simulation'
            description='Model eligibility changes by adjusting income, debt, down payment, or requested loan amount.'
          />
          <FeatureCard
            icon={<ShieldCheck className='h-5 w-5' />}
            title='Explainable Decisions'
            description='Each decision includes probability, risk category, rationale, and conditional requirements.'
          />
        </section>
      </div>
    </main>
  );
}

function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className='rounded-lg border border-border/60 bg-muted/30 p-3'>
      <p className='text-xs uppercase tracking-wide text-muted-foreground'>{label}</p>
      <p className='mt-2 text-sm font-semibold'>{value}</p>
    </div>
  );
}

function Stage({ label, detail }: { label: string; detail: string }) {
  return (
    <div className='rounded-lg border border-border/60 bg-muted/25 p-3'>
      <p className='text-sm font-semibold'>{label}</p>
      <p className='mt-1 text-xs text-muted-foreground'>{detail}</p>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description
}: {
  icon: ReactNode;
  title: string;
  description: string;
}) {
  return (
    <Card className='border-border/60 bg-card/75'>
      <CardHeader>
        <div className='flex h-10 w-10 items-center justify-center rounded-lg bg-primary/15 text-primary'>{icon}</div>
        <CardTitle className='text-xl'>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className='text-sm text-muted-foreground'>{description}</p>
      </CardContent>
    </Card>
  );
}
