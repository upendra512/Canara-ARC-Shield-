# Canara ARC Shield

**A**I-powered **R**egulatory **C**ompliance & audit platform. ARC Shield ingests a banking
regulatory circular (PDF), drives it through a three-stage AI pipeline, and seals every step
into a tamper-evident audit ledger backed by Hyperledger Fabric.

```
PDF circular ─► Intelligence ─► MAP Engine ─► Verification ─► Trust Ledger ─► Dashboards
               (classify +     (impact +      (control        (hash-linked    (executive,
                clauses)        routing)        evidence)        audit chain)    copilot, RBAC)
```

---

## What's in this repo

ARC Shield is a small fleet of services. One orchestrator (TypeScript) owns intake, the
pipeline, and the trust layer; three Python AI nodes do the reasoning; a React app is the
cockpit; Hyperledger Fabric is the trust anchor.

| # | Service | Tech | Port | Role |
|---|---------|------|------|------|
| — | **frontend** | React + Vite + Tailwind | `5173` | Dashboards, circular explorer, copilot, trust center |
| — | **backend** | Node.js + Express + TypeScript | `4000` | Intake, orchestration, trust ledger, read APIs, RBAC |
| 1 | **node1_intelligence** | FastAPI (Python) | `8001` | Classify circular, extract obligation clauses, copilot answers (LLM) |
| 2 | **node2_map_engine** | FastAPI (Python) | `8002` | Diff obligations, score impact, route to departments (MAPs) |
| 3 | **node3_verification_engine** | FastAPI (Python) | `8003` | Verify MAPs against a controls knowledge base (PASS/REVIEW/FAIL) |
| — | **fabric** | Hyperledger Fabric 2.5 | `7051` peer | On-chain `audit-ledger` chaincode (chain of custody) |

The backend reaches each node over HTTP through an **adapter** with an env-configured base URL.
The trust layer runs on **Hyperledger Fabric** (`FABRIC_ENABLED=true`) — every pipeline stage is
sealed on-chain, which is the point of an audit platform. A local hash-chain backend exists only
as a development fallback when Docker is unavailable. Nodes 2 and 3 are fully deterministic/offline;
node 1 optionally enriches titles and answers a copilot query via a local **Ollama** model, and
degrades to a rule-based result if the model is unavailable.

---

## The pipeline

One circular moves through a state machine, and every transition appends a block to the audit
chain:

```
RECEIVED → CLASSIFYING (N1) → MAPPING (N2) → VERIFYING (N3) → SEALED (Trust) → COMPLETE
```

| Stage | Owner | Produces | Ledger event |
|-------|-------|----------|--------------|
| Intake | backend | Circular + extracted text + own/cited refs | `CIRCULAR_RECEIVED` |
| Classifying | node 1 | Title, regulator, sections, obligation clauses | `MAP_GENERATED`* |
| Mapping | node 2 | Compliance MAPs (impact, department, deadline) | `VERIFICATION_EXECUTED`* |
| Verifying | node 3 | Verdicts (PASS/REVIEW/FAIL) + evidence | `EVIDENCE_COLLECTED` |
| Sealing | backend | Audit receipt | `AUDIT_RECEIPT` |

\* The ledger records each stage's completion; the event name marks the boundary crossed.

Long-running agent calls run as queued jobs; the API returns immediately and the client polls
`/api/circulars/:id/pipeline` for status.

---

## Prerequisites

- **Node.js** 20+ and **npm**
- **Python** 3.11+
- **Docker Desktop** with the **WSL2** backend (Ubuntu) — required for Hyperledger Fabric
- **Go** (inside WSL) — Fabric vendors the Go chaincode during deploy
- **Ollama** (optional) — for node 1 LLM enrichment + copilot; runs fine without it

> **Windows note:** the Fabric test-network must run under **WSL2**, not native Windows.
> All `fabric/scripts/*.sh` are run from a WSL Ubuntu shell against the repo at `/mnt/c/...`.

---

## Quick start

Run each block in its own terminal. From the repo root unless noted.

### 1. Install dependencies

```bash
# Backend
cd backend && npm install && cd ..

# Frontend
cd frontend && npm install && cd ..

# Python nodes (one shared venv is fine; only node 1 has external deps)
pip install -r node1_intelligence/requirements.txt
```

### 2. Activate the Hyperledger Fabric trust layer (required)

The audit ledger runs on real Hyperledger Fabric. Start it before the backend. From a
**WSL2 Ubuntu** shell (Docker Desktop must be running):

```bash
# first ever run only: download fabric-samples + binaries + images (~1.5GB)
bash /mnt/c/hack/Canara-ARC-Shield-/fabric/scripts/up.sh

# every run after: one idempotent command brings the chain up + smoke-tests it
bash /mnt/c/hack/Canara-ARC-Shield-/fabric/scripts/start-blockchain.sh
```

`start-blockchain.sh` ends with `VerifyChain -> {"valid":true,"brokenAt":-1}` when the
chain is live. `backend/.env` already ships with `FABRIC_ENABLED=true` and the Org1
connection paths, so the backend connects automatically.

To tear the network down later: `bash /mnt/c/hack/Canara-ARC-Shield-/fabric/scripts/down.sh`.

> Development-only fallback: if Docker is unavailable, set `FABRIC_ENABLED=false` in
> `backend/.env` to use a local hash-chain ledger instead. Not for real use.

