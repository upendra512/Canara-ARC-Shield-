import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("node2.policy_retriever")

# Fallback embedding dimension
_EMBED_DIM = 384  # all-MiniLM-L6-v2 uses 384 dimensions; nomic-embed-text uses 768

class EmbeddingModelLoader:
    """Lazy-loader for embedding models to avoid load time overhead when not needed."""
    _model = None
    _tried_load = False

    @classmethod
    def get_model(cls):
        if not cls._tried_load:
            cls._tried_load = True
            try:
                from sentence_transformers import SentenceTransformer
                logger.info("Loading sentence-transformers offline model 'all-MiniLM-L6-v2'...")
                # This will load the model offline if already downloaded, or download it once
                cls._model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("sentence-transformers offline model loaded successfully.")
            except ImportError:
                logger.warning("sentence-transformers package not installed. Will use Ollama fallback.")
            except Exception as e:
                logger.warning(f"Failed to load sentence-transformers model: {e}. Will use Ollama fallback.")
        return cls._model

def embed_text(text: str) -> Optional[List[float]]:
    """
    Computes embedding for a piece of text.
    First tries sentence-transformers offline model.
    Falls back to Ollama embeddings.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return None

    # Try sentence-transformers first
    model = EmbeddingModelLoader.get_model()
    if model is not None:
        try:
            vector = model.encode(cleaned)
            return [float(x) for x in vector]
        except Exception as e:
            logger.warning(f"Offline sentence-transformers embedding failed: {e}. Trying Ollama fallback.")

    # Fallback: Ollama embeddings (HTTP call)
    import urllib.request
    import urllib.error
    
    ollama_url = os.getenv("ARC_EMBED_URL", "http://localhost:11434/api/embeddings")
    model_name = os.getenv("ARC_EMBED_MODEL", "nomic-embed-text")
    timeout = float(os.getenv("ARC_EMBED_TIMEOUT", "10"))
    
    payload = json.dumps({"model": model_name, "prompt": cleaned}).encode("utf-8")
    req = urllib.request.Request(
        ollama_url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            vector = json.loads(resp.read()).get("embedding")
        if isinstance(vector, list) and vector:
            return [float(x) for x in vector]
    except Exception as exc:
        logger.warning(f"Ollama embedding fallback failed: {exc}")
    
    return None

def compute_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Pure Python/Numpy cosine similarity computation."""
    import numpy as np
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

class PolicyRetriever:
    """
    Handles retrieving the best matching historical policy clause using
    in-memory numpy cosine similarity, making it fully offline and self-contained.
    """
    def __init__(self, db_path: str = "mock_db.json"):
        self.db_path = db_path

    def _load_clauses(self) -> List[Dict]:
        """Loads all clauses from mock_db.json."""
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "r") as f:
                data = json.load(f)
                return list(data.get("clauses", {}).values())
        except Exception as e:
            logger.error(f"Error loading clauses from mock DB: {e}")
            return []

    def find_best_match(self, new_text: str, threshold: float = 0.75, exclude_circular: Optional[str] = None) -> Optional[Dict]:
        """
        Embeds the new text and finds the closest matching policy section in the database.
        Returns the matched policy dict, or None if similarity is below the threshold.
        """
        new_emb = embed_text(new_text)
        clauses = self._load_clauses()
        
        # Exclude same circular clauses
        if exclude_circular:
            clauses = [c for c in clauses if c.get("circular_id") != exclude_circular]

        if not clauses:
            logger.info("No policy clauses in database to compare against.")
            return None

        # Filter clauses that have precomputed embeddings
        clauses_with_emb = [c for c in clauses if c.get("embedding") is not None]

        if new_emb is not None and clauses_with_emb:
            logger.info(f"Running numpy cosine similarity over {len(clauses_with_emb)} clauses...")
            best_clause = None
            best_sim = -1.0
            
            import numpy as np
            # Stack all embeddings for vectorised similarity search
            old_embs = np.array([c["embedding"] for c in clauses_with_emb])
            query_emb = np.array(new_emb)
            
            # Compute similarities
            norms = np.linalg.norm(old_embs, axis=1) * np.linalg.norm(query_emb)
            norms[norms == 0] = 1e-9  # avoid division by zero
            sims = np.dot(old_embs, query_emb) / norms
            
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            
            logger.info(f"Vector search closest match similarity: {best_sim:.4f}")
            if best_sim >= threshold:
                matched = clauses_with_emb[best_idx]
                logger.info(f"Match found: '{matched.get('section_title')}' (Domain: {matched.get('domain')}, Sim: {best_sim:.4f})")
                # Return copies with added similarity score info
                result = dict(matched)
                result["similarity"] = best_sim
                return result

        # Fallback 1: difflib text ratio matching (if embedding fails or no embeddings stored)
        logger.info("Vector search did not yield a match. Running fallback string similarity search...")
        best_clause = None
        best_ratio = -1.0
        import difflib
        
        for clause in clauses:
            ratio = difflib.SequenceMatcher(None, new_text, clause.get("raw_text", "")).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_clause = clause

        logger.info(f"String matching closest match ratio: {best_ratio:.4f}")
        # String match threshold can be lower (e.g. 0.60) since it is text overlap
        if best_ratio >= 0.60:
            result = dict(best_clause)
            result["similarity"] = best_ratio
            return result

        logger.info("No matching policy found in database. Treating as brand new policy (ADDED).")
        return None
