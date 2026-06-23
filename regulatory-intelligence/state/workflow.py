"""Enterprise state architecture for the offline regulatory platform.

These TypedDict classes describe how state evolves across LangGraph layers.
"""

from __future__ import annotations

from typing import Any, TypedDict


class IntakeState(TypedDict, total=False):
    """Layer 0 state produced by intake, OCR, metadata, and storage nodes."""

    source: str
    file_path: str
    raw_text: str
    metadata: dict[str, Any]
    document_id: str
    status: str
    stored_at: str
    errors: list[str]
    confidence: dict[str, float]


class ProcessingState(IntakeState, total=False):
    """Shared state after a document has entered the intelligence engine."""

    normalized_text: str
    chunks: list[dict[str, Any]]
    processing_notes: list[str]


class ClassificationState(ProcessingState, total=False):
    """State produced by the classification agent."""

    regulator: str
    topics: list[str]
    department: str
    circular_category: str
    classification_confidence: float


class RetrievalState(ClassificationState, total=False):
    """State produced by the retrieval agent."""

    related_documents: list[dict[str, Any]]
    related_policies: list[dict[str, Any]]
    related_controls: list[dict[str, Any]]
    retrieval_confidence: float


class ClauseState(RetrievalState, total=False):
    """State produced by the clause extraction agent."""

    clauses: list[dict[str, Any]]
    deadlines: list[dict[str, Any]]
    penalties: list[dict[str, Any]]
    clause_confidence: float


class ObligationState(ClauseState, total=False):
    """State produced by the obligation extraction agent."""

    obligations: list[dict[str, Any]]
    owners: list[str]
    timelines: list[dict[str, Any]]
    obligation_confidence: float
    risk_confidence: float


class ComplianceState(ObligationState, total=False):
    """State produced by the compliance intelligence layer."""

    policy_mappings: list[dict[str, Any]]
    control_mappings: list[dict[str, Any]]
    compliance_gaps: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    compliance_confidence: float


class ReviewState(ComplianceState, total=False):
    """State produced by the human review layer."""

    review_status: str
    reviewer_id: str
    review_decision: str
    review_comments: str
    final_repository_id: str
