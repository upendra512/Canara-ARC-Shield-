import os
import re
import uuid
import json
import logging
import difflib
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("node2.policy_diff_service")

# ==========================================
# 1. CORE DATA STRUCTURES
# ==========================================

@dataclass
class PolicyRule:
    rule_id: str
    rule_title: str
    rule_text: str
    section: str

@dataclass
class PolicyDocument:
    title: str
    version: str
    effective_date: str
    rules: Dict[str, PolicyRule]

@dataclass
class RuleDiff:
    rule_id: str
    change_type: str  # 'ADDED', 'MODIFIED', 'DELETED', 'UNCHANGED'
    section: str
    old_text: Optional[str]
    new_text: Optional[str]
    diff_summary: str
    diff_text: Optional[str] = None

# ==========================================
# 2. SOLID COMPLIANT INTERFACES
# ==========================================

class BasePolicyParser(ABC):
    """SRP: Parsing markdown/text policies into structured PolicyDocument objects"""
    @abstractmethod
    async def parse_file(self, file_path: str) -> PolicyDocument:
        pass

    @abstractmethod
    def parse_content(self, content: str) -> PolicyDocument:
        pass


class BasePolicyDiffer(ABC):
    """SRP: Comparing rules between two versions of a policy"""
    @abstractmethod
    def compare(self, old_doc: PolicyDocument, new_doc: PolicyDocument) -> List[RuleDiff]:
        pass


class BaseSeverityMapper(ABC):
    """SRP: Mapping compliance changes to impact severity levels"""
    @abstractmethod
    def evaluate_severity(self, diff: RuleDiff) -> str:
        pass


class BaseDepartmentMapper(ABC):
    """SRP: Routing compliance changes to responsible departments"""
    @abstractmethod
    def map_departments(self, diff: RuleDiff) -> Tuple[str, List[str]]:
        pass


class BasePolicyRepository(ABC):
    """SRP: Persistence operations for policies, chunks and mappings"""
    @abstractmethod
    async def save_policy_diffs(
        self, 
        policy_title: str, 
        version: str, 
        diffs: List[RuleDiff], 
        mapped_records: List[Dict[str, Any]],
        raw_text: str
    ) -> None:
        pass

# ==========================================
# 3. INTERFACE IMPLEMENTATIONS
# ==========================================

class MarkdownPolicyParser(BasePolicyParser):
    """Asynchronous and synchronous markdown parser using regex and section detection"""
    
    async def parse_file(self, file_path: str) -> PolicyDocument:
        logger.info(f"Asynchronously reading policy file: {file_path}")
        # Run blocking I/O in executor for clean async flow
        import asyncio
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(None, self._read_file, file_path)
        return self.parse_content(content)

    def _read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def parse_content(self, content: str) -> PolicyDocument:
        lines = content.splitlines()
        title = "Unknown Policy"
        version = "0.0.0"
        effective_date = "Unknown"
        
        current_section = "General"
        rules: Dict[str, PolicyRule] = {}
        
        # Regex patterns
        title_pat = re.compile(r"^#\s+(.+)$")
        version_pat = re.compile(r"\*\*Version:\*\*\s*(.+)$", re.IGNORECASE)
        date_pat = re.compile(r"\*\*Effective Date:\*\*\s*(.+)$", re.IGNORECASE)
        section_pat = re.compile(r"^##\s+(.+)$")
        
        # Matches list items like: * **[RULE-KYC-01] Official Valid Documents:** Banks must verify ...
        rule_pat = re.compile(r"^\*\s+\*\*\[([^\]]+)\]\s*([^:]+):\*\*\s*(.+)$")
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            # Parse headings and metadata
            if line_str.startswith("# "):
                m = title_pat.match(line_str)
                if m:
                    title = m.group(1).strip()
            elif "version:" in line_str.lower():
                m = version_pat.search(line_str)
                if m:
                    version = m.group(1).strip()
            elif "effective date:" in line_str.lower():
                m = date_pat.search(line_str)
                if m:
                    effective_date = m.group(1).strip()
            elif line_str.startswith("## "):
                m = section_pat.match(line_str)
                if m:
                    current_section = m.group(1).strip()
            elif line_str.startswith("* "):
                m = rule_pat.match(line_str)
                if m:
                    rule_id = m.group(1).strip()
                    rule_title = m.group(2).strip()
                    rule_text = m.group(3).strip()
                    rules[rule_id] = PolicyRule(
                        rule_id=rule_id,
                        rule_title=rule_title,
                        rule_text=rule_text,
                        section=current_section
                    )
        
        return PolicyDocument(
            title=title,
            version=version,
            effective_date=effective_date,
            rules=rules
        )


