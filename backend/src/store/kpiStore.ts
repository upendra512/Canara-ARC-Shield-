import { config } from "../config/index.js";
import type { KPIPlan } from "../adapters/node2MapEngine.js";
import { Mutex } from "../utils/mutex.js";
import { readJsonFile, writeJsonFileAtomic } from "./persistence.js";
import path from "node:path";

export interface KPIAuditReport {
  id: string;
  timestamp: string;
  csvText: string;
  kpisJson: string;
  plan: KPIPlan;
  sealed: boolean;
  ledgerHash: string | null;
}

interface KPIStateShape {
  reports: Record<string, KPIAuditReport>;
}

const emptyState: KPIStateShape = { reports: {} };

class KPIStore {
  private readonly lock = new Mutex();
  private cache: KPIStateShape = emptyState;
  private loaded = false;
  private readonly kpiStatePath = path.join(config.paths.data, "kpi_state.json");

  private async load(): Promise<void> {
    if (this.loaded) return;
    this.cache = await readJsonFile<KPIStateShape>(this.kpiStatePath, emptyState);
    this.loaded = true;
  }

  private async persist(): Promise<void> {
    await writeJsonFileAtomic(this.kpiStatePath, this.cache);
  }

  async listReports(): Promise<KPIAuditReport[]> {
    await this.load();
    return Object.values(this.cache.reports).sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  async getReport(id: string): Promise<KPIAuditReport | null> {
    await this.load();
    return this.cache.reports[id] ?? null;
  }

  async saveReport(report: KPIAuditReport): Promise<KPIAuditReport> {
    return this.lock.run(async () => {
      await this.load();
      this.cache.reports[report.id] = report;
      await this.persist();
      return report;
    });
  }

  async updateReport(id: string, updates: Partial<KPIAuditReport>): Promise<KPIAuditReport> {
    return this.lock.run(async () => {
      await this.load();
      const report = this.cache.reports[id];
      if (!report) {
        throw new Error(`Unknown KPI report ID: ${id}`);
      }
      this.cache.reports[id] = { ...report, ...updates };
      await this.persist();
      return this.cache.reports[id];
    });
  }
}

export const kpiStore = new KPIStore();
