"""Evaluation framework for the SecureRAG agent."""

import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class EvalMetrics:
    """Evaluation metrics for the RAG pipeline."""
    total_queries: int = 0
    correct_answers: int = 0
    hallucinated_answers: int = 0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    retrieval_precision: float = 0.0

    @property
    def accuracy(self) -> float:
        return self.correct_answers / max(self.total_queries, 1)

    @property
    def hallucination_rate(self) -> float:
        return self.hallucinated_answers / max(self.total_queries, 1)


def evaluate_agent(
    agent,
    test_queries: list[dict],
    ground_truth: list[dict],
) -> EvalMetrics:
    """Run evaluation on the agent with test queries."""
    metrics = EvalMetrics(total_queries=len(test_queries))
    latencies = []

    for query, truth in zip(test_queries, ground_truth):
        start = time.time()
        # TODO: Run agent and compare with ground truth
        latency = (time.time() - start) * 1000
        latencies.append(latency)

    if latencies:
        metrics.avg_latency_ms = sum(latencies) / len(latencies)
        latencies.sort()
        p95_idx = int(len(latencies) * 0.95)
        metrics.p95_latency_ms = latencies[min(p95_idx, len(latencies) - 1)]

    return metrics


def save_eval_results(metrics: EvalMetrics, output_path: Path) -> None:
    """Save evaluation results."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(asdict(metrics), f, indent=2)
    logger.info(f"Results saved to {output_path}")
