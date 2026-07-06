import { config } from "../config/index.js";
import type { Clause, ComplianceMap, Regulator } from "../types/domain.js";
import { postJson } from "./httpClient.js";
import { fail } from "../utils/errors.js";

export interface BaselineClause {
  section: string;
  title: string;
  text: string;
  sourceCircularId: string;
}

export interface MapRequest {
  circularId: string;
  regulator: Regulator | null;
  circularDate: string | null;
  clauses: Clause[];
  baseline: BaselineClause[];
}

export const node2 = {
  async generate(req: MapRequest): Promise<ComplianceMap[]> {
    if (!config.agents.node2Url) {
      throw fail("UPSTREAM_ERROR", "NODE2_URL is not configured");
    }
    return postJson<ComplianceMap[]>(`${config.agents.node2Url}/map`, req);
  },

  async generateKPIPlan(csvText: string, kpisJson: string): Promise<KPIPlan> {
    if (!config.agents.node2Url) {
      throw fail("UPSTREAM_ERROR", "NODE2_URL is not configured");
    }
    return postJson<KPIPlan>(`${config.agents.node2Url}/kpi/plan`, {
      csvText,
      kpisJson,
    });
  },
};

export interface KPIResult {
  kpi_name: string;
  field: string;
  target_value: number;
  operator: string;
  actual_value: number;
  status: string;
  department: string;
  severity: string;
  deviation: number;
}

export interface KPITask {
  task: string;
  department: string;
  priority: string;
  timeline: string;
}

export interface KPIPlan {
  complianceScore: number;
  kpiResults: KPIResult[];
  summary: string;
  gaps: string[];
  roadmap: KPITask[];
  rawReport: string;
}

