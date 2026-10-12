"""Faithfulness and hallucination metric evaluators for SecureRAG responses."""

import re
from typing import Dict, List, Set


class FaithfulnessEvaluator:
    """Evaluates whether claims and identifiers in generated answers are grounded in context."""

    CVE_PATTERN = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)
    MITRE_PATTERN = re.compile(r"T\d{4}(?:\.\d{3})?", re.IGNORECASE)

    @classmethod
    def extract_identifiers(cls, text: str) -> Set[str]:
        """Extract all CVEs and MITRE technique IDs from text."""
        cves = set(cls.CVE_PATTERN.findall(text.upper()))
        mitre = set(cls.MITRE_PATTERN.findall(text.upper()))
        return cves.union(mitre)

    @classmethod
    def evaluate_claim_grounding(
        cls,
        context: str,
        generated_answer: str
    ) -> Dict[str, float]:
        """Check whether security identifiers mentioned in the answer exist in context."""
        context_ids = cls.extract_identifiers(context)
        answer_ids = cls.extract_identifiers(generated_answer)

        if not answer_ids:
            # No specific technical identifiers cited to hallucinate
            return {
                "identifier_hallucination_rate": 0.0,
                "identifier_precision": 1.0,
                "total_cited_ids": 0,
                "unsupported_ids_count": 0,
            }

        unsupported_ids = answer_ids - context_ids
        hallucination_rate = len(unsupported_ids) / len(answer_ids)
        precision = 1.0 - hallucination_rate

        return {
            "identifier_hallucination_rate": float(hallucination_rate),
            "identifier_precision": float(precision),
            "total_cited_ids": len(answer_ids),
            "unsupported_ids_count": len(unsupported_ids),
        }
