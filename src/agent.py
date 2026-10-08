"""LangGraph-based cybersecurity Q&A agent."""

import logging
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from .config import RAGConfig
from .retriever import HybridRetriever

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the RAG agent graph."""
    query: str
    retrieved_docs: list[dict]
    answer: str
    sources: list[str]
    confidence: float


def build_agent(retriever: HybridRetriever, config: RAGConfig) -> StateGraph:
    """Build the LangGraph agent for cybersecurity Q&A."""

    llm = ChatAnthropic(
        model=config.llm_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    def retrieve_node(state: AgentState) -> AgentState:
        """Retrieve relevant documents."""
        docs = retriever.retrieve(state["query"])
        return {"retrieved_docs": docs}

    def generate_node(state: AgentState) -> AgentState:
        """Generate answer from retrieved context."""
        context = "\n\n".join(
            doc["content"] for doc in state["retrieved_docs"]
        )

        prompt = f"""You are a cybersecurity expert. Answer the question based
only on the provided context. If the context doesn't contain enough
information, say so clearly.

Context:
{context}

Question: {state['query']}

Provide a detailed, accurate answer with references to specific CVEs or
MITRE ATT&CK techniques when applicable."""

        response = llm.invoke(prompt)

        sources = [
            doc["metadata"].get("source", "unknown")
            for doc in state["retrieved_docs"]
        ]

        return {
            "answer": response.content,
            "sources": sources,
        }

    # Build the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