class PolicyDifferImpl(BasePolicyDiffer):
    """Compares two policy documents and computes granular diffs"""
    
    def compare(self, old_doc: PolicyDocument, new_doc: PolicyDocument) -> List[RuleDiff]:
        diffs: List[RuleDiff] = []
        
        # Combine all rule IDs from both documents to check additions, deletions, modifications
        all_rule_ids = set(old_doc.rules.keys()).union(set(new_doc.rules.keys()))
        
        for rule_id in all_rule_ids:
            old_rule = old_doc.rules.get(rule_id)
            new_rule = new_doc.rules.get(rule_id)
            
            if old_rule and new_rule:
                if old_rule.rule_text == new_rule.rule_text:
                    # Unchanged
                    diffs.append(RuleDiff(
                        rule_id=rule_id,
                        change_type="UNCHANGED",
                        section=new_rule.section,
                        old_text=old_rule.rule_text,
                        new_text=new_rule.rule_text,
                        diff_summary=f"Rule {rule_id} is unchanged."
                    ))
                else:
                    # Modified
                    diff_text = self._generate_diff_text(old_rule.rule_text, new_rule.rule_text)
                    diffs.append(RuleDiff(
                        rule_id=rule_id,
                        change_type="MODIFIED",
                        section=new_rule.section,
                        old_text=old_rule.rule_text,
                        new_text=new_rule.rule_text,
                        diff_summary=f"Rule {rule_id} has been modified from '{old_rule.rule_text}' to '{new_rule.rule_text}'",
                        diff_text=diff_text
                    ))
            elif new_rule and not old_rule:
                # Added
                diffs.append(RuleDiff(
                    rule_id=rule_id,
                    change_type="ADDED",
                    section=new_rule.section,
                    old_text=None,
                    new_text=new_rule.rule_text,
                    diff_summary=f"New rule {rule_id} has been added: '{new_rule.rule_text}'"
                ))
            elif old_rule and not new_rule:
                # Deleted
                diffs.append(RuleDiff(
                    rule_id=rule_id,
                    change_type="DELETED",
                    section=old_rule.section,
                    old_text=old_rule.rule_text,
                    new_text=None,
                    diff_summary=f"Rule {rule_id} has been deleted: '{old_rule.rule_text}'"
                ))
                
        return diffs

    def _generate_diff_text(self, old_text: str, new_text: str) -> str:
        old_words = old_text.split()
        new_words = new_text.split()
        diff = difflib.ndiff(old_words, new_words)
        return '\n'.join(diff)


class RuleSeverityMapper(BaseSeverityMapper):
    """Decides rule severity based on change type, security context, and numeric threshold changes"""
    
    def evaluate_severity(self, diff: RuleDiff) -> str:
        if diff.change_type == "DELETED":
            # Deletion of compliance controls is critical
            return "CRITICAL"
            
        text_to_analyze = (diff.new_text or diff.old_text or "").lower()
        
        # Check rule category or text contents
        is_security = any(kw in text_to_analyze for kw in ["cyber", "mfa", "encryption", "incident", "auth", "password", "biometric"])
        is_high_risk_kyc = any(kw in text_to_analyze for kw in ["due diligence", "cdd", "edd", "verify", "identity"])
        
        if diff.change_type == "ADDED":
            if is_security:
                return "HIGH"
            elif is_high_risk_kyc:
                return "HIGH"
            return "MEDIUM"
            
        elif diff.change_type == "MODIFIED":
            # Check if there is a numeric change
            old_nums = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', diff.old_text or "")]
            new_nums = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', diff.new_text or "")]
            
            if old_nums and new_nums:
                # If there are numeric threshold changes, calculate variation
                try:
                    old_val = old_nums[0]
                    new_val = new_nums[0]
                    if old_val > 0:
                        pct_change = abs(new_val - old_val) / old_val
                        if pct_change >= 0.5:
                            return "HIGH"
                        elif pct_change >= 0.2:
                            return "MEDIUM"
                except Exception:
                    pass
            
            if is_security:
                return "HIGH"
            return "MEDIUM"
            
        return "LOW"


