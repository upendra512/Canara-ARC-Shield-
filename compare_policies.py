import os
import sys
import json
import logging
import difflib
from typing import Dict, List, Set, Any

# Add root folder to PYTHONPATH to allow relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from node2_map_engine.seed_policies import seed_database
from node2_map_engine.identifier import PolicyIdentifier
from node1_intelligence.extractor import _segments
from node1_intelligence.classifier import classify

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("compare_policies")

# File paths
BASE_DIR = "/home/aarushi/Canara-ARC-Shield-"
OLD_POLICY_PATH = os.path.join(BASE_DIR, "data/policies/kyc.md")
NEW_CIRCULAR_PATH = os.path.join(BASE_DIR, "data/circulars/kyc_amended_2026.md")
DB_PATH = os.path.join(BASE_DIR, "mock_db.json")
REPORT_PATH = "/home/aarushi/.gemini/antigravity-cli/brain/73d0ac8e-63af-4cf7-bc84-cea4f389afb8/kyc_policy_comparison_report.md"

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
    print("STARTING KYC POLICY COMPARISON WORKFLOW")
    print("=" * 80)

    # Clean DB completely before seeding to prevent leftover garbage and namespace collisions
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            # Remove ALL clauses and maps to ensure a clean comparison run
            db["clauses"] = {}
            db["compliance_maps"] = []
            db["human_review_queue"] = []
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            print("Cleared database clauses and maps for a clean comparison run.")
        except Exception as e:
            print(f"Warning: Could not clear DB: {e}")

    # Step 1: Seed the database with the baseline kyc.md policy
    print("\n[STEP 1] Seeding baseline policies into the database...")
    seed_database()

    # Step 2: Load the baseline database to track active clauses
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    # Collect all seeded KYC baseline clause IDs
    baseline_clauses = db.get("clauses", {})
    active_baseline_ids: Set[str] = {
        cid for cid, clause in baseline_clauses.items()
        if clause.get("domain") == "KYC" and clause.get("source") == "SEED"
    }
    
    print(f"Loaded {len(active_baseline_ids)} baseline KYC policies from DB:")
    for cid in sorted(active_baseline_ids):
        print(f" - {baseline_clauses[cid]['section_title']}")

    # Step 3: Parse and segment the amended 2026 circular
    print(f"\n[STEP 2] Reading amended policy file: {os.path.basename(NEW_CIRCULAR_PATH)}...")
    if not os.path.exists(NEW_CIRCULAR_PATH):
        print(f"Error: File not found at {NEW_CIRCULAR_PATH}")
        return

    with open(NEW_CIRCULAR_PATH, "r", encoding="utf-8") as f:
        new_text = f.read()

    new_chunks = _segments(new_text)
    print(f"Segmented amended document into {len(new_chunks)} section chunks.")

    # Initialize comparison results
    results = {
        "UNCHANGED": [],
        "MODIFIED": [],
        "ADDED": [],
        "DELETED": []
    }

    # Step 4: Run the matching engine for each new chunk
    print("\n[STEP 3] Comparing amended chunks against baseline...")
    identifier = PolicyIdentifier()

    for idx, chunk in enumerate(new_chunks):
        # Classify chunk in Node 1 to extract domain & section title metadata
        verdict = classify(chunk)
        
        # Determine the section title for matching
        section_title = verdict.get("regSection", "Other")
        
        # Identify using the 3-Signal cascade
        match_res = identifier.identify(new_text=chunk, section_title=section_title)
        verdict_type = match_res["verdict"]

        if verdict_type in ["UNCHANGED", "MODIFIED"]:
            matched_clause = match_res["matched_clause"]
            matched_id = matched_clause.get("clause_id")
            
            # Remove from active baseline set to mark as "retained"
            if matched_id in active_baseline_ids:
                active_baseline_ids.remove(matched_id)

            if verdict_type == "UNCHANGED":
                results["UNCHANGED"].append({
                    "title": section_title,
                    "text": chunk
                })
            else:  # MODIFIED
                results["MODIFIED"].append({
                    "title": section_title,
                    "old_text": matched_clause.get("raw_text", ""),
                    "new_text": chunk,
                    "diff": get_sentence_diff(matched_clause.get("raw_text", ""), chunk)
                })
        else:
            # Check if this is actually just header/footer metadata (skip if not obligation-bearing)
            if verdict["obligationBearing"]:
                results["ADDED"].append({
                    "title": section_title,
                    "text": chunk
                })

    # Step 5: Any remaining active baseline IDs were DELETED
    print("\n[STEP 4] Identifying deleted sections...")
    for deleted_id in active_baseline_ids:
        clause = baseline_clauses[deleted_id]
        results["DELETED"].append({
            "title": clause["section_title"],
            "text": clause["raw_text"]
        })

    # Step 6: Print terminal summary & write Markdown Artifact report
    print("\n" + "=" * 80)
    print("POLICY COMPARISON SUMMARY")
    print("=" * 80)
    
    print(f"\033[94mUNCHANGED: {len(results['UNCHANGED'])} sections\033[0m")
    for sec in results["UNCHANGED"]:
        print(f"  • {sec['title']}")

    print(f"\n\033[93mMODIFIED: {len(results['MODIFIED'])} sections\033[0m")
    for sec in results["MODIFIED"]:
        print(f"  • {sec['title']}")
        for line in sec["diff"]:
            if line.startswith("+ "):
                print(f"    \033[92m{line}\033[0m")
            elif line.startswith("- "):
                print(f"    \033[91m{line}\033[0m")

    print(f"\n\033[92mADDED: {len(results['ADDED'])} sections\033[0m")
    for sec in results["ADDED"]:
        print(f"  • {sec['title']}")
        print(f"    + {sec['text']}")

    print(f"\n\033[91mDELETED: {len(results['DELETED'])} sections\033[0m")
    for sec in results["DELETED"]:
        print(f"  • {sec['title']}")
        print(f"    - {sec['text']}")

    # Write compliance comparison report artifact
    write_artifact_report(results)
    print(f"\nDetailed compliance report written to: {REPORT_PATH}")
    print("=" * 80 + "\n")

