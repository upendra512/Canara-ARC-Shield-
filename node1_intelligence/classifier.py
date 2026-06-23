"""
Taxonomy-driven classification for Node 1.

Loads taxonomy.json (banking domains -> rule types -> keyword signatures) and
scores text against it. Pure and deterministic: the same text always yields the
same domain, rule type and obligation verdict, so the audit trail holds.
"""

import json
import os
import re
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

_TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "taxonomy.json")


@lru_cache(maxsize=1)
def _taxonomy() -> Dict:
    with open(_TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _hits(haystack: str, keywords: List[str]) -> int:
    return sum(1 for kw in keywords if kw in haystack)


def detect_regulator(text: str) -> str:
    """Highest keyword score wins; RBI is the default for unlabelled bank circulars."""
    hay = _norm(text)
    best, best_score = "RBI", 0
    for reg, keywords in _taxonomy()["regulators"].items():
        score = _hits(hay, keywords)
        if score > best_score:
            best, best_score = reg, score
    return best


def is_obligation(text: str) -> bool:
    hay = _norm(text)
    return any(term in hay for term in _taxonomy()["obligation_terms"])


def classify_domain(text: str) -> Tuple[str, Dict, int]:
    """Return (domain_key, domain_def, score). Falls back to the best partial match."""
    hay = _norm(text)
    domains = _taxonomy()["domains"]
    best_key, best_def, best_score = "reporting", domains["reporting"], 0
    for key, ddef in domains.items():
        score = _hits(hay, ddef["keywords"])
        if score > best_score:
            best_key, best_def, best_score = key, ddef, score
    return best_key, best_def, best_score


def classify_rule_type(text: str, domain_def: Dict) -> Tuple[Optional[str], float]:
    """Within a domain, pick the rule type with the most keyword hits."""
    hay = _norm(text)
    best_type: Optional[str] = None
    best_score = 0
    for rtype, rdef in domain_def.get("rule_types", {}).items():
        score = _hits(hay, rdef["keywords"])
        if score > best_score:
            best_type, best_score = rtype, score
    if best_type is None:
        return None, 0.0
    confidence = min(0.95, 0.55 + 0.15 * best_score)
    return best_type, round(confidence, 2)


def classify(text: str) -> Dict:
    """Full taxonomy verdict for one clause-sized piece of text."""
    domain_key, domain_def, domain_score = classify_domain(text)
    rule_type, rule_conf = classify_rule_type(text, domain_def)
    return {
        "domain": domain_key,
        "domainLabel": domain_def["label"],
        "regSection": domain_def["regSection"],
        "department": domain_def["department"],
        "ruleType": rule_type,
        "obligationBearing": is_obligation(text),
        "confidence": rule_conf if rule_type else (0.5 if domain_score else 0.3),
    }
