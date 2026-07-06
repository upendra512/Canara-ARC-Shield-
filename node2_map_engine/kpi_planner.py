"""
Compliance KPI Assessment and Planner Engine.
Processes USER'S UPLOADED CSV and KPI JSONs to assess compliance posture,
map gap rules to departments, score severity, and generate a remediation plan.
"""

import csv
import json
import logging
import re
from io import StringIO
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error
from node2_map_engine import config

logger = logging.getLogger("node2.kpi_planner")

class KPIPlanner:
    def __init__(self):
        pass

    def parse_csv_metrics(self, csv_text: str) -> Dict[str, List[float]]:
        """
        Parses CSV and extracts numeric values per column.
        Allows mapping fields in KPI JSONs to CSV column data.
        """
        metrics = {}
        f = StringIO(csv_text.strip())
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return {}

        headers = [h.strip() for h in reader.fieldnames]
        for h in headers:
            metrics[h] = []

        for row in reader:
            for h in headers:
                val = row.get(h)
                if val is not None:
                    try:
                        # Strip currency, percentage signs or commas
                        clean_val = re.sub(r'[^\d.-]', '', str(val))
                        metrics[h].append(float(clean_val))
                    except ValueError:
                        pass
        return metrics

    def evaluate_kpis(self, metrics: Dict[str, List[float]], kpis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluates each KPI against parsed metrics.
        Computes actual value, status (PASS/FAIL), and deviation.
        """
        results = []
        for kpi in kpis:
            name = kpi.get("kpi_name", "Unnamed KPI")
            field = kpi.get("field", "")
            target = float(kpi.get("target_value", 0))
            operator = kpi.get("operator", ">=")
            department = kpi.get("department", "Compliance")
            severity = kpi.get("severity", "MEDIUM")

            # Try to match field in metrics
            matched_col = None
            for col in metrics.keys():
                if col.lower() == field.lower():
                    matched_col = col
                    break

            if not matched_col or not metrics[matched_col]:
                # Fallback: if field not found, actual is 0
                actual = 0.0
                status = "FAIL"
                deviation = target
            else:
                values = metrics[matched_col]
                # Default aggregation is mean
                actual = sum(values) / len(values)
                
                # Assess based on operator
                if operator == ">=":
                    passed = actual >= target
                elif operator == ">":
                    passed = actual > target
                elif operator == "<=":
                    passed = actual <= target
                elif operator == "<":
                    passed = actual < target
                elif operator == "==":
                    passed = abs(actual - target) < 1e-5
                else:
                    passed = actual >= target

                status = "PASS" if passed else "FAIL"
                deviation = abs(target - actual) if not passed else 0.0

            results.append({
                "kpi_name": name,
                "field": field,
                "target_value": target,
                "operator": operator,
                "actual_value": round(actual, 4),
                "status": status,
                "department": department,
                "severity": severity,
                "deviation": round(deviation, 4)
            })
        return results

    def generate_plan_rule_based(self, kpi_results: List[Dict[str, Any]], csv_text: str, kpi_json_str: str) -> Dict[str, Any]:
        """
        Deterministic fallback generator when LLM is unavailable.
        """
        failures = [k for k in kpi_results if k["status"] == "FAIL"]
        passes = [k for k in kpi_results if k["status"] == "PASS"]
        
        total_kpis = len(kpi_results)
        passed_count = len(passes)
        score = (passed_count / total_kpis * 100) if total_kpis > 0 else 100.0
        
        gaps = []
        roadmap = []
        
        for fail_k in failures:
            gap_desc = f"{fail_k['kpi_name']} is currently at {fail_k['actual_value']}, failing the required target of {fail_k['operator']}{fail_k['target_value']}."
            gaps.append(gap_desc)
            
            # Formulate action
            action_desc = f"Address deviation in {fail_k['kpi_name']}. Investigate column '{fail_k['field']}' and enforce compliance controls."
            if fail_k['severity'] == "CRITICAL":
                timeline = "Immediate (Next 7 days)"
            elif fail_k['severity'] == "HIGH":
                timeline = "Short-term (Next 14 days)"
            else:
                timeline = "Medium-term (Next 30 days)"
                
            roadmap.append({
                "task": action_desc,
                "department": fail_k["department"],
                "priority": fail_k["severity"],
                "timeline": timeline
            })
            
        summary = f"Compliance scorecard shows a pass rate of {score:.1f}%. Detected {len(failures)} compliance gaps that require remediation."
        
        # Build raw markdown report
        md = f"# KPI Compliance Audit Assessment Report\n\n"
        md += f"**Overall Compliance Score: {score:.1f}%**\n"
        md += f"Processed {total_kpis} KPIs. Passes: {passed_count}, Failures: {len(failures)}.\n\n"
        md += "## Detailed KPI Performance\n\n"
        md += "| KPI Name | Target | Actual | Status | Severity | Department |\n"
        md += "|---|---|---|---|---|---|\n"
        for k in kpi_results:
            md += f"| {k['kpi_name']} | {k['operator']}{k['target_value']} | {k['actual_value']} | {k['status']} | {k['severity']} | {k['department']} |\n"
        
        if gaps:
            md += "\n## Identified Compliance Gaps\n\n"
            for g in gaps:
                md += f"- ❌ {g}\n"
                
            md += "\n## Departmental Action Roadmap\n\n"
            for idx, r in enumerate(roadmap):
                md += f"### {idx+1}. [{r['priority']}] {r['task']}\n"
                md += f"- **Department:** {r['department']}\n"
                md += f"- **Timeline:** {r['timeline']}\n\n"
        else:
            md += "\n## All KPIs Satisfied\n"
            md += "No compliance gaps detected. System remains compliant.\n"
            
        return {
            "complianceScore": round(score, 2),
            "kpiResults": kpi_results,
            "summary": summary,
            "gaps": gaps if gaps else ["No gaps detected."],
            "roadmap": roadmap if roadmap else [{
                "task": "Maintain current security and compliance baselines.",
                "department": "Compliance",
                "priority": "LOW",
                "timeline": "Continuous"
            }],
            "rawReport": md
        }

    def _prompt(self, csv_text: str, kpi_json_str: str, results_summary: str) -> str:
        return (
            "You are an AI Compliance & Audit Planner for Canara Bank.\n"
            "Generate a highly professional, detailed Compliance Plan based on the following contexts:\n\n"
            "=== USER'S UPLOADED CSV ===\n"
            f"{csv_text[:2000]}\n\n"
            "=== KPI JSONs ===\n"
            f"{kpi_json_str[:1500]}\n\n"
            "=== CALCULATED METRICS SUMMARY ===\n"
            f"{results_summary}\n\n"
            "Respond in strict JSON format with exactly these fields:\n"
            "{\n"
            "  \"summary\": \"<Detailed overview paragraph of the audit findings and general state of compliance>\",\n"
            "  \"gaps\": [\"<gap description 1>\", \"<gap description 2>\"],\n"
            "  \"roadmap\": [\n"
            "    {\n"
            "      \"task\": \"<concrete action item to fix the gap>\",\n"
            "      \"department\": \"<owner department>\",\n"
            "      \"priority\": \"CRITICAL\" | \"HIGH\" | \"MEDIUM\" | \"LOW\",\n"
            "      \"timeline\": \"<timeline e.g. Immediate (Next 7 days)>\"\n"
            "    }\n"
            "  ],\n"
            "  \"rawReport\": \"<Complete, beautifully styled Markdown report for executive review, including a compliance scorecard table, section details, and the full action roadmap>\"\n"
            "}\n"
            "Make sure your Markdown report is comprehensive and uses rich formatting like headers, lists, and tables."
        )

    async def generate_plan(self, csv_text: str, kpi_json_str: str) -> Dict[str, Any]:
        """
        Executes the full KPI planner agent pipeline.
        Calculates compliance scorecard directly, then enriches roadmap and summary via LLM.
        """
        # Parse inputs
        try:
            kpis = json.loads(kpi_json_str)
        except Exception as e:
            return {"error": f"Invalid KPI JSON: {str(e)}"}

        metrics = self.parse_csv_metrics(csv_text)
        if not metrics:
            return {"error": "Failed to parse CSV or CSV is empty."}

        kpi_results = self.evaluate_kpis(metrics, kpis)
        
        # Calculate base score
        total_kpis = len(kpi_results)
        passed_count = sum(1 for k in kpi_results if k["status"] == "PASS")
        score = (passed_count / total_kpis * 100) if total_kpis > 0 else 100.0

        if not config.llm_enabled():
            logger.info("KPI Planner: LLM disabled, using rule-based generator.")
            return self.generate_plan_rule_based(kpi_results, csv_text, kpi_json_str)

        # Call LLM for rich summaries and roadmaps
        url = config.llm_url()
        headers = {"Content-Type": "application/json"}
        key = config.llm_key()
        if key:
            headers["Authorization"] = f"Bearer {key}"

        results_summary = json.dumps({
            "complianceScore": score,
            "kpiResults": kpi_results
        }, indent=2)

        prompt = self._prompt(csv_text, kpi_json_str, results_summary)
        user_content = f"/no_think {prompt}" if config.llm_no_think() else prompt
        
        body = json.dumps({
            "model": config.llm_model(),
            "messages": [
                {"role": "system", "content": "You are a banking compliance planner. Reply with strict JSON only."},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }).encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=config.llm_timeout()) as resp:
                payload = json.loads(resp.read())
            content = payload["choices"][0]["message"]["content"]
            
            # Clean content & parse JSON
            cleaned = re.sub(r"<think>.*?</think>", "", content, flags=re.IGNORECASE | re.DOTALL).strip()
            cleaned = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", cleaned, flags=re.IGNORECASE)
            
            # Walk balanced braces if simple parsing fails
            parsed = None
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError:
                # Naive walk for JSON object
                i = cleaned.find("{")
                j = cleaned.rfind("}")
                if i != -1 and j != -1:
                    try:
                        parsed = json.loads(cleaned[i:j+1])
                    except json.JSONDecodeError:
                        pass
            
            if not parsed or not isinstance(parsed, dict) or "roadmap" not in parsed:
                raise ValueError("LLM response lacks expected JSON structure")

            # Merge direct calculations with LLM writing
            return {
                "complianceScore": round(score, 2),
                "kpiResults": kpi_results,
                "summary": parsed.get("summary", f"Calculated compliance score of {score:.1f}%."),
                "gaps": parsed.get("gaps", [r["kpi_name"] for r in kpi_results if r["status"] == "FAIL"]),
                "roadmap": parsed.get("roadmap", []),
                "rawReport": parsed.get("rawReport", "")
            }

        except Exception as exc:
            logger.warning("LLM KPI Planning failed (%s). Falling back to rule-based.", exc)
            return self.generate_plan_rule_based(kpi_results, csv_text, kpi_json_str)
