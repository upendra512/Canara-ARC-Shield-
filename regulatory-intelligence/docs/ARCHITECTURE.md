# Offline Regulatory Intelligence Platform Architecture

This project is an offline-first Regulatory Intelligence and Compliance
Analysis Platform for banking and compliance workflows.

## Critical Constraint

The platform must run completely offline.

Not allowed:

- OpenAI API
- Gemini API
- Claude API
- Azure OpenAI
- AWS Bedrock
- Anthropic
- External APIs
- Internet-dependent runtime calls
- Cloud services

Allowed:

- Python
- LangGraph
- FastAPI
- PostgreSQL or SQLite
- FAISS
- Chroma
- OCR libraries
- spaCy
- sentence-transformers with local models
- local LLMs hosted on the same machine
- Ollama or llama.cpp as optional local runtimes

## Folder Structure

```text
regulatory-intelligence/
  api/                 FastAPI route skeletons.
  classification/      Layer 1 classification node contracts.
  config/              Local-only configuration.
  docs/                Architecture and learning notes.
  extraction/          Clause extraction node contracts.
  graph/               LangGraph builders and graph wiring.
  intelligence/        Layer 2 compliance intelligence node contracts.
  layer0/              Intake, OCR, metadata, and storage node contracts.
  obligations/         Obligation and risk node contracts.
  prompts/             Local prompt templates only, if local LLMs are used.
  retrieval/           FAISS and local retrieval contracts.
  review/              Human review node contracts.
  schemas/             Stored document schemas.
  services/            Future local services, kept thin and explicit.
  state/               Enterprise state definitions.
  storage/             SQL schema and persistence contracts.
  tests/               Unit, node, graph, integration, and evaluation tests.
```

## LangGraph Architecture

The platform should be built as one main graph made from smaller subgraphs.

Main graph:

```text
START
  -> Intake Subgraph
  -> Intelligence Subgraph
  -> Compliance Subgraph
  -> Review Subgraph
END
```

Intake subgraph:

```text
START
  -> Intake
  -> OCR + Parsing
  -> Metadata Extraction
  -> Document Store
END
```

Intelligence subgraph:

```text
Document Store
  -> Classification Agent
  -> Retrieval Agent
  -> Clause Extraction Agent
  -> Obligation Extraction Agent
  -> Risk Categorization Agent
  -> Knowledge Store
```

Compliance subgraph:

```text
Knowledge Store
  -> Gap Analysis Agent
  -> Policy Mapping Agent
  -> Control Mapping Agent
  -> Recommendation Agent
```

Review subgraph:

```text
Compliance Officer
  -> Review Queue
  -> Approval Workflow
  -> Final Repository
```

## Node Contract Standard

Every node should document:

- Purpose
- Input State
- Output State
- Failure Modes
- Retry Strategy
- Confidence Indicators
- Implementation notes section

Keep early node code simple. Prefer readable Python over clever abstractions
while learning LangGraph.

## State Architecture

State evolves in layers:

1. `IntakeState`
2. `ProcessingState`
3. `ClassificationState`
4. `RetrievalState`
5. `ClauseState`
6. `ObligationState`
7. `ComplianceState`
8. `ReviewState`

See `state/workflow.py` for the scaffolded fields.

## Development Principle

Do not implement business logic too early.

First build:

- folders
- state types
- node contracts
- graph edges
- test skeletons
- database design
- retrieval design
- API route contracts

Then implement one node at a time and test it in isolation.
