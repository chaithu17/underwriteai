from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from app.core.config import get_settings

try:
    from langchain_community.vectorstores import Chroma
    from langchain_ollama import OllamaEmbeddings
except Exception:  # pragma: no cover
    Chroma = None
    OllamaEmbeddings = None


class VectorStoreService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.enabled = False
        self.vector_store = None

        if not self.settings.enable_vector_store:
            return

        if self.settings.llm_provider.lower() != 'ollama' or not Chroma or not OllamaEmbeddings:
            return

        try:
            persist_dir = Path(self.settings.vector_db_path)
            persist_dir.mkdir(parents=True, exist_ok=True)

            embeddings = OllamaEmbeddings(
                model=self.settings.embedding_model,
                base_url=self.settings.ollama_base_url,
            )
            self.vector_store = Chroma(
                collection_name='underwrite_ai_context',
                embedding_function=embeddings,
                persist_directory=str(persist_dir),
            )
            self.enabled = True
        except Exception:
            self.enabled = False
            self.vector_store = None

    def upsert_text(self, text: str, metadata: dict[str, Any]) -> None:
        if not self.enabled or not text.strip():
            return

        doc = Document(page_content=text[:15000], metadata=metadata)
        try:
            self.vector_store.add_documents(documents=[doc])
            if hasattr(self.vector_store, 'persist'):
                self.vector_store.persist()
        except Exception:
            return

    def retrieve(self, query: str, k: int = 3) -> list[str]:
        if not self.enabled or not query.strip():
            return []

        try:
            docs = self.vector_store.similarity_search(query=query, k=k)
            return [doc.page_content for doc in docs]
        except Exception:
            return []
