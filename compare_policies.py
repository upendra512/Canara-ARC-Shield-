import os
import sys
import json
import logging
import difflib
import hashlib
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Set, Any, Optional

# Add root folder to PYTHONPATH to allow relative imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from node2_map_engine.seed_policies import seed_database
from node2_map_engine.identifier import PolicyIdentifier, strip_markdown_headers
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

# ==========================================
# 1. DEPENDENCY INJECTION SERVICES (SOLID)
# ==========================================

class HashingService(ABC):
    """Interface for generating standard compliance hashes."""
    @abstractmethod
    def hash_text(self, text: str) -> str:
        pass

class Sha256HashingService(HashingService):
    """SHA-256 implementation stripping formatting headers and normalizing whitespace."""
    def hash_text(self, text: str) -> str:
        if not text:
            return ""
        clean_text = strip_markdown_headers(text)
        normalized = re.sub(r'\s+', ' ', clean_text.lower()).strip()
        normalized = re.sub(r'(?<=\d),(?=\d)', '', normalized)
        normalized = re.sub(r'[.,;!?"\']$', '', normalized)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

class DiffService(ABC):
    """Interface for computing visual regulatory text differences."""
    @abstractmethod
    def compute_sentence_diff(self, old_text: str, new_text: str) -> List[str]:
        pass

class SentenceDiffService(DiffService):
    """Sentence-level diffing utilizing standard ndiff delta outputs."""
    def compute_sentence_diff(self, old_text: str, new_text: str) -> List[str]:
        old_clean = strip_markdown_headers(old_text)
        new_clean = strip_markdown_headers(new_text)
        
        old_sentences = [s.strip() + "." for s in old_clean.split(".") if s.strip()]
        new_sentences = [s.strip() + "." for s in new_clean.split(".") if s.strip()]
        
        diff = difflib.ndiff(old_sentences, new_sentences)
        return [line for line in diff if line.startswith("+ ") or line.startswith("- ")]

# ==========================================
# 2. COMPARISON ENGINE (ORCHESTRATOR)
# ==========================================

