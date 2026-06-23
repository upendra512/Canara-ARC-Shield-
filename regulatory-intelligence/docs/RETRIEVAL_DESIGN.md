# Local Vector Search Design

The retrieval system must run offline.

Recommended stack:

- FAISS for vector search
- sentence-transformers with a local embedding model
- SQLite or PostgreSQL for metadata
- local disk for FAISS index files

## Chunking Strategy

Start simple:

1. Split by headings if available.
2. Fall back to paragraph chunks.
3. Keep chunk size around 300 to 800 words.
4. Store document id, page number, heading, regulator, topic, and date with each chunk.

## Embedding Workflow

1. Load local embedding model from disk.
2. Convert each chunk into an embedding.
3. Store embedding in FAISS.
4. Store chunk metadata in SQLite or PostgreSQL.
5. Save FAISS index locally.

## Metadata Filtering

Before vector search:

- filter by regulator
- filter by date range
- filter by document type
- filter by topic

After vector search:

- rerank by metadata match
- remove duplicates
- attach source citations

## Retrieval Pipeline

```text
query
  -> local embedding model
  -> FAISS search
  -> metadata filtering
  -> reranking
  -> related documents, policies, controls
```

Next step:
Implement retrieval only after chunk schema is stable.