class RuleDepartmentMapper(BaseDepartmentMapper):
    """Routes policy changes to correct departments using our structured taxonomy"""
    
    def __init__(self, rule_taxonomy_path: Optional[str] = None):
        self.taxonomy = {}
        if rule_taxonomy_path and os.path.exists(rule_taxonomy_path):
            try:
                with open(rule_taxonomy_path, 'r', encoding='utf-8') as f:
                    self.taxonomy = json.load(f)
            except Exception as e:
                logger.error(f"Error loading taxonomy in department mapper: {e}")
                
    def map_departments(self, diff: RuleDiff) -> Tuple[str, List[str]]:
        primary = "General Legal"
        secondary = []
        
        rule_id = diff.rule_id.upper()
        text = (diff.new_text or diff.old_text or "").lower()
        
        # Basic keyword routing rules
        if any(kw in rule_id or kw in text for kw in ["CYBER", "SECURITY", "MFA", "AUTHENTICATION", "PASSWORD"]):
            primary = "Cybersecurity Wing"
            secondary = ["IT Vertical", "Digital Banking Services"]
        elif any(kw in rule_id or kw in text for kw in ["AML", "MONITORING", "CTR", "SUSPICIOUS", "CASH"]):
            primary = "Compliance Department"
            secondary = ["Risk Management"]
        elif any(kw in rule_id or kw in text for kw in ["KYC", "IDENT", "DOCUMENT", "RETENTION", "DILIGENCE"]):
            primary = "Compliance Department"
            secondary = ["Customer Service", "Legal Department"]
            
        # Try to match specific rule type to department taxonomy
        rule_to_dept = self.taxonomy.get("rule_to_department_mapping", {})
        matched_rule_type = None
        if "CYBER" in rule_id:
            matched_rule_type = "AUTHENTICATION" if "mfa" in text or "authentication" in text else "ENCRYPTION"
        elif "KYC-01" in rule_id:
            matched_rule_type = "IDENTITY_VERIFICATION"
        elif "KYC-02" in rule_id:
            matched_rule_type = "RECORD_RETENTION"
        elif "KYC-03" in rule_id:
            matched_rule_type = "CDD_REQUIREMENT"
        elif "AML-01" in rule_id:
            matched_rule_type = "TRANSACTION_MONITORING"
        elif "AML-02" in rule_id:
            matched_rule_type = "TRANSACTION_MONITORING"
            
        if matched_rule_type and matched_rule_type in rule_to_dept:
            mapped_def = rule_to_dept[matched_rule_type]
            primary = mapped_def.get("primary", primary)
            secondary = mapped_def.get("secondary", secondary)
            
        return primary, secondary


