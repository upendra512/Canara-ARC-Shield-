"""
NODE 2 INTEGRATION: Bridge between Deterministic Mapper & Existing Workflow
"""

import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from deterministic_mapper import DeterministicRuleMapper, RuleMapping
from schemas import IncomingChunk, MAP

logger = logging.getLogger(__name__)


class EnhancedNode2Engine:
    """
    Enhanced Node 2 that integrates deterministic rule extraction
    with the existing mapping workflow.
    """
    
    def __init__(self, rule_taxonomy_path: str = "node2_map_engine/rule_taxonomy.json"):
        self.mapper = DeterministicRuleMapper(rule_taxonomy_path)
    
    def extract_and_map_chunk(
        self,
        chunk: IncomingChunk,
        raw_chunk_text: str,
        heading: str = None
    ) -> Dict[str, Any]:
        """
        DETERMINISTIC EXTRACTION WORKFLOW:
        
        1. Extract policy type from heading (if provided)
        2. Extract rules from chunk using deterministic mapper
        3. Map each rule to department(s)
        4. Generate enhanced MAP output
        
        No LLM needed. 100% auditable.
        """
        
        result = {
            "chunk_id": chunk.chunk_index,
            "circular_id": chunk.circular_id,
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "policy_type": chunk.domain,
            "extracted_rules": [],
            "department_mappings": [],
            "audit_trail": {}
        }
        
        # STEP 1: Policy type classification (if heading provided)
        if heading:
            policy_type, policy_conf, policy_audit = \
                self.mapper.extract_policy_type_from_heading(heading)
            result["policy_type"] = policy_type
            result["audit_trail"]["policy_classification"] = {
                "heading": heading,
                "classified_as": policy_type,
                "confidence": policy_conf,
                "details": policy_audit
            }
            logger.info(f"Policy classified as {policy_type} (conf: {policy_conf})")
        else:
            policy_type = chunk.domain
        
        # STEP 2: Extract rules from chunk
        extracted_rules = self.mapper.extract_rules_from_chunk(
            raw_chunk_text,
            policy_type
        )
        
        if not extracted_rules:
            logger.warning(f"No rules extracted from chunk {chunk.chunk_index}")
            result["audit_trail"]["extraction_status"] = "NO_RULES_FOUND"
            return result
        
        result["audit_trail"]["extraction_status"] = "RULES_FOUND"
        result["audit_trail"]["rule_count"] = len(extracted_rules)
        
        # STEP 3: Convert to mappings & generate MAP objects
        for rule_extraction in extracted_rules:
            # Map rule to department
            dept_mapping = self.mapper.map_rule_to_department(
                rule_extraction.rule_type,
                rule_extraction.confidence
            )
            
            if not dept_mapping:
                logger.warning(f"Could not map {rule_extraction.rule_type} to department")
                continue
            
            # Add to results
            result["extracted_rules"].append({
                "rule_type": rule_extraction.rule_type,
                "policy_type": rule_extraction.policy_type,
                "confidence": rule_extraction.confidence,
                "matched_keywords": rule_extraction.matched_keywords,
                "matched_phrases": rule_extraction.matched_phrases,
                "reasoning": rule_extraction.reasoning,
                "line_number": rule_extraction.line_number
            })
            
            result["department_mappings"].append({
                "rule_type": dept_mapping.rule_type,
                "primary_department": dept_mapping.primary_department,
                "secondary_departments": dept_mapping.secondary_departments,
                "system_owner": dept_mapping.system_owner,
                "owner_subsystem": dept_mapping.owner_subsystem,
                "confidence": dept_mapping.confidence,
                "implementation_ref": dept_mapping.implementation_ref,
                "audit_trail": dept_mapping.audit_trail
            })
        
        return result
    
    def generate_map_from_extraction(
        self,
        extraction_result: Dict[str, Any],
        chunk: IncomingChunk,
        old_obligation: Optional[str] = None
    ) -> Optional[MAP]:
        """
        Convert deterministic extraction result → MAP object
        for database storage and compliance tracking.
        """
        
        if not extraction_result.get("department_mappings"):
            return None
        
        # Aggregate all departments for this chunk
        all_departments = set()
        all_rules = []
        primary_dept = None
        
        for mapping in extraction_result["department_mappings"]:
            all_departments.add(mapping["primary_department"])
            all_departments.update(mapping["secondary_departments"])
            all_rules.append(mapping["rule_type"])
            
            if not primary_dept:
                primary_dept = mapping["primary_department"]
        
        # Generate MAP
        map_obj = MAP(
            map_id=f"{chunk.circular_id}::{chunk.chunk_index}",
            clause_ref=f"CHUNK_{chunk.chunk_index}",
            change_type="NEW_OBLIGATION",  # Determined by Node 3
            change_reason=f"Deterministic extraction of {len(all_rules)} rules",
            impact={
                "affected_rules": all_rules,
                "affected_departments": list(all_departments),
                "rule_count": len(all_rules)
            },
            summary=f"Extracted {len(all_rules)} compliance rules requiring action in {primary_dept}",
            old_obligation=old_obligation,
            new_obligation=chunk.chunk_text,
            affected_department=primary_dept,
            deadline=datetime.utcnow(),
            source_circular=chunk.circular_id,
            confidence=sum(
                m["confidence"] for m in extraction_result["department_mappings"]
            ) / len(extraction_result["department_mappings"])
        )
        
        return map_obj
    
    def batch_process_chunks(
        self,
        chunks: List[IncomingChunk],
        heading: str = None
    ) -> Dict[str, Any]:
        """
        Process multiple chunks from a single circular.
        Returns aggregated extraction + mapping results.
        """
        
        results = {
            "circular_id": chunks[0].circular_id if chunks else None,
            "heading": heading,
            "total_chunks": len(chunks),
            "chunks_processed": 0,
            "total_rules_extracted": 0,
            "chunk_results": [],
            "department_action_items": {}
        }
        
        for chunk in chunks:
            extraction = self.extract_and_map_chunk(
                chunk,
                chunk.chunk_text,
                heading if chunk.chunk_index == 0 else None  # Use heading for first chunk
            )
            
            results["chunks_processed"] += 1
            results["total_rules_extracted"] += len(extraction["extracted_rules"])
            results["chunk_results"].append(extraction)
            
            # Aggregate by department
            for mapping in extraction["department_mappings"]:
                dept = mapping["primary_department"]
                if dept not in results["department_action_items"]:
                    results["department_action_items"][dept] = {
                        "primary_rules": [],
                        "secondary_rules": [],
                        "total_confidence": 0.0
                    }
                
                results["department_action_items"][dept]["primary_rules"].append(
                    mapping["rule_type"]
                )
                results["department_action_items"][dept]["secondary_rules"].extend(
                    mapping["secondary_departments"]
                )
                results["department_action_items"][dept]["total_confidence"] += \
                    mapping["confidence"]
        
        return results


# ============= COMPATIBILITY TEST =============

if __name__ == "__main__":
    # Example with existing IncomingChunk schema
    sample_chunk = IncomingChunk(
        chunk_index=0,
        circular_id="RBI_2024_001",
        circular_date="2024-06-01",
        regulator="RBI",
        domain="KYC",
        section_title="Customer Identification",
        chunk_text="""
        Banks shall verify the identity of customers using official valid documents (OVD).
        Enhanced due diligence shall be performed for high-risk customers.
        Transaction monitoring must be conducted in real-time on all transactions.
        KYC records must be retained for 10 years after account closure.
        """
    )
    
    engine = EnhancedNode2Engine()
    
    result = engine.extract_and_map_chunk(
        sample_chunk,
        sample_chunk.chunk_text,
        heading="Master Direction - KYC and AML Requirements (Amended)"
    )
    
    print("\n===== ENHANCED NODE 2 EXTRACTION =====\n")
    print(json.dumps(result, indent=2))
    
    # Test MAP generation
    map_obj = engine.generate_map_from_extraction(result, sample_chunk)
    if map_obj:
        print("\n===== GENERATED MAP OBJECT =====\n")
        print(json.dumps(map_obj.model_dump(), indent=2))
