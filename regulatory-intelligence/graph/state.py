"""Shared workflow state for Layer 0: Regulatory Intake.

LangGraph passes one state dictionary through the workflow.

Each node reads values from the state.
Each node returns a small dictionary with updates.
LangGraph merges those updates into the main state.
"""

from typing import Any, TypedDict


class RegulatoryIntakeState(TypedDict, total=False):
    """The dictionary shape used by our graph.

    total=False means every field is optional.
    That is useful because the first input may only contain source/file_path,
    while later nodes add raw_text, metadata, and document_id.
    """

    # Where the document came from:
    # manual_upload, email, rbi_circular, web_url, etc.
    source: str

    # Local file path or URL for the document.
    file_path: str

    # Text extracted from the document.
    raw_text: str

    # Structured details extracted from raw_text.
    metadata: dict[str, Any]

    # Id created after storing the document.
    document_id: str

    # Simple workflow status after each node.
    status: str

    # Optional workflow diagnostics.
    errors: list[str]
    confidence: dict[str, float]

    # Optional Layer 1 outputs. Keeping these here lets the beginner demo graph
    # carry richer values without introducing a second state type immediately.
    chunks: list[dict[str, Any]]
    related_documents: list[dict[str, Any]]
    clauses: list[dict[str, Any]]
    deadlines: list[dict[str, Any]]
    penalties: list[dict[str, Any]]
    obligations: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
