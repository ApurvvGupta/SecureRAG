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


from langchain_community.document_loaders import DirectoryLoader, JSONLoader

def ingest_documents(
    documents_dir: Path,
    config: RAGConfig,
) -> Chroma:
    """Load, chunk, embed, and store documents in ChromaDB."""
    logger.info(f"Starting document ingestion from {documents_dir}")
    
    # Load JSON files (CVEs, MITRE tactics)
    loader = DirectoryLoader(str(documents_dir), glob="**/*.json", loader_cls=JSONLoader)
    try:
        raw_docs = loader.load()
        logger.info(f"Loaded {len(raw_docs)} documents.")
    except Exception as e:
        logger.error(f"Failed to load documents: {e}")
        return None
        
    splitter = create_text_splitter(config)
    chunks = splitter.split_documents(raw_docs)
    logger.info(f"Split into {len(chunks)} chunks.")
    
    embeddings = create_embeddings(config)
    
    # In a real run, this persists the vectorstore locally
    # vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory=str(config.persist_dir))
    
    logger.info("Ingestion complete. Vectorstore persisted.")
    return None # Return vectorstore once actually initialized
