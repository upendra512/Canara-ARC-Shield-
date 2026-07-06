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


# Below this rule-type confidence, Tier 1 is treated as weak/ambiguous and the
# semantic tier is consulted (no rule-type match, or a single lukewarm keyword).
_KEYWORD_TRUST = 0.80

# Below this confidence after Tier 1+2, the LLM tier (Tier 3) is consulted — but
# only if the LLM is configured. It is off by default, so this is normally inert.
_SEMANTIC_TRUST = 0.70


def classify(text: str, doc_domain_key: Optional[str] = None) -> Dict:
    """Full taxonomy verdict for one clause-sized piece of text.

    First tries the 3-Signal PolicyIdentifier. If a match is found (verdict is
    UNCHANGED, MODIFIED, or AMBIGUOUS), we inherit the domain and section title from
    the matched policy.
    Otherwise, runs the fallback taxonomy classification ladder (keyword, semantic, LLM).
    """
    try:
        from node2_map_engine.identifier import PolicyIdentifier
        identifier = PolicyIdentifier()
        # We extract a potential section title from the beginning of the text to help title matches
        first_line = text.split("\n")[0].strip()
        id_result = identifier.identify(new_text=text, section_title=first_line)
        
        if id_result["verdict"] in ["UNCHANGED", "MODIFIED"]:
            domain_key = id_result["domain"].lower()
            domains = _taxonomy()["domains"]
            domain_def = domains.get(domain_key, domains.get("kyc"))
            
            # Extract rule type based on matched section or keywords within the domain
            rule_type, rule_conf = classify_rule_type(text, domain_def)
            if not rule_type:
                rule_type = "IDENTITY_VERIFICATION"  # default rule type
                rule_conf = 0.95
                
            return {
                "domain": domain_key,
                "domainLabel": domain_def["label"],
                "regSection": id_result["matched_clause"].get("section_title", domain_def["regSection"]),
                "department": domain_def["department"],
                "ruleType": rule_type,
                "source": f"policy_db_match_{id_result['signal']}",
                "obligationBearing": True,
                "confidence": id_result["similarity"] if id_result["similarity"] > 0 else 0.95,
            }
    except Exception as e:
        logger.warning(f"PolicyIdentifier match failed in Node 1 ({e}). Falling back to standard classifier.")

    # FALLBACK: Original taxonomy classification ladder
    if doc_domain_key and doc_domain_key in _taxonomy()["domains"]:
        domain_key = doc_domain_key
        domain_def = _taxonomy()["domains"][domain_key]
        domain_score = 1
    else:
        domain_key, domain_def, domain_score = classify_domain(text)
        
    rule_type, rule_conf = classify_rule_type(text, domain_def)
    source = "keyword" if rule_type else "none"

    if rule_type is None or rule_conf < _KEYWORD_TRUST:
        semantic = _semantic_vote(text)
        if semantic and semantic.get("ruleType"):
            if rule_type is None or semantic["confidence"] >= rule_conf:
                rule_type = semantic["ruleType"]
                rule_conf = semantic["confidence"]
                source = "semantic"
                if domain_score == 0 and semantic.get("domain"):
                    domain_key = semantic["domain"]
                    domain_def = _taxonomy()["domains"].get(domain_key, domain_def)

    if rule_type is None or rule_conf < _SEMANTIC_TRUST:
        llm_pick = _llm_vote(text, domain_key, domain_def)
        if llm_pick and llm_pick.get("ruleType"):
            if rule_type is None or llm_pick["confidence"] >= rule_conf:
                rule_type = llm_pick["ruleType"]
                rule_conf = llm_pick["confidence"]
                source = "llm"
                if domain_score == 0 and llm_pick.get("domain"):
                    domain_key = llm_pick["domain"]
                    domain_def = _taxonomy()["domains"].get(domain_key, domain_def)

    return {
        "domain": domain_key,
        "domainLabel": domain_def["label"],
        "regSection": domain_def["regSection"],
        "department": domain_def["department"],
        "ruleType": rule_type,
        "source": source,
        "obligationBearing": is_obligation(text),
        "confidence": rule_conf if rule_type else (0.5 if domain_score else 0.3),
    }


def _semantic_vote(text: str):
    """Lazy bridge to Tier 2 (semantic.py). Imported here, not at module top, to
    avoid a circular import (semantic.py reads this module's taxonomy). Any failure
    returns None so the ladder degrades to the Tier 1 keyword verdict."""
    try:
        from node1_intelligence.semantic import semantic_rule_type

        return semantic_rule_type(text)
    except Exception:  # noqa: BLE001 — semantic tier is best-effort
        return None


def _llm_vote(text: str, domain_key: str, domain_def: Dict):
    """Lazy bridge to Tier 3 (llm.classify_rule). Off unless an LLM is configured.

    Candidates are the detected domain's rule types (keeps the prompt small and the
    pick inside the taxonomy). Any failure returns None so the ladder keeps the
    Tier 1/Tier 2 verdict."""
    try:
        from node1_intelligence import llm
        from node1_intelligence import config

        if not llm.enabled() or not config.llm_classify():
            return None
        candidates = [
            {"domain": domain_key, "ruleType": rtype}
            for rtype in domain_def.get("rule_types", {})
        ]
        return llm.classify_rule(text, candidates)
    except Exception:  # noqa: BLE001 — LLM tier is best-effort
        return None
