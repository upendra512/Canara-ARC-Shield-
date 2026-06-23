"""Retrieval node for Layer 1."""

from __future__ import annotations

from typing import Any

from retrieval.faiss_contract import search_local_index
from state.workflow import RetrievalState


def build_query(state: RetrievalState) -> str:
    """Create a simple search query from classification output."""

    query_parts = []

    regulator = state.get("regulator", "")
    if regulator != "":
        query_parts.append(regulator)

    topics = state.get("topics", [])
    query_parts.extend(topics)

    raw_text = state.get("raw_text", "")
    if raw_text != "":
        query_parts.append(raw_text[:500])

    return " ".join(query_parts)


def retrieval_node(state: RetrievalState) -> dict[str, Any]:
    """Retrieve related regulations, policies, and controls."""

    query = build_query(state)
    results = search_local_index(query, top_k=5)

    if len(results) > 0:
        retrieval_confidence = max(float(item.get("score", 0.0)) for item in results)
        status = "retrieval_completed"
    else:
        retrieval_confidence = 0.0
        status = "retrieval_no_results"

    return {
        "related_documents": results,
        "related_policies": [],
        "related_controls": [],
        "retrieval_confidence": retrieval_confidence,
        "status": status,
    }