class PolicyMockDbRepository(BasePolicyRepository):
    """Integrates directly with the system's mock_db.json file"""
    
    def __init__(self, db_path: str = "mock_db.json"):
        self.db_path = db_path
        
    def _load_db(self) -> Dict[str, Any]:
        if not os.path.exists(self.db_path):
            return {"clauses": {}, "compliance_maps": [], "human_review_queue": []}
        with open(self.db_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {"clauses": {}, "compliance_maps": [], "human_review_queue": []}
            
    def _save_db(self, db: Dict[str, Any]) -> None:
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
            
    async def save_policy_diffs(
        self, 
        policy_title: str, 
        version: str, 
        diffs: List[RuleDiff], 
        mapped_records: List[Dict[str, Any]],
        raw_text: str
    ) -> None:
        logger.info(f"Saving policy diffs and new clauses to DB: {self.db_path}")
        
        # Load DB in executor for async safety
        import asyncio
        loop = asyncio.get_event_loop()
        db = await loop.run_in_executor(None, self._load_db)
        
        # 1. Update compliance_maps
        if "compliance_maps" not in db:
            db["compliance_maps"] = []
            
        db["compliance_maps"].extend(mapped_records)
        
        # 2. Add the clauses from the new policy version to the clauses database
        if "clauses" not in db:
            db["clauses"] = {}
            
        for i, diff in enumerate(diffs):
            if diff.change_type in ["ADDED", "MODIFIED", "UNCHANGED"]:
                clause_id = f"POL-{policy_title.replace(' ', '-')}-v{version}::{diff.rule_id}"
                db["clauses"][clause_id] = {
                    "clause_id": clause_id,
                    "circular_id": f"POL-{policy_title.replace(' ', '-')}-v{version}",
                    "circular_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "domain": diff.section,
                    "section_title": diff.section,
                    "raw_text": diff.new_text,
                    "created_at": datetime.utcnow().isoformat(),
                    "source": "INTERNAL_POLICY"
                }
                
        # Save DB in executor
        await loop.run_in_executor(None, self._save_db, db)
        logger.info("Successfully updated mock database with policy version updates.")

# ==========================================
# 4. ORCHESTRATION ENGINE (FACADE)
# ==========================================

class PolicyDiffEngine:
    """Facade orchestrator coordinating the entire comparison and mapping workflow"""
    
    def __init__(
        self,
        parser: BasePolicyParser,
        differ: BasePolicyDiffer,
        severity_mapper: BaseSeverityMapper,
        dept_mapper: BaseDepartmentMapper,
        repository: BasePolicyRepository
    ):
        self.parser = parser
        self.differ = differ
        self.severity_mapper = severity_mapper
        self.dept_mapper = dept_mapper
        self.repository = repository
        
    async def process_policy_update(
        self, 
        old_policy_path: str, 
        new_policy_path: str
    ) -> Dict[str, Any]:
        logger.info("--- Starting Policy Update Analysis Workflow ---")
        
        # Parse both versions
        old_doc = await self.parser.parse_file(old_policy_path)
        new_doc = await self.parser.parse_file(new_policy_path)
        
        logger.info(f"Old version: {old_doc.version}, Rules count: {len(old_doc.rules)}")
        logger.info(f"New version: {new_doc.version}, Rules count: {len(new_doc.rules)}")
        
        # Compute differences
        diffs = self.differ.compare(old_doc, new_doc)
        
        # Process and map each diff
        mapped_records = []
        for diff in diffs:
            # We skip UNCHANGED rules for database mapping records
            if diff.change_type == "UNCHANGED":
                continue
                
            # Map severity
            severity = self.severity_mapper.evaluate_severity(diff)
            
            # Map department
            primary_dept, secondary_depts = self.dept_mapper.map_departments(diff)
            
            # Form mapping record compatible with backend schema
            map_record = {
                "map_id": str(uuid.uuid4()),
                "clause_ref": diff.rule_id,
                "change_type": diff.change_type,
                "change_reason": diff.diff_summary,
                "impact": severity,
                "summary": f"{diff.change_type} rule in section '{diff.section}': {diff.diff_summary}",
                "old_obligation": diff.old_text,
                "new_obligation": diff.new_text,
                "affected_department": primary_dept,
                "deadline": datetime.utcnow().isoformat() + "Z",
                "source_circular": f"{new_doc.title} v{new_doc.version}",
                "confidence": 0.95
            }
            mapped_records.append(map_record)
            
        # Read raw text of new policy
        import asyncio
        loop = asyncio.get_event_loop()
        raw_text = await loop.run_in_executor(None, self._read_raw, new_policy_path)
            
        # Save to database
        await self.repository.save_policy_diffs(
            policy_title=new_doc.title,
            version=new_doc.version,
            diffs=diffs,
            mapped_records=mapped_records,
            raw_text=raw_text
        )
        
        logger.info(f"--- Policy Update Analysis Workflow Completed. Mapped {len(mapped_records)} changes. ---")
        
        return {
            "title": new_doc.title,
            "old_version": old_doc.version,
            "new_version": new_doc.version,
            "diffs": [
                {
                    "rule_id": d.rule_id,
                    "change_type": d.change_type,
                    "section": d.section,
                    "summary": d.diff_summary,
                    "old_text": d.old_text,
                    "new_text": d.new_text
                }
                for d in diffs
            ],
            "mapped_records": mapped_records
        }

    def _read_raw(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
