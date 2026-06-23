"""Clause extraction node for Layer 1."""

from __future__ import annotations

import re
from typing import Any

from state.workflow import ClauseState


DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*"
    r"\s+\d{4})\b",
    re.IGNORECASE,
)
PENALTY_WORDS = ["penalty", "penalties", "fine", "liable", "violation", "non-compliance"]


def split_into_clauses(raw_text: str) -> list[dict[str, Any]]:
    """Split text into simple clause records."""

    paragraphs = []

    for block in raw_text.split("\n"):
        cleaned = " ".join(block.split())
        if cleaned != "":
            paragraphs.append(cleaned)

    clauses = []

    for index, paragraph in enumerate(paragraphs, start=1):
        clause_number_match = re.match(r"^(\d+(?:\.\d+)*)", paragraph)

        if clause_number_match is not None:
            clause_number = clause_number_match.group(1)
        else:
            clause_number = str(index)

        clauses.append(
            {
                "clause_id": "CLAUSE-" + str(index).zfill(4),
                "clause_number": clause_number,
                "clause_text": paragraph,
                "confidence": 0.7,
            }
        )

    return clauses


def extract_deadlines(clauses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find dates inside clauses."""

    deadlines = []

    for clause in clauses:
        dates = DATE_PATTERN.findall(str(clause.get("clause_text", "")))

        for date_text in dates:
            deadlines.append(
                {
                    "clause_id": clause.get("clause_id", ""),
                    "deadline_text": date_text,
                    "confidence": 0.8,
                }
            )

    return deadlines


def extract_penalties(clauses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find clauses that mention penalties or non-compliance."""

    penalties = []

    for clause in clauses:
        clause_text = str(clause.get("clause_text", ""))
        lower_text = clause_text.lower()

        for word in PENALTY_WORDS:
            if word in lower_text:
                penalties.append(
                    {
                        "clause_id": clause.get("clause_id", ""),
                        "penalty_text": clause_text,
                        "matched_word": word,
                        "confidence": 0.7,
                    }
                )
                break

    return penalties


def clause_extraction_node(state: ClauseState) -> dict[str, Any]:
    """Extract clauses, requirements, deadlines, and penalties."""

    raw_text = state.get("raw_text", "")
    clauses = split_into_clauses(raw_text)
    deadlines = extract_deadlines(clauses)
    penalties = extract_penalties(clauses)

    if len(clauses) > 0:
        status = "clause_extraction_completed"
        clause_confidence = 0.7
    else:
        status = "clause_extraction_no_text"
        clause_confidence = 0.0

    return {
        "clauses": clauses,
        "deadlines": deadlines,
        "penalties": penalties,
        "clause_confidence": clause_confidence,
        "status": status,
    }
