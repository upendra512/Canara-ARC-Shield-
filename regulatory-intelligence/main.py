"""Entry point for the Regulatory Intelligence Layer 0 workflow.

Run this file to see the full LangGraph flow:

python main.py
"""

from __future__ import annotations

from graph.builder import build_layer0_graph


def main() -> None:
    """Build, compile, and run the Layer 0 graph."""

    # Step 1: Build the graph structure.
    graph_builder = build_layer0_graph()

    # Step 2: Compile the graph.
    # compile() prepares the graph so LangGraph can execute it.
    graph = graph_builder.compile()

    # Step 3: Create sample input.
    # This is the first state dictionary that enters the graph.
    sample_input = {
        "source": "rbi",
        "file_path": "data/input/sample-rbi-circular.txt",
        "raw_text": (
            "RBI/2024-25/123 Master Direction on KYC Compliance\n"
            "Date: 12 June 2026\n"
            "Banks and Asset Reconstruction Companies must strengthen KYC, "
            "AML monitoring, fraud reporting, and governance controls."
        ),
    }

    # Step 4: Run the graph.
    # invoke() sends the sample_input through every connected node.
    result = graph.invoke(sample_input)

    # Step 5: Print the final state after all nodes finish.
    print(result)


# This makes sure main() runs only when this file is executed directly.
# If another file imports main.py, this block will not run automatically.
if __name__ == "__main__":
    main()
