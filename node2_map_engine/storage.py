import json
import logging
import os
from typing import Optional, Dict, Any

from arc_vector import HybridVectorStore

logger = logging.getLogger(__name__)

# A hybrid score at/above this means the incoming clause is a revision of a
# stored clause (so Node 2 diffs them) rather than a brand-new obligation.
_CLAUSE_MATCH_THRESHOLD = float(os.getenv("NODE2_CLAUSE_MATCH_THRESHOLD", "0.50"))


class StorageInterface:
    """
    Interface for data persistence.
    Locally, this reads and writes to a mock_db.json file. Historical clauses are
    also indexed in a persistent ChromaDB collection so a new clause can be
    matched to its prior version by semantic + keyword (hybrid) search.
    In production, this would implement SQLAlchemy for Postgres + the same store.
    """

    _vector_store: Optional[HybridVectorStore] = None
    _seeded = False

    def __init__(self, db_path: str = "mock_db.json"):
        self.db_path = db_path
        # Ensure the mock DB exists
        if not os.path.exists(self.db_path):
            logger.warning(f"{self.db_path} not found. Creating a blank mock database.")
            self._save_db({"clauses": {}, "compliance_maps": [], "human_review_queue": []})
        self._ensure_index()

    @classmethod
    def _store(cls) -> HybridVectorStore:
        if cls._vector_store is None:
            cls._vector_store = HybridVectorStore("clauses")
        return cls._vector_store

    def _ensure_index(self) -> None:
        """Seed the vector store from the historical clauses once per process."""
        if StorageInterface._seeded:
            return
        store = self._store()
        clauses = self._load_db().get("clauses", {})
        for clause in clauses.values():
            store.upsert(
                clause["clause_id"],
                clause.get("raw_text", ""),
                {
                    "domain": clause.get("domain", ""),
                    "section_title": clause.get("section_title", ""),
                },
            )
        StorageInterface._seeded = True
        logger.info("Indexed %d historical clauses into the vector store.", len(clauses))

    def _load_db(self) -> Dict[str, Any]:
        with open(self.db_path, "r") as f:
            return json.load(f)

    def _save_db(self, data: Dict[str, Any]):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

    def find_historical_clause(self, domain: str, section_title: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to find the old clause using exact metadata match (Postgres).
        """
        logger.info(f"Querying Mock DB for Domain: {domain}, Section: {section_title}")
        db = self._load_db()

        for clause in db.get("clauses", {}).values():
            if clause["domain"] == domain and clause["section_title"] == section_title:
                logger.info("Found historical clause via metadata match.")
                return clause

        return None

    def vector_search_clause(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Fallback: when the exact metadata match misses, find the prior version of
        this clause by Hybrid Search (semantic embedding + keyword overlap) over
        the indexed historical clauses. Returns the full clause record or None.
        """
        logger.info("Metadata match failed. Running hybrid vector search over historical clauses.")
        hit = self._store().best(text, threshold=_CLAUSE_MATCH_THRESHOLD)
        if not hit:
            logger.info("Vector search yielded no high-confidence results.")
            return None
        clause = self._load_db().get("clauses", {}).get(hit.id)
        if clause:
            logger.info(
                "Vector match: %s (score=%.3f semantic=%.3f keyword=%.3f)",
                hit.id, hit.score, hit.semantic, hit.keyword,
            )
        return clause


    def save_map(self, map_data: Dict[str, Any], requires_review: bool):
        """
        Saves the final generated MAP to the mock JSON DB.
        """
        db = self._load_db()
        
        target_table = "human_review_queue" if requires_review else "compliance_maps"
        logger.info(f"Saving MAP {map_data.get('map_id')} to table: {target_table}")
        
        # Append the new MAP to the appropriate list
        if target_table not in db:
            db[target_table] = []
            
        # Convert datetime objects to strings before saving to JSON
        import datetime
        for key, value in map_data.items():
            if isinstance(value, datetime.datetime):
                map_data[key] = value.isoformat()

        db[target_table].append(map_data)
        
        # Save the file
        self._save_db(db)
        logger.info("Mock DB successfully updated.")
