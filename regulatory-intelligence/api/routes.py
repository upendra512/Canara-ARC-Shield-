"""FastAPI routes for the offline regulatory platform."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from graph.builder import build_layer0_graph
from graph.subgraphs import (
    build_compliance_subgraph,
    build_intelligence_subgraph,
    build_review_subgraph,
)
from layer0.storage import STORAGE_DIR


router = APIRouter()


class IntakeRequest(BaseModel):
    """Request body for document intake."""

    source: str = "manual_upload"
    file_path: str = ""
    raw_text: str = ""


class ReviewDecisionRequest(BaseModel):
    """Request body for human review decisions."""

    reviewer_id: str
    decision: str
    comments: str = ""


def document_path(document_id: str) -> Path:
    """Return the local JSON path for a stored document."""

    return STORAGE_DIR / (document_id + ".json")


def load_document(document_id: str) -> dict[str, Any]:
    """Load one stored document from local JSON storage."""

    path = document_path(document_id)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    return json.loads(path.read_text(encoding="utf-8"))


@router.post("/documents/intake")
def create_document_intake(request: IntakeRequest) -> dict[str, Any]:
    """Submit a new offline document intake request."""

    graph = build_layer0_graph().compile()
    result = graph.invoke(request.model_dump())
    return result


@router.get("/documents/{document_id}")
def get_document(document_id: str) -> dict[str, Any]:
    """Fetch a stored regulatory document by id."""

    return load_document(document_id)


@router.post("/intelligence/{document_id}/run")
def run_intelligence(document_id: str) -> dict[str, Any]:
    """Run Layer 1 intelligence analysis for one document."""

    document = load_document(document_id)
    graph = build_intelligence_subgraph().compile()
    result = graph.invoke(document)
    return result


@router.post("/compliance/{document_id}/run")
def run_compliance(document_id: str) -> dict[str, Any]:
    """Run Layer 2 compliance intelligence for one document."""

    document = load_document(document_id)
    graph = build_compliance_subgraph().compile()
    result = graph.invoke(document)
    return result


@router.get("/review/queue")
def list_review_queue() -> dict[str, Any]:
    """List items waiting for compliance officer review."""

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    items = []

    for path in STORAGE_DIR.glob("*.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        items.append(
            {
                "document_id": document.get("document_id", ""),
                "title": document.get("metadata", {}).get("title", ""),
                "status": "pending_review",
            }
        )

    return {
        "items": items,
        "count": len(items),
    }


@router.post("/review/{item_id}/decision")
def submit_review_decision(
    item_id: str,
    request: ReviewDecisionRequest,
) -> dict[str, Any]:
    """Submit approval, rejection, or changes requested by a reviewer."""

    document = load_document(item_id)
    review_state = {
        **document,
        "reviewer_id": request.reviewer_id,
        "review_decision": request.decision,
        "review_comments": request.comments,
    }
    graph = build_review_subgraph().compile()
    result = graph.invoke(review_state)
    return result
