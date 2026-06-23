"""Layer 0 metadata extraction node."""

from __future__ import annotations

import re
from typing import Any

from graph.state import RegulatoryIntakeState


DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*"
    r"\s+\d{4})\b",
    re.IGNORECASE,
)
CIRCULAR_PATTERN = re.compile(
    r"\b(?:RBI|SEBI|IRDAI|IFSCA|NHB|PFRDA)[/-][A-Z0-9./-]+\b",
    re.IGNORECASE,
)
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


def first_non_empty_line(text: str) -> str:
    """Return a practical title from the first meaningful line."""

    for line in text.splitlines():
        cleaned = " ".join(line.split())
        if cleaned != "":
            return cleaned[:160]

    return "Untitled regulatory document"


def find_regulator(text: str) -> str:
    """Find the first known regulator in the text."""

    for regulator in REGULATORS:
        if re.search(r"\b" + regulator + r"\b", text, re.IGNORECASE):
            return regulator

    return ""


def find_topics(text: str) -> list[str]:
    """Find simple topic tags from keywords."""

    lower_text = text.lower()
    topics = []

    for keyword, topic in TOPIC_KEYWORDS.items():
        if re.search(r"\b" + re.escape(keyword) + r"\b", lower_text):
            topics.append(topic)

    return sorted(set(topics))


def calculate_metadata_confidence(metadata: dict[str, Any]) -> float:
    """Calculate a simple completeness score."""

    required_fields = ["title", "regulator", "circular_number", "issue_date"]
    found_count = 0

    for field in required_fields:
        if metadata.get(field, "") not in ("", None, []):
            found_count = found_count + 1

    return found_count / len(required_fields)


def metadata_node(state: RegulatoryIntakeState) -> dict[str, Any]:
    """Extract structured document metadata from raw text."""

    raw_text = state.get("raw_text", "")
    dates = DATE_PATTERN.findall(raw_text)
    circular_numbers = CIRCULAR_PATTERN.findall(raw_text)
    existing_metadata = dict(state.get("metadata", {}))

    if len(dates) > 0:
        issue_date = dates[0]
    else:
        issue_date = ""

    if len(circular_numbers) > 0:
        circular_number = circular_numbers[0].upper()
        document_type = "regulatory_circular"
    else:
        circular_number = ""
        document_type = "regulatory_document"

    metadata = {
        **existing_metadata,
        "title": first_non_empty_line(raw_text),
        "source": state.get("source", ""),
        "regulator": find_regulator(raw_text),
        "circular_number": circular_number,
        "issue_date": issue_date,
        "document_type": document_type,
        "topics": find_topics(raw_text),
        "word_count": len(re.findall(r"\b\w+\b", raw_text)),
    }
    metadata["confidence"] = calculate_metadata_confidence(metadata)

    confidence = dict(state.get("confidence", {}))
    confidence["metadata_confidence"] = metadata["confidence"]

    return {
        "metadata": metadata,
        "confidence": confidence,
        "status": "metadata_extracted",
    }
