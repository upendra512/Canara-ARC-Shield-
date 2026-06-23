"""
Local embedding via Ollama. Pure stdlib HTTP — no extra deps beyond what the
nodes already have. Any failure returns None so callers degrade to keyword-only
search instead of breaking the pipeline.
"""

import json
import logging
import os
import urllib.error
import urllib.request
from functools import lru_cache
from typing import List, Optional

logger = logging.getLogger("arc_vector.embeddings")

_OLLAMA_URL = os.getenv("ARC_EMBED_URL", "http://localhost:11434/api/embeddings")
_MODEL = os.getenv("ARC_EMBED_MODEL", "nomic-embed-text")
_TIMEOUT = float(os.getenv("ARC_EMBED_TIMEOUT", "30"))


def embed(text: str) -> Optional[List[float]]:
    """Embed one piece of text. Returns the vector, or None if the model is
    unavailable (so the caller can fall back to keyword search)."""
    cleaned = (text or "").strip()
    if not cleaned:
        return None
    payload = json.dumps({"model": _MODEL, "prompt": cleaned}).encode("utf-8")
    req = urllib.request.Request(
        _OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            vector = json.loads(resp.read()).get("embedding")
        if isinstance(vector, list) and vector:
            return vector
        logger.warning("Embedding response had no vector; falling back to keyword search.")
        return None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        logger.warning("Embedding unavailable (%s); falling back to keyword search.", exc)
        return None


@lru_cache(maxsize=1)
def embedding_available() -> bool:
    """One-shot probe: is the embedding model reachable right now? Cached so a
    cold/absent Ollama is not re-probed on every clause."""
    return embed("healthcheck") is not None
