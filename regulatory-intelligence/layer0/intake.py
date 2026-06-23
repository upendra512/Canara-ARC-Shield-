"""Layer 0 intake node.

This node performs the first basic checks on a document request.

Everything here is offline and beginner friendly:
1. Clean the source name.
2. Check whether the input has a file path or raw text.
3. Guess source from the file path when needed.
4. Return a small state update for LangGraph.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from graph.state import RegulatoryIntakeState


SOURCE_ALIASES = {
    "email": "email",
    "mail": "email",
    "manual": "manual_upload",
    "manual_upload": "manual_upload",
    "upload": "manual_upload",
    "rbi": "rbi_circular",
    "rbi_circular": "rbi_circular",
    "url": "web_url",
    "web": "web_url",
    "web_url": "web_url",
}

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".json", ".csv", ".xml", ".html", ".eml"}


def normalize_source(source: str) -> str:
    """Convert user input into one standard source name."""

    cleaned_source = source.strip().lower()
    cleaned_source = cleaned_source.replace("-", "_")
    cleaned_source = cleaned_source.replace(" ", "_")

    if cleaned_source in SOURCE_ALIASES:
        return SOURCE_ALIASES[cleaned_source]

    if cleaned_source == "":
        return "manual_upload"

    return cleaned_source


def guess_source_from_path(file_path: str) -> str:
    """Guess source when the caller did not give one."""

    lower_path = file_path.lower()

    if lower_path.startswith("http://") or lower_path.startswith("https://"):
        return "web_url"

    if "rbi" in lower_path:
        return "rbi_circular"

    if lower_path.endswith(".eml") or "email" in lower_path:
        return "email"

    return "manual_upload"


def calculate_file_hash(path: Path) -> str:
    """Create a SHA-256 hash for duplicate detection."""

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        while True:
            chunk = file.read(1024 * 1024)
            if chunk == b"":
                break
            sha256.update(chunk)

    return sha256.hexdigest()


def intake_node(state: RegulatoryIntakeState) -> dict[str, Any]:
    """Accept the first document payload and prepare it for OCR/parsing."""

    file_path = state.get("file_path", "").strip()
    raw_text = state.get("raw_text", "").strip()
    source = state.get("source", "").strip()
    errors = []
    confidence = {}
    metadata = dict(state.get("metadata", {}))

    if source != "":
        normalized_source = normalize_source(source)
        confidence["source_confidence"] = 1.0
    else:
        normalized_source = guess_source_from_path(file_path)
        confidence["source_confidence"] = 0.6

    if file_path == "" and raw_text == "":
        errors.append("Either file_path or raw_text is required.")

    normalized_file_path = ""
    if file_path != "":
        path = Path(file_path)
        normalized_file_path = str(path)
        extension = path.suffix.lower()

        if extension != "" and extension not in ALLOWED_EXTENSIONS:
            errors.append("Unsupported file type: " + extension)

        if path.exists() and path.is_file():
            metadata["document_hash"] = calculate_file_hash(path)
            confidence["validation_confidence"] = 1.0
        elif raw_text != "":
            confidence["validation_confidence"] = 0.7
        else:
            errors.append("File was not found at file_path.")
            confidence["validation_confidence"] = 0.2
    elif raw_text != "":
        confidence["validation_confidence"] = 0.8

    if len(errors) == 0:
        status = "intake_received"
    else:
        status = "intake_validation_failed"

    return {
        "source": normalized_source,
        "file_path": normalized_file_path,
        "metadata": metadata,
        "errors": errors,
        "confidence": confidence,
        "status": status,
    }
