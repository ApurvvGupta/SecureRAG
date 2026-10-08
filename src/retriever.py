"""Retrieval and reranking for the RAG pipeline."""

import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import RAGConfig

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Retriever with optional reranking support."""

    def __init__(self, vectorstore: Chroma, config: RAGConfig):
        self.vectorstore = vectorstore
        self.config = config

    def retrieve(self, query: str) -> list[dict]:
        """Retrieve relevant documents for a query."""
        results = self.vectorstore.similarity_search_with_score(
            query, k=self.config.top_k
        )

        documents = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
            for doc, score in results
        ]

        if self.config.use_reranking:
            documents = self._rerank(query, documents)

        return documents[: self.config.rerank_top_k]

    def _rerank(self, query: str, documents: list[dict]) -> list[dict]:
        """Rerank retrieved documents."""
        # TODO: Implement cross-encoder reranking
        logger.info("Reranking %d documents", len(documents))
        return documents
