"""LangGraph builder for Layer 0: Regulatory Intake.

This file connects all node functions into one graph.

Our graph flow is:

START
  -> intake
  -> ocr_parsing
  -> metadata_extraction
  -> document_storage
END
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from graph.nodes import intake_node, metadata_node, ocr_node, storage_node
from graph.state import RegulatoryIntakeState


def build_layer0_graph() -> StateGraph[RegulatoryIntakeState]:
    """Create the Layer 0 LangGraph workflow.

    Important beginner idea:
        A LangGraph graph is made of nodes and edges.

    Node:
        A Python function that receives state and returns a state update.

    Edge:
        A connection that tells LangGraph which node runs next.
    """

    # StateGraph needs to know the state shape.
    # RegulatoryIntakeState is a TypedDict defined in graph/state.py.
    graph = StateGraph(RegulatoryIntakeState)

    # Add each Python function as a named graph node.
    # The first argument is the node name.
    # The second argument is the Python function to run.
    graph.add_node("intake", intake_node)
    graph.add_node("ocr_parsing", ocr_node)
    graph.add_node("metadata_extraction", metadata_node)
    graph.add_node("document_storage", storage_node)

    # START is a special LangGraph value.
    # It means "this is where the graph begins".
    graph.add_edge(START, "intake")

    # Each edge says what should happen after a node finishes.
    graph.add_edge("intake", "ocr_parsing")
    graph.add_edge("ocr_parsing", "metadata_extraction")
    graph.add_edge("metadata_extraction", "document_storage")

    # END is a special LangGraph value.
    # It means "the graph is finished".
    graph.add_edge("document_storage", END)

    # We return the graph builder.
    # The caller will run .compile() before invoking it.
    return graph
