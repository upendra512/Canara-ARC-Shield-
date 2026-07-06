"""
DETERMINISTIC RULE EXTRACTION & MAPPING ENGINE
No ML. Pure keyword + pattern matching + taxonomy.
100% auditable, traceable, repeatable.
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence scoring for rule mapping (deterministic)"""
    EXACT_MATCH = 0.95  # Exact keyword + header pattern match
    STRONG_MATCH = 0.85  # Multiple keywords + trigger phrase
    MODERATE_MATCH = 0.70  # Some keywords + context
    WEAK_MATCH = 0.50  # Single keyword, minimal context
    NO_MATCH = 0.0


@dataclass
class RuleExtraction:
    """Result of deterministic rule extraction"""
    rule_type: str
    policy_type: str
    confidence: float
    matched_keywords: List[str]
    matched_phrases: List[str]
    chunk_text: str
    line_number: int
    reasoning: str


@dataclass
class RuleMapping:
    """Rule mapped to department(s)"""
    rule_type: str
    policy_type: str
    confidence: float
    primary_department: str
    secondary_departments: List[str]
    system_owner: str
    owner_subsystem: str
    implementation_ref: Optional[str]
    audit_trail: Dict[str, Any]


class DeterministicRuleMapper:
    """
    Pure deterministic (NO ML) rule extraction and mapping.
    Uses keyword taxonomy + regex patterns + rule definitions.
    """
    
    def __init__(self, rule_taxonomy_path: str):
        """Load the rule taxonomy"""
        with open(rule_taxonomy_path, 'r') as f:
            self.taxonomy = json.load(f)
        self.policy_types = self.taxonomy["policy_types"]
        self.rule_types = self.taxonomy["rule_types"]
        self.rule_dept_mapping = self.taxonomy["rule_to_department_mapping"]
    
    # =========== PHASE 1: HEADING → POLICY TYPE ===========
    
    def extract_policy_type_from_heading(self, heading: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        DETERMINISTIC: Classify policy type from heading.
        Uses keyword matching + header patterns + regulatory references.
        
        Returns: (policy_type, confidence, audit_details)
        """
        heading_lower = heading.lower()
        audit_trail = {
            "matched_keywords": [],
            "matched_patterns": [],
            "scores": {}
        }
        
        best_policy = None
        best_score = 0.0
        
        for policy_name, policy_def in self.policy_types.items():
            score = 0.0
            matched_kw = []
            matched_patterns = []
            
            # KEYWORD MATCHING (weight: 0.4)
            kw_matches = sum(1 for kw in policy_def["keywords"] 
                           if kw in heading_lower)
            if kw_matches > 0:
                kw_score = min(kw_matches * 0.2, 0.4)  # Cap at 0.4
                score += kw_score
                matched_kw = [kw for kw in policy_def["keywords"] 
                            if kw in heading_lower]
            
            # HEADER PATTERN MATCHING (weight: 0.6)
            for pattern in policy_def["header_patterns"]:
                if re.search(pattern, heading_lower, re.IGNORECASE):
                    score += 0.6
                    matched_patterns.append(pattern)
                    break  # First match counts
            
            if score > best_score:
                best_score = score
                best_policy = policy_name
                audit_trail["matched_keywords"] = matched_kw
                audit_trail["matched_patterns"] = matched_patterns
            
            audit_trail["scores"][policy_name] = score
        
        # CONFIDENCE MAPPING
        if best_score >= 0.6:
            confidence = ConfidenceLevel.EXACT_MATCH.value
        elif best_score >= 0.4:
            confidence = ConfidenceLevel.STRONG_MATCH.value
        elif best_score >= 0.2:
            confidence = ConfidenceLevel.MODERATE_MATCH.value
        else:
            confidence = ConfidenceLevel.WEAK_MATCH.value
        
        return best_policy or "UNKNOWN", confidence, audit_trail
    
    # =========== PHASE 2: CHUNK → EXTRACT RULES ===========
    
    def extract_rules_from_chunk(
        self, 
        chunk_text: str, 
        policy_type: str,
        line_offset: int = 0
    ) -> List[RuleExtraction]:
        """
        DETERMINISTIC: Extract individual rules from a policy chunk.
        Each rule is: keyword match + trigger phrase + context validation.
        
        Returns: List of RuleExtraction objects (one per rule found)
        """
        rules_found = []
        lines = chunk_text.split('\n')
        chunk_lower = chunk_text.lower()
        
        for rule_name, rule_def in self.rule_types.items():
            # Check if rule applies to this policy type
            if rule_def["category"] != policy_type:
                continue
            
            # KEYWORD MATCHING
            matched_keywords = [
                kw for kw in rule_def["keywords"]
                if kw in chunk_lower
            ]
            
            if not matched_keywords:
                continue  # No keywords = no match
            
            # TRIGGER PHRASE MATCHING (validates it's actually a rule, not just mention)
            matched_phrases = []
            for trigger in rule_def["trigger_phrases"]:
                matches = re.findall(trigger, chunk_lower, re.IGNORECASE)
                if matches:
                    matched_phrases.extend(matches)
            
            # SCORING
            if matched_phrases:
                # Has trigger phrase = strong evidence of actual rule
                confidence = ConfidenceLevel.STRONG_MATCH.value
                reasoning = f"Matched {len(matched_keywords)} keywords + {len(matched_phrases)} trigger phrases"
            elif len(matched_keywords) >= 2:
                # Multiple keywords = moderate evidence
                confidence = ConfidenceLevel.MODERATE_MATCH.value
                reasoning = f"Matched {len(matched_keywords)} keywords (no trigger phrase)"
            else:
                # Single keyword = weak evidence
                confidence = ConfidenceLevel.WEAK_MATCH.value
                reasoning = f"Single keyword match"
            
            # Find line number
            line_num = line_offset
            for i, line in enumerate(lines):
                if any(kw in line.lower() for kw in matched_keywords):
                    line_num = line_offset + i
                    break
            
            extraction = RuleExtraction(
                rule_type=rule_name,
                policy_type=policy_type,
                confidence=confidence,
                matched_keywords=matched_keywords,
                matched_phrases=matched_phrases,
                chunk_text=chunk_text[:500],  # First 500 chars for context
                line_number=line_num,
                reasoning=reasoning
            )
            
            rules_found.append(extraction)
        
        return rules_found
    
    # =========== PHASE 3: RULE → DEPARTMENT MAPPING ===========
    
    def map_rule_to_department(
        self, 
        rule_type: str,
        confidence: float
    ) -> Optional[RuleMapping]:
        """
        DETERMINISTIC: Map extracted rule to department(s).
        Uses the rule_to_department_mapping taxonomy.
        
        Returns: RuleMapping with primary + secondary departments
        """
        if rule_type not in self.rule_dept_mapping:
            return None
        
        mapping_def = self.rule_dept_mapping[rule_type]
        rule_def = self.rule_types.get(rule_type, {})
        
        mapping = RuleMapping(
            rule_type=rule_type,
            policy_type=rule_def.get("category", "UNKNOWN"),
            confidence=confidence,
            primary_department=mapping_def["primary"],
            secondary_departments=mapping_def["secondary"],
            system_owner=mapping_def["system_owner"],
            owner_subsystem=mapping_def["owner_subsystem"],
            implementation_ref=rule_def.get("sub_rules", {}).get("IMPLEMENTATION", {}).get("implementation"),
            audit_trail={
                "confidence_score": confidence,
                "mapping_source": "deterministic_taxonomy",
                "rule_category": rule_def.get("category"),
                "has_sub_rules": bool(rule_def.get("sub_rules"))
            }
        )
        
        return mapping
    
    # =========== END-TO-END WORKFLOW ===========
    
    def process_circular_heading_and_extract_rules(
        self,
        heading: str,
        chunks: List[str]
    ) -> Dict[str, Any]:
        """
        COMPLETE WORKFLOW:
        1. Heading → Policy Type classification
        2. Each chunk → Extract rules
        3. Each rule → Map to department(s)
        
        100% deterministic output with full audit trail.
        """
        
        # STEP 1: Classify policy type
        policy_type, policy_confidence, policy_audit = \
            self.extract_policy_type_from_heading(heading)
        
        # STEP 2: For each chunk, extract rules
        all_extracted_rules = []
        all_mapped_rules = []
        
        for chunk_idx, chunk in enumerate(chunks):
            extracted = self.extract_rules_from_chunk(
                chunk, 
                policy_type,
                line_offset=chunk_idx * 100  # Rough estimate
            )
            all_extracted_rules.extend(extracted)
            
            # STEP 3: Map each rule to department
            for rule_extraction in extracted:
                department_mapping = self.map_rule_to_department(
                    rule_extraction.rule_type,
                    rule_extraction.confidence
                )
                if department_mapping:
                    all_mapped_rules.append(department_mapping)
        
        return {
            "heading": heading,
            "policy_type": policy_type,
            "policy_confidence": policy_confidence,
            "policy_audit": policy_audit,
            "extracted_rules": [
                {
                    "rule_type": r.rule_type,
                    "policy_type": r.policy_type,
                    "confidence": r.confidence,
                    "matched_keywords": r.matched_keywords,
                    "matched_phrases": r.matched_phrases,
                    "reasoning": r.reasoning,
                    "line_number": r.line_number
                }
                for r in all_extracted_rules
            ],
            "department_mappings": [
                {
                    "rule_type": m.rule_type,
                    "primary_department": m.primary_department,
                    "secondary_departments": m.secondary_departments,
                    "system_owner": m.system_owner,
                    "owner_subsystem": m.owner_subsystem,
                    "confidence": m.confidence,
                    "audit_trail": m.audit_trail
                }
                for m in all_mapped_rules
            ]
        }


# ============= TEST / DEMO =============

if __name__ == "__main__":
    mapper = DeterministicRuleMapper("node2_map_engine/rule_taxonomy.json")
    
    # Example heading
    heading = "Master Direction - Know Your Customer (KYC) Norms and Anti-Money Laundering (AML) Requirements"
    
    # Example chunks
    chunks = [
        """
        The bank shall verify the identity of the customer using official valid documents (OVD).
        Each customer must provide proof of address as per the KYC guidelines.
        PAN and Aadhaar verification is mandatory for all account openings.
        """,
        """
        The bank shall perform customer due diligence (CDD) before onboarding.
        Customers shall be classified as Low, Medium, or High risk.
        High-risk customers require Enhanced Due Diligence (EDD) and additional checks.
        """,
        """
        Transaction monitoring shall be performed in real-time.
        Suspicious transactions shall be reported to FIU within the prescribed timeline.
        All KYC records shall be retained for 10 years after account closure.
        """
    ]
    
    result = mapper.process_circular_heading_and_extract_rules(heading, chunks)
    
    print("\n===== DETERMINISTIC EXTRACTION RESULT =====\n")
    print(json.dumps(result, indent=2))