### 3. Start the three AI nodes

From the repo root, with `PYTHONPATH` set to the repo so the packages resolve:

```bash
# bash
export PYTHONPATH=$(pwd)
python -m uvicorn node1_intelligence.api:app --port 8001 &
python -m uvicorn node2_map_engine.api:app   --port 8002 &
python -m uvicorn node3_verification_engine.api:app --port 8003 &
```

```powershell
# PowerShell
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn node1_intelligence.api:app --port 8001
python -m uvicorn node2_map_engine.api:app   --port 8002
python -m uvicorn node3_verification_engine.api:app --port 8003
```

Confirm each is up: `GET http://localhost:8001/health` (and 8002, 8003).

### 4. Start the backend and frontend

```bash
cd backend && npm run dev      # http://localhost:4000
cd frontend && npm run dev     # http://localhost:5173
```

Open **http://localhost:5173**.

---

## Configuration

### backend/.env

| Var | Purpose | Default |
|-----|---------|---------|
| `PORT` | Backend HTTP port | `4000` |
| `NODE1_URL` / `NODE2_URL` / `NODE3_URL` | Agent node base URLs | `http://localhost:800{1,2,3}` |
| `COPILOT_URL` | Copilot answer service (node 1) | `http://localhost:8001` |
| `AGENT_TIMEOUT_MS` | Per-call timeout to nodes | `20000` |
| `FABRIC_ENABLED` | Use Fabric ledger vs. local hash-chain | `true` |
| `FABRIC_CHANNEL` / `FABRIC_CHAINCODE` | Channel + chaincode names | `auditchannel` / `audit-ledger` |
| `FABRIC_*_PATH` / `FABRIC_*_DIR` | Org1 TLS cert, signcert, keystore paths | (from `print-connection.sh`) |
| `CACHE_DASHBOARD_TTL_MS` | Dashboard cache TTL | `15000` |

### frontend/.env

| Var | Purpose | Default |
|-----|---------|---------|
| `VITE_API_BASE_URL` | Backend API base | `http://localhost:4000/api` |

### node1_intelligence/.env (optional LLM)

Point `NODE1_LLM_URL` at a local Ollama (`http://localhost:11434/v1/chat/completions`) and set
`NODE1_LLM_MODEL` (e.g. `qwen3.5:9b`). Blank `NODE1_LLM_URL` to run node 1 purely rule-based.

---

## API surface (backend)

Envelope: every response is `{ ok, data }` or `{ ok, error }`. Role is sent via the `x-role`
header (`compliance` | `it` | `cxo` | `auditor`).

| Method | Path | Serves |
|--------|------|--------|
| GET  | `/api/health` | Liveness probe |
| POST | `/api/circulars` | Upload + intake a circular PDF (multipart `file`) |
| GET  | `/api/circulars` | List circulars |
| GET  | `/api/circulars/:id` | One circular |
| POST | `/api/circulars/:id/process` | Kick off the async pipeline |
| GET  | `/api/circulars/:id/pipeline` | Pipeline record (intelligence, maps, verifications, receipt) |
| GET  | `/api/circulars/:id/references` | Reference graph (cites / cited-by) |
| GET  | `/api/dashboard/summary` | Executive metrics (cached) |
| GET  | `/api/dashboard/role/:role` | MAPs + verifications for a role |
| GET  | `/api/ledger/chain` | Full hash-linked ledger |
| GET  | `/api/ledger/verify` | Chain integrity check |
| GET  | `/api/ledger/custody/:refId` | Chain of custody for one circular |
| POST | `/api/copilot/ask` | RAG answer with citations + verification status |

---

## Project layout

```
Canara-ARC-Shield-/
  backend/                  Orchestrator + intake + trust layer (TypeScript)  → see backend/CLAUDE.md
  frontend/                 React cockpit (Vite)
  node1_intelligence/       FastAPI — classify + extract clauses + copilot
  node2_map_engine/         FastAPI — compliance MAP generation
  node3_verification_engine/ FastAPI — control verification
  fabric/
    chaincode/audit-ledger/ Go chaincode (RecordBlock / GetChain / GetByRef / VerifyChain)
    scripts/                up.sh, down.sh, print-connection.sh
    fabric-samples/         Hyperledger test-network (downloaded on first up.sh)
  mock_db.json              Shared clause/MAP store for node 2
```

The backend's design rules, HLD, LLD, and module contracts live in **`backend/CLAUDE.md`**.

---

## Verifying the system end-to-end

With all services up:

```bash
# 1. health of every node + backend
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:4000/api/health

# 2. upload a circular (compliance role)
curl -X POST http://localhost:4000/api/circulars \
  -H "x-role: compliance" -F "file=@path/to/circular.pdf"
#    → returns { ok:true, data:{ id, ... } }

# 3. run the pipeline, then poll status
curl -X POST http://localhost:4000/api/circulars/<id>/process -H "x-role: compliance"
curl http://localhost:4000/api/circulars/<id>/pipeline

# 4. confirm the audit chain sealed and is intact
curl http://localhost:4000/api/ledger/verify        # → { valid: true }
curl http://localhost:4000/api/ledger/custody/<id>  # chain of custody for the circular
```

In the UI: upload on **Circular Explorer**, watch it move to COMPLETE, then check
**Executive Dashboard**, **Blockchain Trust Center** (chain + integrity), **Role Workspace**,
and **Compliance Copilot**.
