"""Classification node for Layer 1.

This node uses simple offline keyword rules.
It can be replaced later with spaCy or a local model.
"""

from __future__ import annotations

import re
from typing import Any

from state.workflow import ClassificationState


REGULATORS = ["RBI", "SEBI", "IRDAI", "IFSCA", "NHB", "PFRDA"]
TOPIC_KEYWORDS = {
    "kyc": "kyc",
    "aml": "aml",
    "fraud": "fraud",
    "cyber": "cybersecurity",
    "asset reconstruction": "asset_reconstruction",
    "arc": "asset_reconstruction",
    "governance": "governance",
    "risk": "risk",
    "reporting": "reporting",
    "disclosure": "disclosure",
}
DEPARTMENT_KEYWORDS = {
    "kyc": "Compliance",
    "aml": "Compliance",
    "fraud": "Risk",
    "cyber": "Information Security",
    "reporting": "Regulatory Reporting",
    "governance": "Corporate Governance",
}


def detect_regulator(text: str, metadata: dict[str, Any]) -> str:
    """Find regulator from metadata first, then from text."""

    regulator_from_metadata = metadata.get("regulator", "")
    if regulator_from_metadata != "":
        return str(regulator_from_metadata)

    for regulator in REGULATORS:
        if re.search(r"\b" + regulator + r"\b", text, re.IGNORECASE):
            return regulator

    return ""


def detect_topics(text: str, metadata: dict[str, Any]) -> list[str]:
    """Find topics using metadata and keyword rules."""

    topics = list(metadata.get("topics", []))
    lower_text = text.lower()

    for keyword, topic in TOPIC_KEYWORDS.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", lower_text):
            topics.append(topic)

    return sorted(set(topics))


def detect_department(topics: list[str]) -> str:
    """Pick a likely owner department from detected topics."""

    for topic in topics:
        if topic in DEPARTMENT_KEYWORDS:
            return DEPARTMENT_KEYWORDS[topic]

    return "Compliance"


def detect_category(text: str, metadata: dict[str, Any]) -> str:
    """Decide the broad document category."""

    if metadata.get("document_type", "") != "":
        return str(metadata["document_type"])

    lower_text = text.lower()

    if "master direction" in lower_text:
        return "master_direction"

    if "circular" in lower_text:
        return "regulatory_circular"

    if "notification" in lower_text:
        return "notification"

    return "regulatory_document"


def classification_node(state: ClassificationState) -> dict[str, Any]:
    """Classify regulator, topic, department, and circular category."""

    raw_text = state.get("raw_text", "")
    metadata = dict(state.get("metadata", {}))
    regulator = detect_regulator(raw_text, metadata)
    topics = detect_topics(raw_text, metadata)
    department = detect_department(topics)
    category = detect_category(raw_text, metadata)

    score_parts = 0
    if regulator != "":
        score_parts = score_parts + 1
    if len(topics) > 0:
        score_parts = score_parts + 1
    if category != "":
        score_parts = score_parts + 1

    confidence = score_parts / 3

    return {
        "regulator": regulator,
        "topics": topics,
        "department": department,
        "circular_category": category,
        "classification_confidence": confidence,
        "status": "classification_completed",
    }
