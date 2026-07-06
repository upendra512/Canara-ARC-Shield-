import os
import sys
import json
import logging
import asyncio
from datetime import datetime

# Add root folder to PYTHONPATH to allow relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from node2_map_engine.schemas import IncomingChunk
from node2_map_engine.workflow import run_map_engine
from node1_intelligence.extractor import _segments, extract_title, detect_regulator, extract_issued_date
from node1_intelligence.classifier import classify

# Set logging levels to clean stdout output
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("test_md_ingestion")

DB_PATH = "/home/aarushi/Canara-ARC-Shield-/mock_db.json"

def clean_previous_runs():
    """Removes previously generated test circular mappings from mock_db.json."""
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            
            # Filter out any clauses from previous test runs
            clauses = db.get("clauses", {})
            initial_count = len(clauses)
            cleaned_clauses = {
                k: v for k, v in clauses.items()
                if not (v.get("circular_id", "").startswith("RBI/TEST") or v.get("circular_id") == "RBI/2026-27/115")
            }
            db["clauses"] = cleaned_clauses
            
            # Filter out test compliance maps
            db["compliance_maps"] = [
                m for m in db.get("compliance_maps", [])
                if not (m.get("source_circular", "").startswith("RBI/TEST") or m.get("source_circular") == "RBI/2026-27/115")
            ]
            
            db["human_review_queue"] = [
                m for m in db.get("human_review_queue", [])
                if not (m.get("source_circular", "").startswith("RBI/TEST") or m.get("source_circular") == "RBI/2026-27/115")
            ]

            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            
            removed = initial_count - len(cleaned_clauses)
            if removed > 0:
                print(f"Cleaned {removed} old test clauses and maps from mock database.")
        except Exception as e:
            print(f"Warning: Could not clean DB: {e}")

async def test_circular_md(file_path: str):
    print("=" * 80)
    print(f"TESTING FILE: {os.path.basename(file_path)}")
    print("=" * 80)

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Parse metadata as Node 1 does
    title = extract_title(text, os.path.basename(file_path))
    regulator = detect_regulator(text)
    issued_date = extract_issued_date(text)
    circular_id = "RBI/2026-27/115"

    print(f"Derived Title : {title}")
    print(f"Regulator     : {regulator}")
    print(f"Issued Date   : {issued_date}")
    print(f"Circular ID   : {circular_id}")
    print("-" * 80)

    # Segment text into chunks
    chunks = _segments(text)
    print(f"Extracted {len(chunks)} text chunks to evaluate.")

    # Process each chunk through our pipeline
    for i, chunk_text in enumerate(chunks):
        # We only care about obligation-bearing chunks (skip header / signature blocks)
        verdict = classify(chunk_text)
        if not verdict["obligationBearing"]:
            continue

        print(f"\nEvaluating Obligation Chunk #{i+1}...")
        
        # Build incoming chunk schema
        chunk = IncomingChunk(
            circular_id=circular_id,
            circular_date=issued_date or "",
            regulator=regulator,
            domain="UNKNOWN",
            section_title=verdict.get("regSection", "Other"),
            chunk_text=chunk_text,
            chunk_index=i,
            chunk_hash=f"hash_test_md_{i}"
        )

        # Run Node 2 Map Engine
        # Set USE_MOCK_LLM to run offline
        os.environ["USE_MOCK_LLM"] = "true"
        await run_map_engine(chunk)

    print("\n" + "=" * 80 + "\n")

async def main():
    multi_section_md = "/home/aarushi/Canara-ARC-Shield-/data/circulars/rbi_kyc_cyber_circular_2026.md"

    # Clean database before running
    clean_previous_runs()

    print("STARTING TEST ON MULTI-SECTION RBI CIRCULAR MARKDOWN FILE...\n")
    
    # Run Scenario: Multi-section circular
    await test_circular_md(multi_section_md)

if __name__ == "__main__":
    asyncio.run(main())