class PolicyComparisonEngine:
    """Core orchestrator class utilizing Dependency Injection for components."""
    def __init__(self, identifier: PolicyIdentifier, hashing_service: HashingService, diff_service: DiffService):
        self.identifier = identifier
        self.hashing_service = hashing_service
        self.diff_service = diff_service

    def compare(self, new_chunks: List[str], active_baseline_ids: Set[str], baseline_clauses: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        results = {
            "UNCHANGED": [],
            "MODIFIED": [],
            "ADDED": [],
            "DELETED": []
        }

        for chunk in new_chunks:
            # Classify in Node 1 to find domain & section title
            verdict = classify(chunk)
            section_title = verdict.get("regSection", "Other")

            # Run the 3-Signal matching cascade
            match_res = self.identifier.identify(new_text=chunk, section_title=section_title)
            verdict_type = match_res["verdict"]

            if verdict_type in ["UNCHANGED", "MODIFIED"]:
                matched_clause = match_res["matched_clause"]
                matched_id = matched_clause.get("clause_id")
                
                # Check for content change using injected hashing service
                old_raw = matched_clause.get("raw_text", "")
                old_hash = self.hashing_service.hash_text(old_raw)
                new_hash = self.hashing_service.hash_text(chunk)
                is_identical = (old_hash == new_hash)

                if matched_id in active_baseline_ids:
                    active_baseline_ids.remove(matched_id)

                if is_identical:
                    results["UNCHANGED"].append({
                        "title": matched_clause.get("section_title", section_title),
                        "text": chunk
                    })
                else:
                    results["MODIFIED"].append({
                        "title": matched_clause.get("section_title", section_title),
                        "old_text": old_raw,
                        "new_text": chunk,
                        "diff": self.diff_service.compute_sentence_diff(old_raw, chunk)
                    })
            else:
                if verdict["obligationBearing"]:
                    results["ADDED"].append({
                        "title": section_title,
                        "text": chunk
                    })

        # Mark all unmatched active baseline clauses as DELETED
        for deleted_id in active_baseline_ids:
            clause = baseline_clauses[deleted_id]
            results["DELETED"].append({
                "title": clause["section_title"],
                "text": clause["raw_text"]
            })

        return results

# ==========================================
# 3. RUNNER WORKFLOW
# ==========================================

def main():
    print("=" * 80)
    print("STARTING KYC POLICY COMPARISON WORKFLOW (CLEAN OOP)")
    print("=" * 80)

    # Step 1: Clean DB completely to prevent namespace/historical collisions
    if os.path.exists(DB_PATH):
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            db["clauses"] = {}
            db["compliance_maps"] = []
            db["human_review_queue"] = []
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2)
            print("Cleared database clauses and maps for a clean comparison run.")
        except Exception as e:
            print(f"Warning: Could not clear DB: {e}")

    # Step 2: Seed the database with the baseline kyc.md policy
    print("\n[STEP 1] Seeding baseline policies into the database...")
    seed_database()

    # Step 3: Load the baseline database to track active clauses
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    with open(DB_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)

    # Collect seeded KYC baseline clauses
    baseline_clauses = db.get("clauses", {})
    active_baseline_ids = {
        cid for cid, clause in baseline_clauses.items()
        if clause.get("domain") == "KYC" and clause.get("source") == "SEED"
    }
    
    print(f"Loaded {len(active_baseline_ids)} baseline KYC policies from DB.")

    # Step 4: Parse and segment the amended circular
    print(f"\n[STEP 2] Reading amended policy file: {os.path.basename(NEW_CIRCULAR_PATH)}...")
    if not os.path.exists(NEW_CIRCULAR_PATH):
        print(f"Error: File not found at {NEW_CIRCULAR_PATH}")
        return

    with open(NEW_CIRCULAR_PATH, "r", encoding="utf-8") as f:
        new_text = f.read()

    new_chunks = _segments(new_text)
    print(f"Segmented amended document into {len(new_chunks)} section chunks.")

    # Step 5: Instantiate services and run comparison (Dependency Injection)
    print("\n[STEP 3] Comparing amended chunks against baseline...")
    identifier = PolicyIdentifier()
    hashing_service = Sha256HashingService()
    diff_service = SentenceDiffService()

    engine = PolicyComparisonEngine(
        identifier=identifier,
        hashing_service=hashing_service,
        diff_service=diff_service
    )

    results = engine.compare(new_chunks, active_baseline_ids, baseline_clauses)

    # Step 6: Print Change Results
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
        # Print body text cleanly without header markings
        body_lines = [l.strip() for l in sec["text"].split("\n") if l.strip() and not l.strip().startswith("#")]
        for l in body_lines:
            print(f"    + {l}")

    print(f"\n\033[91mDELETED: {len(results['DELETED'])} sections\033[0m")
    for sec in results["DELETED"]:
        print(f"  • {sec['title']}")
        body_lines = [l.strip() for l in sec["text"].split("\n") if l.strip() and not l.strip().startswith("#")]
        for l in body_lines:
            print(f"    - {l}")

    # Write compliance comparison report artifact
    write_artifact_report(results)
    print(f"\nDetailed compliance report written to: {REPORT_PATH}")
    print("=" * 80 + "\n")

def write_artifact_report(results: Dict[str, List[Dict]]):
    """Generates the Markdown compliance report artifact."""
    from datetime import datetime
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
            # Clean body formatting
            body_text = "\n".join(l.strip() for l in sec['text'].split('\n') if l.strip() and not l.strip().startswith('#'))
            markdown.append(f"> [!IMPORTANT]\n> **New Obligation:** {body_text}\n")
        markdown.append("---\n")

    # Deleted Sections
    if Antiquity := results["DELETED"]:
        markdown.append("## 🔴 Deleted/Retired Regulations")
        for idx, sec in enumerate(Antiquity):
            markdown.append(f"### {idx+1}. {sec['title']}")
            body_text = "\n".join(l.strip() for l in sec['text'].split('\n') if l.strip() and not l.strip().startswith('#'))
            markdown.append(f"> [!CAUTION]\n> **Retired Baseline Rule:** {body_text}\n")
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
    main()
