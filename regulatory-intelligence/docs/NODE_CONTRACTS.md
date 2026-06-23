# Node Contracts

## Layer 0: Regulatory Intake

### Intake

Purpose:
Validate the initial document request and identify the source.

Input State:
`source`, `file_path`.

Output State:
`status`, later `source_confidence`, `validation_confidence`.

Failure Modes:
Missing file, unsupported source, unsupported file type, duplicate document.

Retry Strategy:
Retry after correcting the input payload or file path.

Confidence Indicators:
Source confidence and validation confidence.

### OCR + Parsing

Purpose:
Extract text from offline documents.

Input State:
`file_path`, `source`.

Output State:
`raw_text`, extraction metadata, status.

Failure Modes:
File not found, scanned PDF without OCR, unsupported format, empty text.

Retry Strategy:
Retry after installing local OCR dependencies or improving parsing rules.

Confidence Indicators:
Extraction confidence and page coverage.

### Metadata Extraction

Purpose:
Extract searchable document metadata.

Input State:
`raw_text`, `source`.

Output State:
`metadata`, missing fields, confidence.

Failure Modes:
No date, no regulator, no circular number, conflicting metadata.

Retry Strategy:
Retry after improving extraction rules or adding manual corrections.

Confidence Indicators:
Metadata confidence and missing field list.

### Document Store

Purpose:
Persist the document record locally.

Input State:
`source`, `file_path`, `raw_text`, `metadata`.

Output State:
`document_id`, status.

Failure Modes:
Database unavailable, duplicate document, invalid schema.

Retry Strategy:
Retry after storage issue is corrected.

Confidence Indicators:
Read-after-write verification flag.

## Layer 1: Regulatory Intelligence Engine

### Classification Agent

Responsibilities:
Regulator detection, topic detection, department classification, circular
categorization.

Next step:
Start with rules. Add local model support only after rules are tested.

### Retrieval Agent

Responsibilities:
Retrieve historical circulars, related regulations, internal policies, and
compliance controls.

Next step:
Use local FAISS indexes and local embeddings.

### Clause Extraction Agent

Responsibilities:
Extract clauses, requirements, deadlines, and penalties.

Next step:
Start with explainable text parsing.

### Obligation Extraction Agent

Responsibilities:
Extract actionable obligations, compliance tasks, owners, and timelines.

Next step:
Define obligation schema before implementing extraction.

### Risk Categorization Agent

Responsibilities:
Classify high, medium, and low risk plus operational and regulatory impact.

Next step:
Create a transparent risk scoring rubric.

## Layer 2: Compliance Intelligence

Nodes:
Gap Analysis, Policy Mapping, Control Mapping, Recommendation.

Next step:
Implement only after obligations, controls, and policies have stable schemas.

## Layer 3: Human Review

Nodes:
Review Queue, Approval Workflow, Final Repository.

Next step:
Build reviewer workflows after core outputs are auditable.
