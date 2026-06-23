"""
Shared embedding + vector-store layer for ARC Shield.

Both Node 1 (circular-level similarity) and Node 2 (clause-level retrieval for
diffing) need the same capability: turn regulatory text into a vector with a
local embedding model and run semantic search over a persistent vector DB. This
package is that single implementation, imported by both nodes (PYTHONPATH = repo
root), so neither reimplements it.

Design:
  - Embeddings come from a local Ollama model (nomic-embed-text by default) over
    its HTTP API. No cloud, no API key. If Ollama is unreachable, embedding
    returns None and callers fall back to keyword-only search, so the pipeline
    never blocks on the model.
  - Vectors live in ChromaDB (persistent, cosine space). Each logical collection
    gets its own on-disk directory, so Node 1 and Node 2 — separate OS processes
    — never contend on one SQLite file.
  - Retrieval is Hybrid Search: semantic cosine similarity blended with keyword
    overlap, matching the product design (vector + keyword, best-of-N).
"""

from arc_vector.embeddings import embed, embedding_available
from arc_vector.store import HybridVectorStore, HybridHit

__all__ = ["embed", "embedding_available", "HybridVectorStore", "HybridHit"]
