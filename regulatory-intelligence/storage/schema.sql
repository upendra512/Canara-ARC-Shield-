-- Offline regulatory intelligence database schema scaffold.
-- This file is design-first. Add migrations later using Alembic or SQLModel.

CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    file_path TEXT NOT NULL,
    raw_text TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE document_metadata (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    regulator TEXT,
    circular_number TEXT,
    issue_date DATE,
    document_type TEXT,
    confidence REAL
);

CREATE TABLE clauses (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    clause_number TEXT,
    clause_text TEXT NOT NULL,
    page_number INTEGER,
    confidence REAL
);

CREATE TABLE obligations (
    id TEXT PRIMARY KEY,
    clause_id TEXT NOT NULL REFERENCES clauses(id),
    obligation_text TEXT NOT NULL,
    owner_department TEXT,
    due_date DATE,
    risk_level TEXT,
    confidence REAL
);

CREATE TABLE controls (
    id TEXT PRIMARY KEY,
    control_name TEXT NOT NULL,
    control_description TEXT,
    owner_department TEXT,
    status TEXT
);

CREATE TABLE policies (
    id TEXT PRIMARY KEY,
    policy_name TEXT NOT NULL,
    policy_text TEXT,
    owner_department TEXT,
    effective_date DATE
);

CREATE TABLE compliance_gaps (
    id TEXT PRIMARY KEY,
    obligation_id TEXT NOT NULL REFERENCES obligations(id),
    gap_description TEXT NOT NULL,
    severity TEXT,
    recommended_action TEXT,
    status TEXT
);

CREATE TABLE review_decisions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    comments TEXT,
    decided_at TIMESTAMP NOT NULL
);

-- Suggested indexes for local performance.
CREATE INDEX idx_documents_source ON documents(source);
CREATE INDEX idx_metadata_regulator ON document_metadata(regulator);
CREATE INDEX idx_metadata_circular_number ON document_metadata(circular_number);
CREATE INDEX idx_clauses_document_id ON clauses(document_id);
CREATE INDEX idx_obligations_risk_level ON obligations(risk_level);
CREATE INDEX idx_gaps_severity ON compliance_gaps(severity);
CREATE INDEX idx_review_decisions_document_id ON review_decisions(document_id);