def write_artifact_report(results: Dict[str, List[Dict]]):
    """Generates the Markdown compliance report artifact."""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    
    markdown = []
    markdown.append("# KYC Policy Comparison & Gap Analysis Report")
    markdown.append(f"**Date generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown.append("\nThis report provides a structural and semantic delta analysis comparing the **KYC Baseline (January 2024)** with the **Amended KYC Master Directions (July 2026)**.\n")
    
    # Dashboard summary table
    markdown.append("## 📊 Change Dashboard")
    markdown.append("| Status | Count | Description |")
    markdown.append("| :--- | :---: | :--- |")
    markdown.append(f"| 🟢 **Added** | **{len(results['ADDED'])}** | New policy requirements introduced |")
    markdown.append(f"| 🟡 **Modified** | **{len(results['MODIFIED'])}** | Amended policy requirements |")
    markdown.append(f"| 🔴 **Deleted** | **{len(results['DELETED'])}** | Policy requirements removed or retired |")
    markdown.append(f"| ⚪ **Unchanged** | **{len(results['UNCHANGED'])}** | Retained policies without modifications |")
    markdown.append("\n---\n")

    # Modified Sections
    if results["MODIFIED"]:
        markdown.append("## 🟡 Modified Regulations")
        for idx, sec in enumerate(results["MODIFIED"]):
            markdown.append(f"### {idx+1}. {sec['title']}")
            markdown.append("```diff")
            for line in sec["diff"]:
                markdown.append(line)
            markdown.append("```")
            markdown.append("\n")
        markdown.append("---\n")

    # Added Sections
    if results["ADDED"]:
        markdown.append("## 🟢 Added Regulations")
        for idx, sec in enumerate(results["ADDED"]):
            markdown.append(f"### {idx+1}. {sec['title']}")
            markdown.append(f"> [!IMPORTANT]\n> **New Obligation:** {sec['text']}\n")
        markdown.append("---\n")

    # Deleted Sections
    if results["DELETED"]:
        markdown.append("## 🔴 Deleted/Retired Regulations")
        for idx, sec in enumerate(results["DELETED"]):
            markdown.append(f"### {idx+1}. {sec['title']}")
            markdown.append(f"> [!CAUTION]\n> **Retired Baseline Rule:** {sec['text']}\n")
        markdown.append("---\n")

    # Unchanged Sections
    if results["UNCHANGED"]:
        markdown.append("## ⚪ Unchanged Regulations")
        for sec in results["UNCHANGED"]:
            markdown.append(f"- **{sec['title']}**")
        markdown.append("\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown))

if __name__ == "__main__":
    from datetime import datetime
    main()
