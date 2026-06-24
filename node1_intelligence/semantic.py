"""
Tier 2 of the Node 1 classification ladder: semantic rule-type matching.

Tier 1 (taxonomy keyword scoring in classifier.py) is fast and exact but misses
paraphrases that share no keywords with the taxonomy. This tier embeds the clause
and runs Hybrid Search against the taxonomy's own example sentences (one indexed
document per rule-type example), returning the domain + rule type of the closest
example. It only fires when keyword scoring is weak, and degrades to keyword
overlap (then to nothing) if the embedding model or vector store is unavailable,
so the ladder never blocks the pipeline.
"""

import logging
from functools import lru_cache
from typing import Dict, Optional

from node1_intelligence.classifier import _taxonomy

logger = logging.getLogger("node1.semantic")

# Minimum hybrid score (0.7*semantic + 0.3*keyword) to trust a semantic match.
_SEMANTIC_FLOOR = 0.28


@lru_cache(maxsize=1)
def _store():
    """Build (once) a vector store of every taxonomy example, tagged with its
    domain + rule type. Returns None if the store can't be created (e.g. chromadb
    not installed) so the caller cleanly falls back to keyword-only."""
    try:
        from arc_vector import HybridVectorStore

        store = HybridVectorStore("rule_types")
    except Exception as exc:  # noqa: BLE001 — any failure disables the tier
        logger.warning("Semantic tier unavailable (%s); ladder uses keyword only.", exc)
        return None

    for dkey, ddef in _taxonomy()["domains"].items():
        for rtype, rdef in ddef.get("rule_types", {}).items():
            for i, example in enumerate(rdef.get("examples", [])):
                store.upsert(
                    f"{dkey}::{rtype}::{i}",
                    example,
                    {"domain": dkey, "ruleType": rtype},
                )
    return store


def semantic_rule_type(text: str) -> Optional[Dict]:
    """Closest taxonomy example by Hybrid Search.

    Returns {domain, ruleType, score, confidence} or None if nothing clears the
    floor / the tier is unavailable.
    """
    store = _store()
    if store is None:
        return None
    hit = store.best(text, threshold=_SEMANTIC_FLOOR, top_k=10)
    if not hit:
        return None
    return {
        "domain": hit.metadata.get("domain"),
        "ruleType": hit.metadata.get("ruleType"),
        "score": hit.score,
        "confidence": round(min(0.92, 0.45 + 0.5 * hit.score), 2),
    }
