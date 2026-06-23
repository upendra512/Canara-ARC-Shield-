"""Compliance intelligence nodes for Layer 2."""

from __future__ import annotations

from typing import Any

from state.workflow import ComplianceState


def gap_analysis_node(state: ComplianceState) -> dict[str, Any]:
    """Compare obligations against available controls and policies."""

    obligations = state.get("obligations", [])
    controls = state.get("related_controls", [])
    gaps = []

    if len(controls) == 0:
        for obligation in obligations:
            gaps.append(
                {
                    "obligation_id": obligation.get("obligation_id", ""),
                    "gap_description": "No mapped control found.",
                    "severity": obligation.get("risk_category", "medium"),
                }
            )

    return {
        "compliance_gaps": gaps,
        "status": "gap_analysis_completed",
    }


def policy_mapping_node(state: ComplianceState) -> dict[str, Any]:
    """Map obligations to internal policy documents."""

    obligations = state.get("obligations", [])
    policies = state.get("related_policies", [])
    mappings = []

    for obligation in obligations:
        mappings.append(
            {
                "obligation_id": obligation.get("obligation_id", ""),
                "matched_policy_count": len(policies),
                "status": "mapped" if len(policies) > 0 else "not_mapped",
            }
        )

    return {
        "policy_mappings": mappings,
        "status": "policy_mapping_completed",
    }


def control_mapping_node(state: ComplianceState) -> dict[str, Any]:
    """Map obligations to internal compliance controls."""

    obligations = state.get("obligations", [])
    controls = state.get("related_controls", [])
    mappings = []

    for obligation in obligations:
        mappings.append(
            {
                "obligation_id": obligation.get("obligation_id", ""),
                "matched_control_count": len(controls),
                "status": "mapped" if len(controls) > 0 else "not_mapped",
            }
        )

    return {
        "control_mappings": mappings,
        "status": "control_mapping_completed",
    }


def recommendation_node(state: ComplianceState) -> dict[str, Any]:
    """Prepare remediation recommendations for human review."""

    gaps = state.get("compliance_gaps", [])
    recommendations = []

    for gap in gaps:
        recommendations.append(
            {
                "gap_id": gap.get("id", ""),
                "obligation_id": gap.get("obligation_id", ""),
                "recommendation": "Create or update a control and send for compliance review.",
                "priority": gap.get("severity", "medium"),
            }
        )

    return {
        "recommendations": recommendations,
        "status": "recommendation_completed",
    }
