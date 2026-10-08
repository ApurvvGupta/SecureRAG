"""Data ingestion pipeline for CVE and MITRE ATT&CK advisories."""

import json
import logging
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import RAGConfig

logger = logging.getLogger(__name__)


def create_text_splitter(config: RAGConfig) -> RecursiveCharacterTextSplitter:
    """Create text splitter with configured chunk size and overlap."""
    return RecursiveCharacterTextSplitter(
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )


def create_embeddings(config: RAGConfig) -> HuggingFaceEmbeddings:
    """Initialize embedding model."""
    return HuggingFaceEmbeddings(
        model_name=config.embedding_model,
        model_kwargs={"device": "cpu"},
    )


def ingest_documents(
    documents_dir: Path,
    config: RAGConfig,
) -> Chroma:
    """Load, chunk, embed, and store documents in ChromaDB."""
    # TODO: Implement document loading from CVE/MITRE sources
    raise NotImplementedError(
        "Implement document loading for CVE/MITRE ATT&CK data"
    )
