from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _pct(value: float) -> str:
    return f'{value * 100:.2f}%'


def generate_underwriting_pdf(
    *,
    borrower_profile: dict,
    metrics: dict,
    decision: dict,
    documents: list[dict],
) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph('UnderwriteAI - Mortgage Underwriting Report', styles['Title']))
    story.append(Spacer(1, 12))

    profile_data = [
        ['Annual Income', f"${borrower_profile['annual_income']:,.2f}"],
        ['Credit Score', str(borrower_profile['credit_score'])],
        ['Monthly Debts', f"${borrower_profile['monthly_debts']:,.2f}"],
        ['Assets', f"${borrower_profile['assets']:,.2f}"],
        ['Loan Amount', f"${borrower_profile['loan_amount']:,.2f}"],
        ['Down Payment', f"${borrower_profile['down_payment']:,.2f}"],
    ]
    story.append(Paragraph('Borrower Profile', styles['Heading2']))
    story.extend(_build_table(profile_data))

    metric_data = [
        ['DTI', _pct(metrics['dti'])],
        ['LTV', _pct(metrics['ltv'])],
        ['Credit Utilization', _pct(metrics['credit_utilization'])],
        ['Risk Score', f"{metrics['risk_score']:.2f}"],
        ['Risk Band', metrics['risk_band']],
    ]
    story.append(Spacer(1, 8))
    story.append(Paragraph('Financial Metrics', styles['Heading2']))
    story.extend(_build_table(metric_data))

    decision_data = [
        ['Decision', decision['decision']],
        ['Risk Category', decision['risk_category']],
        ['Approval Probability', _pct(decision['approval_probability'])],
    ]
    story.append(Spacer(1, 8))
    story.append(Paragraph('Loan Decision', styles['Heading2']))
    story.extend(_build_table(decision_data))

    story.append(Spacer(1, 8))
    story.append(Paragraph('AI Explanation', styles['Heading2']))
    story.append(Paragraph(decision['explanation'], styles['BodyText']))

    if decision.get('conditions'):
        story.append(Spacer(1, 8))
        story.append(Paragraph('Conditions', styles['Heading3']))
        for condition in decision['conditions']:
            story.append(Paragraph(f'- {condition}', styles['BodyText']))

    if documents:
        story.append(Spacer(1, 8))
        story.append(Paragraph('Documents Processed', styles['Heading2']))
        for item in documents:
            story.append(Paragraph(f"- {item['filename']} ({item['document_type']})", styles['BodyText']))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _build_table(rows: list[list[str]]) -> list:
    table = Table(rows, colWidths=[220, 280])
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
        )
    )
    return [table]
