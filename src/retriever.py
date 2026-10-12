"""Retrieval and reranking for the RAG pipeline."""

import logging
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import RAGConfig

logger = logging.getLogger(__name__)


from typing import Optional
try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None


class HybridRetriever:
    """Retriever with optional reranking support."""

    def __init__(self, vectorstore: Chroma, config: RAGConfig):
        self.vectorstore = vectorstore
        self.config = config
        self._reranker: Optional[CrossEncoder] = None

        if self.config.use_reranking and CrossEncoder is not None:
            try:
                # Load lightweight cross-encoder for MS MARCO passage reranking
                self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
                logger.info("Initialized CrossEncoder reranker model successfully.")
            except Exception as e:
                logger.warning("Could not initialize CrossEncoder model: %s. Falling back to dense scores.", e)

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

        if self.config.use_reranking and documents:
            documents = self._rerank(query, documents)

        return documents[: self.config.rerank_top_k]

    def _rerank(self, query: str, documents: list[dict]) -> list[dict]:
        """Rerank retrieved documents using cross-encoder scores."""
        if not self._reranker:
            logger.debug("No cross-encoder loaded; skipping rerank step.")
            return documents

        logger.info("Reranking %d candidate documents with CrossEncoder", len(documents))
        pairs = [[query, doc["content"]] for doc in documents]
        scores = self._reranker.predict(pairs)

        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        # Sort documents descending by reranker score
        reranked_docs = sorted(documents, key=lambda d: d.get("rerank_score", 0.0), reverse=True)
        return reranked_docs
