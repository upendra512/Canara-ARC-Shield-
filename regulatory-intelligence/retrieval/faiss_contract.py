"""Local retrieval helpers.

The preferred path uses sentence-transformers and FAISS when both are installed.
The fallback path uses simple word overlap, so the project still runs offline
on a beginner machine without heavy dependencies installed.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any


INDEX_DIR = Path(__file__).resolve().parents[1] / "data" / "vector_indexes" / "faiss"
LEXICAL_INDEX_PATH = INDEX_DIR / "lexical_index.json"
FAISS_INDEX_PATH = INDEX_DIR / "documents.faiss"
METADATA_PATH = INDEX_DIR / "metadata.json"


def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into word chunks."""

    words = text.split()
    chunks = []

    for start in range(0, len(words), chunk_size):
        chunk_words = words[start : start + chunk_size]
        chunks.append(" ".join(chunk_words))

    return chunks


def tokenize(text: str) -> set[str]:
    """Create a lowercase token set for fallback lexical search."""

    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]+\b", text.lower())
    return set(words)


def lexical_score(query: str, text: str) -> float:
    """Score text by word overlap with the query."""

    query_tokens = tokenize(query)
    text_tokens = tokenize(text)

    if len(query_tokens) == 0 or len(text_tokens) == 0:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)
    return len(overlap) / math.sqrt(len(query_tokens) * len(text_tokens))


def build_lexical_index(documents: list[dict[str, Any]]) -> None:
    """Save a simple JSON index for offline fallback search."""

    entries = []

    for document in documents:
        document_id = str(document.get("document_id", ""))
        text = str(document.get("raw_text", ""))
        metadata = dict(document.get("metadata", {}))

        for chunk_number, chunk in enumerate(chunk_text(text)):
            entries.append(
                {
                    "document_id": document_id,
                    "chunk_number": chunk_number,
                    "text": chunk,
                    "metadata": metadata,
                }
            )

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    LEXICAL_INDEX_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def build_faiss_index(documents: list[dict[str, Any]]) -> bool:
    """Build FAISS index if local dependencies are installed."""

    try:
        import faiss  # type: ignore
        import numpy as np  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError:
        return False

    texts = []
    metadata_rows = []

    for document in documents:
        document_id = str(document.get("document_id", ""))
        text = str(document.get("raw_text", ""))
        metadata = dict(document.get("metadata", {}))

        for chunk_number, chunk in enumerate(chunk_text(text)):
            texts.append(chunk)
            metadata_rows.append(
                {
                    "document_id": document_id,
                    "chunk_number": chunk_number,
                    "text": chunk,
                    "metadata": metadata,
                }
            )

    if len(texts) == 0:
        return False

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, normalize_embeddings=True)
    vectors = np.array(embeddings, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(metadata_rows, indent=2), encoding="utf-8")

    return True


def build_local_index(documents: list[dict[str, Any]]) -> None:
    """Build a local retrieval index."""

    faiss_built = build_faiss_index(documents)

    if not faiss_built:
        build_lexical_index(documents)


def search_faiss_index(query: str, top_k: int) -> list[dict[str, Any]]:
    """Search FAISS index when dependencies and index files exist."""

    if not FAISS_INDEX_PATH.exists() or not METADATA_PATH.exists():
        return []

    try:
        import faiss  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError:
        return []

    index = faiss.read_index(str(FAISS_INDEX_PATH))
    metadata_rows = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_vector = model.encode([query], normalize_embeddings=True)
    scores, indexes = index.search(query_vector, top_k)
    results = []

    for score, row_index in zip(scores[0], indexes[0]):
        if row_index < 0:
            continue

        row = dict(metadata_rows[int(row_index)])
        row["score"] = float(score)
        results.append(row)

    return results


def search_lexical_index(query: str, top_k: int) -> list[dict[str, Any]]:
    """Search the JSON fallback index."""

    if not LEXICAL_INDEX_PATH.exists():
        return []

    entries = json.loads(LEXICAL_INDEX_PATH.read_text(encoding="utf-8"))
    scored_entries = []

    for entry in entries:
        score = lexical_score(query, str(entry.get("text", "")))
        if score > 0:
            result = dict(entry)
            result["score"] = score
            scored_entries.append(result)

    scored_entries.sort(key=lambda item: item["score"], reverse=True)
    return scored_entries[:top_k]


def search_local_index(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Search local FAISS first, then fallback lexical index."""

    query = query.strip()
    if query == "":
        return []

    faiss_results = search_faiss_index(query, top_k)
    if len(faiss_results) > 0:
        return faiss_results

    return search_lexical_index(query, top_k)
