import os
import sys
import json
import difflib
from typing import Dict, List, Set

# Add root folder to PYTHONPATH to allow relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from node2_map_engine.identifier import PolicyIdentifier
from node1_intelligence.extractor import _segments
from node1_intelligence.classifier import classify

DB_PATH = "/home/aarushi/Canara-ARC-Shield-/mock_db.json"
NEW_CIRCULAR_PATH = "/home/aarushi/Canara-ARC-Shield-/data/circulars/kyc_amended_2026.md"

def get_sentence_diff(old_text: str, new_text: str) -> List[str]:
    """Generates a list of differences between two strings at the sentence level."""
    from node2_map_engine.identifier import strip_markdown_headers
    old_clean = strip_markdown_headers(old_text)
    new_clean = strip_markdown_headers(new_text)
    
    old_sentences = [s.strip() + "." for s in old_clean.split(".") if s.strip()]
    new_sentences = [s.strip() + "." for s in new_clean.split(".") if s.strip()]
    
    diff = difflib.ndiff(old_sentences, new_sentences)
    return [line for line in diff if line.startswith("+ ") or line.startswith("- ")]

def main():
    print("=" * 80)
    print("KYC POLICY DIFF VIEW ENGINES (PROD-CHECK)")
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
        print("Please run 'compare_policies.py' or seed the policies first. Exiting.")
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

    # Initialize results
    results = {
        "UNCHANGED": [],
        "MODIFIED": [],
        "ADDED": [],
        "DELETED": []
    }

    # Step 4: Run 3-Signal matching
    identifier = PolicyIdentifier()
    for chunk in new_chunks:
        verdict = classify(chunk)
        section_title = verdict.get("regSection", "Other")
        
        match_res = identifier.identify(new_text=chunk, section_title=section_title)
        verdict_type = match_res["verdict"]

        if verdict_type in ["UNCHANGED", "MODIFIED"]:
            matched_clause = match_res["matched_clause"]
            matched_id = matched_clause.get("clause_id")
            
            if matched_id in active_baseline_ids:
                active_baseline_ids.remove(matched_id)

            if verdict_type == "UNCHANGED":
                results["UNCHANGED"].append({
                    "title": section_title
                })
            else:
                results["MODIFIED"].append({
                    "title": section_title,
                    "diff": get_sentence_diff(matched_clause.get("raw_text", ""), chunk)
                })
        else:
            if verdict["obligationBearing"]:
                results["ADDED"].append({
                    "title": section_title,
                    "text": chunk
                })

    # Step 5: Remaining baseline ids are DELETED
    for deleted_id in active_baseline_ids:
        clause = baseline_clauses[deleted_id]
        results["DELETED"].append({
            "title": clause["section_title"],
            "text": clause["raw_text"]
        })

    # Step 6: Print Change Results
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
        # Split into lines and print body text cleanly
        clean_lines = [l.strip() for l in sec["text"].split("\n") if l.strip() and not l.strip().startswith("#")]
        for l in clean_lines:
            print(f"      \033[92m+ {l}\033[0m")

    print(f"\n\033[91mDELETED REGULATORY OBLIGATIONS ({len(results['DELETED'])}):\033[0m")
    for sec in results["DELETED"]:
        print(f"  [-] {sec['title']}")
        clean_lines = [l.strip() for l in sec["text"].split("\n") if l.strip() and not l.strip().startswith("#")]
        for l in clean_lines:
            print(f"      \033[91m- {l}\033[0m")

    print("\n" + "=" * 80)
    print("END OF POLICY DIFF VIEW")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
