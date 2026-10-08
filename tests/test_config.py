"""Tests for SecureRAG configuration."""

import pytest
from src.config import RAGConfig


def test_default_config():
    config = RAGConfig()
    assert config.chunk_size == 512
    assert config.top_k == 5
    assert config.use_reranking is True


def test_chunk_overlap_less_than_size():
    config = RAGConfig()
    assert config.chunk_overlap < config.chunk_size
