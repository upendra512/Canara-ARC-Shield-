# Testing Scaffold

This folder is intentionally organized before tests are implemented.

- `unit/`: small pure Python tests for helper functions.
- `nodes/`: one test file per LangGraph node contract.
- `graphs/`: tests that compile and invoke subgraphs.
- `integration/`: tests for local database, FAISS, OCR, and API wiring.
- `evaluation/`: quality checks for extraction, retrieval, and recommendations.

Next step:

- Add a tiny sample RBI circular text fixture.
- Add one compile test for every subgraph.
- Add one contract test for every node.
