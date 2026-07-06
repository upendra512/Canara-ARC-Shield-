import json
import logging
import os
import datetime
from typing import Optional, Dict, Any

from node2_map_engine.policy_retriever import PolicyRetriever, embed_text

logger = logging.getLogger(__name__)

# A similarity score at/above this means the incoming clause is a revision of a
# stored clause (so Node 2 diffs them) rather than a brand-new obligation.
_CLAUSE_MATCH_THRESHOLD = float(os.getenv("NODE2_CLAUSE_MATCH_THRESHOLD", "0.75"))


class StorageInterface:
    """
    Interface for data persistence.
    Locally, this reads and writes to a mock_db.json file.
    Uses PolicyRetriever for in-memory numpy cosine similarity search,
    removing ChromaDB and Docker dependency completely.
    """

    def __init__(self, db_path: str = "mock_db.json"):
        self.db_path = db_path
        self.retriever = PolicyRetriever(db_path=db_path)
        # Ensure the mock DB exists
        if not os.path.exists(self.db_path):
            logger.warning(f"{self.db_path} not found. Creating a blank mock database.")
            self._save_db({"clauses": {}, "compliance_maps": [], "human_review_queue": []})

    def _load_db(self) -> Dict[str, Any]:
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_db(self, data: Dict[str, Any]):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def find_historical_clause(
        self, domain: str, section_title: str, exclude_circular: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Attempts to find the old clause using exact metadata match.
        Skips clauses from `exclude_circular` so a circular never diffs against
        its own previously-stored clauses (which would happen on reprocessing).
        """
        logger.info(f"Querying Mock DB for Domain: {domain}, Section: {section_title}")
        db = self._load_db()

        for clause in db.get("clauses", {}).values():
            if exclude_circular and clause.get("circular_id") == exclude_circular:
                continue
            if clause.get("domain", "").upper() == domain.upper() and clause.get("section_title", "").lower() == section_title.lower():
                logger.info("Found historical clause via metadata match.")
                return clause

        return None

    def vector_search_clause(
        self, text: str, exclude_circular: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback: when the exact metadata match misses, find the prior version of
        this clause by in-memory numpy similarity search.
        """
        logger.info("Metadata match failed. Running in-memory vector search over historical clauses.")
        return self.retriever.find_best_match(
            text, threshold=_CLAUSE_MATCH_THRESHOLD, exclude_circular=exclude_circular
        )

    def save_historical_clause(self, clause_record: Dict[str, Any]) -> None:
        """
        Persists a processed clause into the database.
        Generates and saves the embedding as well so it can be vector searched.
        """
        db = self._load_db()
        clauses = db.setdefault("clauses", {})
        
        # Calculate embedding vector if not already present
        if "embedding" not in clause_record or clause_record["embedding"] is None:
            logger.info(f"Generating embedding for clause: {clause_record['clause_id']}")
            clause_record["embedding"] = embed_text(clause_record.get("raw_text", clause_record.get("text", "")))

        clauses[clause_record["clause_id"]] = clause_record
        self._save_db(db)
        logger.info("Stored historical clause %s in Mock DB.", clause_record["clause_id"])

    def save_map(self, map_data: Dict[str, Any], requires_review: bool):
        """
        Saves the final generated MAP to the mock JSON DB.
        """
        db = self._load_db()
        
        target_table = "human_review_queue" if requires_review else "compliance_maps"
        logger.info(f"Saving MAP {map_data.get('map_id')} to table: {target_table}")
        
        if target_table not in db:
            db[target_table] = []
            
        for key, value in map_data.items():
            if isinstance(value, datetime.datetime):
                map_data[key] = value.isoformat()

        db[target_table].append(map_data)
        self._save_db(db)
        logger.info("Mock DB successfully updated.")
