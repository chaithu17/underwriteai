from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.schemas.underwriting import DecisionEnum, RiskCategoryEnum, UnderwritingDecisionOutput

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama import ChatOllama
except Exception:  # pragma: no cover
    ChatPromptTemplate = None
    ChatOllama = None

try:
    from langchain_groq import ChatGroq
except Exception:  # pragma: no cover
    ChatGroq = None


class DocumentAgentOutput(BaseModel):
    summary: str
    inferred_income_stability: str = Field(description='stable | mixed | unstable')
    potential_issues: list[str] = Field(default_factory=list)


class IncomeVerificationOutput(BaseModel):
    verified: bool
    discrepancy_notes: list[str] = Field(default_factory=list)


class RiskAnalysisOutput(BaseModel):
    key_risks: list[str] = Field(default_factory=list)
    mitigants: list[str] = Field(default_factory=list)
    recommended_conditions: list[str] = Field(default_factory=list)
    probability_adjustment: float = Field(default=0.0, ge=-0.35, le=0.35)


class DecisionAgentOutput(BaseModel):
    decision: DecisionEnum
    risk_category: RiskCategoryEnum
    approval_probability: float = Field(..., ge=0, le=1)
    explanation: str


class ReportAgentOutput(BaseModel):
    executive_summary: str


