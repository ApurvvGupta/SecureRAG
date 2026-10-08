from pathlib import Path
from dataclasses import dataclass

@dataclass
class RAGConfig:
    """Configuration for the RAG pipeline."""
    # Embedding
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 50
    
    # Retrieval
    top_k: int = 5
    collection_name: str = "cve_advisories"
    persist_dir: Path = Path("data/vectorstore")
    
    # LLM
    llm_model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.1
    max_tokens: int = 1024
    
    # Reranking
    use_reranking: bool = True
    rerank_top_k: int = 3
