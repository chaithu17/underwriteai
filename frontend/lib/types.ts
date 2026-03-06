export type BorrowerInput = {
  annual_income: number;
  credit_score: number;
  monthly_debts: number;
  assets: number;
  loan_amount: number;
  down_payment: number;
  credit_used: number;
  credit_limit: number;
};

export type Metrics = {
  dti: number;
  ltv: number;
  credit_utilization: number;
  risk_score: number;
  risk_band: string;
};

export type UnderwritingDecision = {
  id: number;
  borrower_profile_id: number;
  decision: 'APPROVED' | 'CONDITIONALLY_APPROVED' | 'DENIED';
  risk_category: 'LOW' | 'MODERATE' | 'HIGH';
  approval_probability: number;
  explanation: string;
  reasoning_json: {
    conditions?: string[];
    key_risks?: string[];
    mitigants?: string[];
  };
};

export type ScenarioOutput = {
  metrics: Metrics;
  decision: {
    decision: 'APPROVED' | 'CONDITIONALLY_APPROVED' | 'DENIED';
    risk_category: 'LOW' | 'MODERATE' | 'HIGH';
    approval_probability: number;
    explanation: string;
    key_risks: string[];
    mitigants: string[];
    conditions: string[];
  };
};
