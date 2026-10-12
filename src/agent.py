"""LangGraph-based cybersecurity Q&A agent."""

import logging
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from .config import RAGConfig
from .retriever import HybridRetriever

logger = logging.getLogger(__name__)


from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from .config import RAGConfig
from .retriever import HybridRetriever
from .prompts import SYSTEM_PROMPT, format_rag_prompt

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the RAG agent graph with conversation memory."""
    query: str
    chat_history: List[dict]
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

    def retrieve_node(state: AgentState) -> dict:
        """Retrieve relevant documents."""
        docs = retriever.retrieve(state["query"])
        return {"retrieved_docs": docs}

    def generate_node(state: AgentState) -> dict:
        """Generate answer from retrieved context with citation enforcement."""
        formatted_prompt = format_rag_prompt(state["retrieved_docs"], state["query"])
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": formatted_prompt},
        ]

        response = llm.invoke(messages)

        sources = list(set([
            doc["metadata"].get("source", "unknown")
            for doc in state["retrieved_docs"]
        ]))

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
