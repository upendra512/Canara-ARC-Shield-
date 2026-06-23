# Database Design

Use PostgreSQL for enterprise deployment or SQLite for local learning.

## Tables

Documents:
Stores one row per ingested document.

Document Metadata:
Stores extracted metadata such as regulator, circular number, issue date, and
confidence.

Clauses:
Stores extracted clauses linked to documents.

Obligations:
Stores actionable compliance obligations linked to clauses.

Controls:
Stores internal compliance controls.

Policies:
Stores internal policy documents.

Compliance Gaps:
Stores missing controls, policy gaps, and remediation needs.

Review Decisions:
Stores human approvals, rejections, and comments.

## Relationships

- `documents` has many `document_metadata`
- `documents` has many `clauses`
- `clauses` has many `obligations`
- `obligations` has many `compliance_gaps`
- `documents` has many `review_decisions`
- `controls` and `policies` are mapped to obligations through future mapping tables

## Index Strategy

Suggested indexes:

- `documents.source`
- `document_metadata.regulator`
- `document_metadata.circular_number`
- `clauses.document_id`
- `obligations.risk_level`
- `compliance_gaps.severity`
- `review_decisions.document_id`

See `storage/schema.sql` for the SQL scaffold.