class UnderwritingAgentOrchestrator:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.llm = None

        if self.settings.llm_provider.lower() == 'groq' and ChatGroq and self.settings.groq_api_key:
            try:
                self.llm = ChatGroq(
                    model=self.settings.groq_model,
                    api_key=self.settings.groq_api_key,
                    temperature=0.1,
                )
            except Exception:
                self.llm = None
        elif self.settings.llm_provider.lower() == 'ollama' and ChatOllama:
            try:
                self.llm = ChatOllama(
                    model=self.settings.llm_model,
                    base_url=self.settings.ollama_base_url,
                    temperature=0.1,
                )
            except Exception:
                self.llm = None

    def run(
        self,
        *,
        profile: dict[str, Any],
        metrics: dict[str, Any],
        documents: list[dict[str, Any]],
        rag_context: list[str],
    ) -> UnderwritingDecisionOutput:
        if not self.llm or not ChatPromptTemplate:
            return self._rule_based_decision(metrics=metrics, profile=profile, documents=documents)

        try:
            doc_stage = self._document_agent(documents=documents, rag_context=rag_context)
            income_stage = self._income_verification_agent(profile=profile, doc_stage=doc_stage, documents=documents)
            risk_stage = self._risk_analysis_agent(metrics=metrics, income_stage=income_stage, doc_stage=doc_stage)
            decision_stage = self._decision_agent(
                profile=profile,
                metrics=metrics,
                doc_stage=doc_stage,
                income_stage=income_stage,
                risk_stage=risk_stage,
            )
            report_stage = self._report_agent(profile=profile, decision_stage=decision_stage, risk_stage=risk_stage)

            return UnderwritingDecisionOutput(
                decision=decision_stage.decision,
                risk_category=decision_stage.risk_category,
                approval_probability=decision_stage.approval_probability,
                explanation=f"{decision_stage.explanation}\n\n{report_stage.executive_summary}",
                key_risks=risk_stage.key_risks,
                mitigants=risk_stage.mitigants,
                conditions=risk_stage.recommended_conditions,
            )
        except Exception:
            return self._rule_based_decision(metrics=metrics, profile=profile, documents=documents)

    def _document_agent(self, *, documents: list[dict[str, Any]], rag_context: list[str]) -> DocumentAgentOutput:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are Document Agent for mortgage underwriting. Analyze extracted documents and provide concise risk-relevant output.',
                ),
                (
                    'human',
                    'Documents JSON:\n{documents}\n\nRetrieved Context:\n{rag_context}\n'
                    'Return structured output only.',
                ),
            ]
        )
        chain = prompt | self.llm.with_structured_output(DocumentAgentOutput)
        return chain.invoke({'documents': documents, 'rag_context': rag_context})

    def _income_verification_agent(
        self,
        *,
        profile: dict[str, Any],
        doc_stage: DocumentAgentOutput,
        documents: list[dict[str, Any]],
    ) -> IncomeVerificationOutput:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are Income Verification Agent. Compare borrower-declared income with document evidence and identify discrepancies.',
                ),
                (
                    'human',
                    'Borrower profile: {profile}\nDocument agent output: {doc_stage}\nDocuments: {documents}\nReturn structured output.',
                ),
            ]
        )
        chain = prompt | self.llm.with_structured_output(IncomeVerificationOutput)
        return chain.invoke({'profile': profile, 'doc_stage': doc_stage.model_dump(), 'documents': documents})

    def _risk_analysis_agent(
        self,
        *,
        metrics: dict[str, Any],
        income_stage: IncomeVerificationOutput,
        doc_stage: DocumentAgentOutput,
    ) -> RiskAnalysisOutput:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are Risk Analysis Agent. Evaluate DTI/LTV/credit utilization, documentation quality, and verification confidence.',
                ),
                (
                    'human',
                    'Metrics: {metrics}\nIncome stage: {income_stage}\nDocument stage: {doc_stage}\nReturn structured output.',
                ),
            ]
        )
        chain = prompt | self.llm.with_structured_output(RiskAnalysisOutput)
        return chain.invoke(
            {
                'metrics': metrics,
                'income_stage': income_stage.model_dump(),
                'doc_stage': doc_stage.model_dump(),
            }
        )

    def _decision_agent(
        self,
        *,
        profile: dict[str, Any],
        metrics: dict[str, Any],
        doc_stage: DocumentAgentOutput,
        income_stage: IncomeVerificationOutput,
        risk_stage: RiskAnalysisOutput,
    ) -> DecisionAgentOutput:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    'system',
                    'You are Loan Decision Agent. Make a prudent mortgage underwriting decision. Avoid approval when severe risks are unresolved.',
                ),
                (
                    'human',
                    'Profile: {profile}\nMetrics: {metrics}\nDoc stage: {doc_stage}\nIncome stage: {income_stage}\nRisk stage: {risk_stage}\nReturn structured output.',
                ),
            ]
        )
        chain = prompt | self.llm.with_structured_output(DecisionAgentOutput)
        return chain.invoke(
            {
                'profile': profile,
                'metrics': metrics,
                'doc_stage': doc_stage.model_dump(),
                'income_stage': income_stage.model_dump(),
                'risk_stage': risk_stage.model_dump(),
            }
        )

    def _report_agent(
        self,
        *,
        profile: dict[str, Any],
        decision_stage: DecisionAgentOutput,
        risk_stage: RiskAnalysisOutput,
    ) -> ReportAgentOutput:
        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', 'You are Report Generator Agent for a lender-facing underwriting report.'),
                (
                    'human',
                    'Profile: {profile}\nDecision: {decision}\nRisk detail: {risk}\nCreate a concise professional summary.',
                ),
            ]
        )
        chain = prompt | self.llm.with_structured_output(ReportAgentOutput)
        return chain.invoke(
            {
                'profile': profile,
                'decision': decision_stage.model_dump(),
                'risk': risk_stage.model_dump(),
            }
        )

    def _rule_based_decision(
        self,
        *,
        metrics: dict[str, Any],
        profile: dict[str, Any] | None = None,
        documents: list[dict[str, Any]] | None = None,
    ) -> UnderwritingDecisionOutput:
        profile = profile or {}
        documents = documents or []

        dti = metrics['dti']
        ltv = metrics['ltv']
        utilization = metrics['credit_utilization']
        risk_band = metrics['risk_band']
        risk_score = float(metrics.get('risk_score', 0.0))
        credit_score = int(profile.get('credit_score', 680))
        annual_income = float(profile.get('annual_income', 0.0) or 0.0)
        monthly_debts = float(profile.get('monthly_debts', 0.0) or 0.0)
        assets = float(profile.get('assets', 0.0) or 0.0)
        loan_amount = float(profile.get('loan_amount', 0.0) or 0.0)

        # Approximate reserve strength using debt + estimated mortgage payment.
        estimated_housing_payment = loan_amount * 0.006
        total_monthly_obligations = max(monthly_debts + estimated_housing_payment, 1.0)
        liquidity_months = assets / total_monthly_obligations

        document_count = len(documents)
        extracted_incomes = [
            float(doc.get('extracted_json', {}).get('annual_income'))
            for doc in documents
            if doc.get('extracted_json', {}).get('annual_income') is not None
        ]
        income_mismatch = False
        if annual_income > 0 and extracted_incomes:
            avg_doc_income = sum(extracted_incomes) / len(extracted_incomes)
            income_mismatch = abs(avg_doc_income - annual_income) / annual_income > 0.15

        probability = 1 - min(max(risk_score, 0), 100) / 100

        if credit_score >= 760:
            probability += 0.08
        elif credit_score >= 700:
            probability += 0.04
        elif credit_score < 620:
            probability -= 0.15

        if dti > 0.50:
            probability -= 0.20
        elif dti > 0.43:
            probability -= 0.12

        if ltv > 0.97:
            probability -= 0.18
        elif ltv > 0.90:
            probability -= 0.10

        if utilization > 0.75:
            probability -= 0.12
        elif utilization > 0.50:
            probability -= 0.08

        if liquidity_months >= 6:
            probability += 0.06
        elif liquidity_months < 2:
            probability -= 0.08

        if document_count == 0:
            probability -= 0.06
        if income_mismatch:
            probability -= 0.12

        probability = max(0.01, min(0.99, round(probability, 3)))

        hard_stop = dti > 0.58 or ltv > 1.0 or utilization > 0.95 or credit_score < 560
        if hard_stop or probability < 0.40:
            decision = DecisionEnum.denied
            risk_category = RiskCategoryEnum.high
        elif (
            probability >= 0.75
            and dti <= 0.43
            and ltv <= 0.85
            and utilization <= 0.50
            and not income_mismatch
        ):
            decision = DecisionEnum.approved
            risk_category = RiskCategoryEnum.low
        else:
            decision = DecisionEnum.conditional
            risk_category = RiskCategoryEnum.moderate

        key_risks = []
        if dti > 0.43:
            key_risks.append(f'Elevated DTI at {dti:.1%}.')
        if ltv > 0.90:
            key_risks.append(f'High LTV at {ltv:.1%}.')
        if utilization > 0.50:
            key_risks.append(f'High credit utilization at {utilization:.1%}.')
        if credit_score < 640:
            key_risks.append(f'Weak credit score at {credit_score}.')
        if liquidity_months < 2:
            key_risks.append(f'Low post-close liquidity at {liquidity_months:.1f} months of obligations.')
        if income_mismatch:
            key_risks.append('Declared income diverges from uploaded document evidence.')
        if document_count == 0:
            key_risks.append('No supporting income documents uploaded.')

        mitigants = []
        if ltv < 0.80:
            mitigants.append('Strong borrower equity position.')
        if dti < 0.36:
            mitigants.append('Conservative debt burden relative to income.')
        if credit_score >= 740:
            mitigants.append('High credit quality supports repayment reliability.')
        if liquidity_months >= 6:
            mitigants.append('Strong cash reserves provide repayment cushion.')

        conditions: list[str] = []
        if decision == DecisionEnum.conditional:
            conditions.append('Provide latest 2 pay stubs and employment verification.')
            conditions.append('Maintain post-close liquidity threshold per policy.')
        if document_count == 0:
            conditions.append('Upload W-2 and latest 2 months bank statements for file completion.')
        if income_mismatch:
            conditions.append('Reconcile declared income with verified document income.')

        if decision == DecisionEnum.approved:
            explanation = (
                f'Decision: Approved. Approval probability {probability:.1%}. '
                f'Borrower metrics show DTI {dti:.1%}, LTV {ltv:.1%}, utilization {utilization:.1%}, '
                f'with risk band {risk_band}.'
            )
        elif decision == DecisionEnum.conditional:
            explanation = (
                f'Decision: Conditionally Approved. Approval probability {probability:.1%}. '
                f'Core eligibility is acceptable but file requires conditions based on leverage, documentation, '
                f'or reserve profile.'
            )
        else:
            explanation = (
                f'Decision: Denied. Approval probability {probability:.1%}. '
                f'Risk exceeds tolerance due to repayment capacity, leverage, or credit quality.'
            )

        return UnderwritingDecisionOutput(
            decision=decision,
            risk_category=risk_category,
            approval_probability=probability,
            explanation=explanation,
            key_risks=key_risks,
            mitigants=mitigants,
            conditions=conditions,
        )
