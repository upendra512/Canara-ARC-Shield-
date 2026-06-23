# Testing Strategy

## Unit Tests

Purpose:
Test small pure Python functions.

Examples:

- source normalization
- date parsing
- document id creation
- chunk splitting

## Node Tests

Purpose:
Test one LangGraph node at a time.

Each node test should check:

- input state
- output state
- status
- confidence fields
- failure behavior

## Graph Tests

Purpose:
Test that each subgraph compiles and runs with minimal state.

Graphs:

- Intake subgraph
- Intelligence subgraph
- Compliance subgraph
- Review subgraph
- Main graph

## Integration Tests

Purpose:
Test local components together.

Examples:

- OCR plus metadata extraction
- database write and read
- FAISS build and search
- FastAPI route calling a graph

## Evaluation Tests

Purpose:
Measure quality, not just correctness.

Examples:

- clause extraction accuracy
- obligation extraction precision
- retrieval recall
- recommendation usefulness

Start evaluation with small manually labeled examples.
