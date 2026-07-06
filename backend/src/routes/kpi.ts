import { Router } from "express";
import { asyncHandler, sendOk, param } from "../utils/http.js";
import { fail } from "../utils/errors.js";
import { requireRole } from "../middleware/auth.js";
import { node2 } from "../adapters/node2MapEngine.js";
import { kpiStore, type KPIAuditReport } from "../store/kpiStore.js";
import { ledgerBackend } from "../store/ledger/index.js";
import { sha256Of } from "../utils/crypto.js";
import { randomUUID } from "node:crypto";

export const kpiRouter = Router();

// Endpoint: Generate Compliance plan from CSV + JSON
kpiRouter.post(
  "/plan",
  requireRole("compliance"),
  asyncHandler(async (req, res) => {
    const { csvText, kpisJson } = req.body as { csvText?: string; kpisJson?: string };
    if (!csvText || !csvText.trim()) {
      throw fail("BAD_REQUEST", "Missing or empty field 'csvText'");
    }
    if (!kpisJson || !kpisJson.trim()) {
      throw fail("BAD_REQUEST", "Missing or empty field 'kpisJson'");
    }

    // Call Node 2 to run calculations + AI evaluation
    const plan = await node2.generateKPIPlan(csvText, kpisJson);

    // Create a new Audit Report record
    const reportId = `kpi_${randomUUID()}`;
    const report: KPIAuditReport = {
      id: reportId,
      timestamp: new Date().toISOString(),
      csvText,
      kpisJson,
      plan,
      sealed: false,
      ledgerHash: null,
    };

    // Save report in state
    await kpiStore.saveReport(report);
    sendOk(res, report, 201);
  })
);

// Endpoint: Seal the plan on blockchain (tamper-evident audit ledger)
kpiRouter.post(
  "/:id/seal",
  requireRole("compliance"),
  asyncHandler(async (req, res) => {
    const id = param(req, "id");
    const report = await kpiStore.getReport(id);
    if (!report) {
      throw fail("NOT_FOUND", `Unknown KPI Report: ${id}`);
    }
    if (report.sealed) {
      throw fail("CONFLICT", `Report ${id} is already sealed`);
    }

    // Calculate cryptographic payload hash
    const payloadHash = sha256Of(report.plan);

    // Commit transaction to Hyperledger Fabric or local hash-chain
    const block = await ledgerBackend.append("KPI_AUDIT_SEALED", id, payloadHash);

    // Update state to record sealing status and block hash
    const updated = await kpiStore.updateReport(id, {
      sealed: true,
      ledgerHash: block.hash,
    });

    sendOk(res, {
      report: updated,
      block,
    });
  })
);

// Endpoint: List all reports
kpiRouter.get(
  "/",
  asyncHandler(async (_req, res) => {
    const reports = await kpiStore.listReports();
    sendOk(res, reports);
  })
);

// Endpoint: Retrieve single report
kpiRouter.get(
  "/:id",
  asyncHandler(async (req, res) => {
    const id = param(req, "id");
    const report = await kpiStore.getReport(id);
    if (!report) {
      throw fail("NOT_FOUND", `KPI Report not found: ${id}`);
    }
    sendOk(res, report);
  })
);
