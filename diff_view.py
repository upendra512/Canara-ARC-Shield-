import os
import sys
import json

# Add root folder to PYTHONPATH to allow relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from node2_map_engine.identifier import PolicyIdentifier
from node1_intelligence.extractor import _segments
from compare_policies import Sha256HashingService, SentenceDiffService, PolicyComparisonEngine

DB_PATH = "/home/aarushi/Canara-ARC-Shield-/mock_db.json"
NEW_CIRCULAR_PATH = "/home/aarushi/Canara-ARC-Shield-/policies/kyc_amended.md"

def main():
    print("=" * 80)
    print("KYC POLICY DIFF VIEW ENGINES (PROD-CHECK - REUSED OOP SERVICES)")
    print("=" * 80)

    # Step 1: Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}. Please seed policies first.")
        sys.exit(1)

    # Step 2: Load DB and verify if old version (baseline SEED policies) exists
    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    baseline_clauses = db.get("clauses", {})
    active_baseline_ids = {
        cid for cid, clause in baseline_clauses.items()
        if clause.get("domain") == "KYC" and clause.get("source") == "SEED"
    }

    if not active_baseline_ids:
        print("\n\033[91m[WARNING] Old baseline KYC policies not found in database.\033[0m")
        print("This diff viewer requires the baseline version to be loaded in mock_db.json.")
        print("Please run 'compare_policies.py' first to initialize. Exiting.")
        sys.exit(0)

    print(f"\n[FOUND] Database contains {len(active_baseline_ids)} active baseline KYC sections.")
    print("Executing visual delta diff...")
    print("-" * 80)

    # Step 3: Parse and segment the amended 2026 circular
    if not os.path.exists(NEW_CIRCULAR_PATH):
        print(f"Error: Amended circular not found at {NEW_CIRCULAR_PATH}")
        sys.exit(1)

    with open(NEW_CIRCULAR_PATH, "r", encoding="utf-8") as f:
        new_text = f.read()

    new_chunks = _segments(new_text)

    # Step 4: Instantiate dependency-injected services and execute compare engine
    identifier = PolicyIdentifier()
    hashing_service = Sha256HashingService()
    diff_service = SentenceDiffService()

    engine = PolicyComparisonEngine(
        identifier=identifier,
        hashing_service=hashing_service,
        diff_service=diff_service
    )

    results = engine.compare(new_chunks, active_baseline_ids, baseline_clauses)

    # Step 5: Print Change Results
    print(f"\n\033[94mUNCHANGED REGULATORY OBLIGATIONS ({len(results['UNCHANGED'])}):\033[0m")
    for sec in results["UNCHANGED"]:
        print(f"  [ ] {sec['title']}")

    print(f"\n\033[93mMODIFIED REGULATORY OBLIGATIONS ({len(results['MODIFIED'])}):\033[0m")
    for sec in results["MODIFIED"]:
        print(f"  [*] {sec['title']}")
        for line in sec["diff"]:
            if line.startswith("+ "):
                print(f"      \033[92m{line}\033[0m")
            elif line.startswith("- "):
                print(f"      \033[91m{line}\033[0m")

    print(f"\n\033[92mADDED REGULATORY OBLIGATIONS ({len(results['ADDED'])}):\033[0m")
    for sec in results["ADDED"]:
        print(f"  [+] {sec['title']}")
        body_lines = [l.strip() for l in sec["text"].split("\n") if l.strip() and not l.strip().startswith("#")]
        for l in body_lines:
            print(f"      \033[92m+ {l}\033[0m")

    print(f"\n\033[91mDELETED REGULATORY OBLIGATIONS ({len(results['DELETED'])}):\033[0m")
    for sec in results["DELETED"]:
        print(f"  [-] {sec['title']}")
        body_lines = [l.strip() for l in sec["text"].split("\n") if l.strip() and not l.strip().startswith("#")]
        for l in body_lines:
            print(f"      \033[91m- {l}\033[0m")

    print("\n" + "=" * 80)
    print("END OF POLICY DIFF VIEW")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
