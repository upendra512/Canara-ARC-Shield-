"""Obligation extraction and risk nodes for Layer 1."""

from __future__ import annotations

import re
from typing import Any

from state.workflow import ObligationState


OBLIGATION_WORDS = ["must", "shall", "should", "required", "ensure", "submit", "report"]
OWNER_KEYWORDS = {
    "board": "Board",
    "compliance": "Compliance",
    "risk": "Risk",
    "it": "Information Technology",
    "cyber": "Information Security",
    "audit": "Internal Audit",
    "operations": "Operations",
}


def split_sentences(text: str) -> list[str]:
    """Split text into simple sentence-like pieces."""

    pieces = re.split(r"(?<=[.!?])\s+", text)
    sentences = []

    for piece in pieces:
        cleaned = " ".join(piece.split())
        if cleaned != "":
            sentences.append(cleaned)

    return sentences


def find_owner(text: str) -> str:
    """Guess owner department from keywords."""

    lower_text = text.lower()

    for keyword, owner in OWNER_KEYWORDS.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", lower_text):
            return owner

    return "Compliance"


def obligation_extraction_node(state: ObligationState) -> dict[str, Any]:
    """Extract actionable obligations from clauses."""

    clauses = state.get("clauses", [])
    obligations = []

    for clause in clauses:
        clause_text = str(clause.get("clause_text", ""))
        sentences = split_sentences(clause_text)

        for sentence in sentences:
            lower_sentence = sentence.lower()

            has_obligation_word = False
            for word in OBLIGATION_WORDS:
                if re.search(r"\b" + word + r"\b", lower_sentence):
                    has_obligation_word = True
                    break

            if has_obligation_word:
                obligation_number = len(obligations) + 1
                obligations.append(
                    {
                        "obligation_id": "OBL-" + str(obligation_number).zfill(4),
                        "clause_id": clause.get("clause_id", ""),
                        "obligation_text": sentence,
                        "owner": find_owner(sentence),
                        "confidence": 0.7,
                    }
                )

    owners = sorted(set(str(item.get("owner", "")) for item in obligations))

    if len(obligations) > 0:
        status = "obligation_extraction_completed"
        obligation_confidence = 0.7
    else:
        status = "obligation_extraction_no_obligations_found"
        obligation_confidence = 0.0

    return {
        "obligations": obligations,
        "owners": owners,
        "timelines": state.get("deadlines", []),
        "obligation_confidence": obligation_confidence,
        "status": status,
    }


def score_risk(obligation: dict[str, Any], penalties: list[dict[str, Any]]) -> str:
    """Assign a simple risk category."""

    text = str(obligation.get("obligation_text", "")).lower()
    clause_id = obligation.get("clause_id", "")
    penalty_clause_ids = {item.get("clause_id", "") for item in penalties}

    if clause_id in penalty_clause_ids:
        return "high"

    if "immediate" in text or "suspicious" in text or "fraud" in text:
        return "high"

    if "quarterly" in text or "review" in text or "report" in text:
        return "medium"

    return "low"


def risk_categorization_node(state: ObligationState) -> dict[str, Any]:
    """Categorize obligation risk as high, medium, or low."""

    obligations = list(state.get("obligations", []))
    penalties = state.get("penalties", [])

    for obligation in obligations:
        risk_category = score_risk(obligation, penalties)
        obligation["risk_category"] = risk_category

        if risk_category == "high":
            obligation["operational_impact"] = "Immediate process or control attention needed."
            obligation["regulatory_impact"] = "High regulatory scrutiny possible."
        elif risk_category == "medium":
            obligation["operational_impact"] = "Planned control update may be needed."
            obligation["regulatory_impact"] = "Moderate compliance impact."
        else:
            obligation["operational_impact"] = "Low operational impact."
            obligation["regulatory_impact"] = "Low regulatory impact."

    if len(obligations) > 0:
        risk_confidence = 0.7
    else:
        risk_confidence = 0.0

    return {
        "obligations": obligations,
        "risk_confidence": risk_confidence,
        "status": "risk_categorization_completed",
    }
