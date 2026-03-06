from __future__ import annotations

import json
import re
from pathlib import Path

import pytesseract
from PIL import Image
from pypdf import PdfReader

from app.core.config import get_settings
from app.schemas.document import DocumentFinancialData

try:
    from pdf2image import convert_from_path
except Exception:  # pragma: no cover
    convert_from_path = None

try:
    from langchain_ollama import ChatOllama
except Exception:  # pragma: no cover
    ChatOllama = None


class DocumentProcessingService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._llm = None

        if self.settings.llm_provider.lower() == 'ollama' and ChatOllama:
            try:
                self._llm = ChatOllama(
                    model=self.settings.llm_model,
                    base_url=self.settings.ollama_base_url,
                    temperature=0,
                )
            except Exception:
                self._llm = None

    def extract_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()

        if suffix in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}:
            return self._ocr_image(file_path)

        if suffix == '.pdf':
            return self._extract_pdf_text(file_path)

        return ''

    def _ocr_image(self, file_path: Path) -> str:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    def _extract_pdf_text(self, file_path: Path) -> str:
        text_chunks: list[str] = []
        reader = PdfReader(str(file_path))

        for page in reader.pages:
            text_chunks.append(page.extract_text() or '')

        merged_text = '\n'.join(chunk.strip() for chunk in text_chunks if chunk.strip())
        if merged_text:
            return merged_text

        if convert_from_path:
            images = convert_from_path(str(file_path), first_page=1, last_page=3)
            ocr_chunks = [pytesseract.image_to_string(image) for image in images]
            return '\n'.join(chunk for chunk in ocr_chunks if chunk.strip())

        return ''

    def extract_structured_data(self, raw_text: str) -> DocumentFinancialData:
        if self._llm and raw_text.strip():
            structured = self._llm_extract(raw_text)
            if structured:
                return structured

        return self._regex_extract(raw_text)

    def _llm_extract(self, raw_text: str) -> DocumentFinancialData | None:
        prompt = (
            'Extract financial details from mortgage docs and return strict JSON with keys: '
            'employer, annual_income, bank_balance, pay_frequency, detected_debts. '
            'Use null when unknown.\n\n'
            f'Document text:\n{raw_text[:12000]}'
        )

        try:
            result = self._llm.invoke(prompt)
            payload = self._safe_json_loads(result.content)
            if not payload:
                return None
            return DocumentFinancialData(**payload)
        except Exception:
            return None

    @staticmethod
    def _safe_json_loads(content: str | list) -> dict | None:
        if isinstance(content, list):
            content = ''.join(str(part) for part in content)

        text = str(content).strip()
        if text.startswith('```'):
            text = text.strip('`')
            text = text.replace('json\n', '', 1)

        try:
            return json.loads(text)
        except Exception:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group())
            except Exception:
                return None

    @staticmethod
    def _regex_extract(raw_text: str) -> DocumentFinancialData:
        employer_match = re.search(r'(Employer|Company)\s*[:\-]\s*([A-Za-z0-9 &,.]+)', raw_text, re.IGNORECASE)
        income_match = re.search(r'(Annual Income|Salary)\s*[:\-\$\s]*([0-9,]+(?:\.[0-9]{1,2})?)', raw_text, re.IGNORECASE)
        bank_match = re.search(r'(Balance|Bank Balance)\s*[:\-\$\s]*([0-9,]+(?:\.[0-9]{1,2})?)', raw_text, re.IGNORECASE)

        return DocumentFinancialData(
            employer=employer_match.group(2).strip() if employer_match else None,
            annual_income=float(income_match.group(2).replace(',', '')) if income_match else None,
            bank_balance=float(bank_match.group(2).replace(',', '')) if bank_match else None,
            pay_frequency=None,
            detected_debts=None,
        )
