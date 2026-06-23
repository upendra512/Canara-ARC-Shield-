"""Layer 0 document storage node."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from graph.state import RegulatoryIntakeState


STORAGE_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"


def build_document_id(state: RegulatoryIntakeState) -> str:
    """Create a stable local id from source, path, and text."""

    source = state.get("source", "")
    file_path = state.get("file_path", "")
    raw_text = state.get("raw_text", "")
    fingerprint = source + "|" + file_path + "|" + raw_text
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    return "DOC-" + digest[:12].upper()


def build_document_record(state: RegulatoryIntakeState, document_id: str) -> dict[str, Any]:
    """Build the JSON record saved by this beginner storage node."""

    return {
        "document_id": document_id,
        "source": state.get("source", ""),
        "file_path": state.get("file_path", ""),
        "raw_text": state.get("raw_text", ""),
        "metadata": state.get("metadata", {}),
        "confidence": state.get("confidence", {}),
        "errors": state.get("errors", []),
        "status": "stored",
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }


def storage_node(state: RegulatoryIntakeState) -> dict[str, Any]:
    """Persist the normalized document record as local JSON."""

    document_id = state.get("document_id", "")

    if document_id == "":
        document_id = build_document_id(state)

    record = build_document_record(state, document_id)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = STORAGE_DIR / (document_id + ".json")
    output_text = json.dumps(record, indent=2, sort_keys=True)
    output_path.write_text(output_text, encoding="utf-8")

    storage_verified = output_path.exists()
    confidence = dict(state.get("confidence", {}))

    if storage_verified:
        confidence["storage_confidence"] = 1.0
        status = "storage_completed"
    else:
        confidence["storage_confidence"] = 0.0
        status = "storage_failed"

    return {
        "document_id": document_id,
        "confidence": confidence,
        "status": status,
    }
