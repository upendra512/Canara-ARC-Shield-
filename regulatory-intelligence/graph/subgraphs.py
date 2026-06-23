"""LangGraph subgraph scaffolds.

This module shows how the platform can be split into smaller graphs.
The functions are contracts only; extend them as you build each layer.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from classification.nodes import classification_node
from extraction.nodes import clause_extraction_node
from graph.nodes import intake_node, metadata_node, ocr_node, storage_node
from intelligence.nodes import (
    control_mapping_node,
    gap_analysis_node,
    policy_mapping_node,
    recommendation_node,
)
from obligations.nodes import obligation_extraction_node, risk_categorization_node
from retrieval.nodes import retrieval_node
from review.nodes import approval_workflow_node, final_repository_node, review_queue_node
from state.workflow import ComplianceState, IntakeState, ObligationState, ReviewState


def build_intake_subgraph() -> StateGraph[IntakeState]:
    """Build Layer 0 intake subgraph."""

    graph = StateGraph(IntakeState)
    graph.add_node("intake", intake_node)
    graph.add_node("ocr_parsing", ocr_node)
    graph.add_node("metadata_extraction", metadata_node)
    graph.add_node("document_storage", storage_node)
    graph.add_edge(START, "intake")
    graph.add_edge("intake", "ocr_parsing")
    graph.add_edge("ocr_parsing", "metadata_extraction")
    graph.add_edge("metadata_extraction", "document_storage")
    graph.add_edge("document_storage", END)
    return graph


def build_intelligence_subgraph() -> StateGraph[ObligationState]:
    """Build Layer 1 regulatory intelligence subgraph."""

    graph = StateGraph(ObligationState)
    graph.add_node("classification", classification_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("clause_extraction", clause_extraction_node)
    graph.add_node("obligation_extraction", obligation_extraction_node)
    graph.add_node("risk_categorization", risk_categorization_node)
    graph.add_edge(START, "classification")
    graph.add_edge("classification", "retrieval")
    graph.add_edge("retrieval", "clause_extraction")
    graph.add_edge("clause_extraction", "obligation_extraction")
    graph.add_edge("obligation_extraction", "risk_categorization")
    graph.add_edge("risk_categorization", END)
    return graph


def build_compliance_subgraph() -> StateGraph[ComplianceState]:
    """Build Layer 2 compliance intelligence subgraph."""

    graph = StateGraph(ComplianceState)
    graph.add_node("gap_analysis", gap_analysis_node)
    graph.add_node("policy_mapping", policy_mapping_node)
    graph.add_node("control_mapping", control_mapping_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_edge(START, "gap_analysis")
    graph.add_edge("gap_analysis", "policy_mapping")
    graph.add_edge("policy_mapping", "control_mapping")
    graph.add_edge("control_mapping", "recommendation")
    graph.add_edge("recommendation", END)
    return graph


def build_review_subgraph() -> StateGraph[ReviewState]:
    """Build Layer 3 human review subgraph."""

    graph = StateGraph(ReviewState)
    graph.add_node("review_queue", review_queue_node)
    graph.add_node("approval_workflow", approval_workflow_node)
    graph.add_node("final_repository", final_repository_node)
    graph.add_edge(START, "review_queue")
    graph.add_edge("review_queue", "approval_workflow")
    graph.add_edge("approval_workflow", "final_repository")
    graph.add_edge("final_repository", END)
    return graph
