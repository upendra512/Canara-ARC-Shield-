# Node 1 — Regulatory Intelligence Engine

External agent microservice for the ARC Shield pipeline. Given a circular's raw
text, it classifies the document and extracts obligation clauses, returning one
`IntelligenceResult` shaped to `backend/src/types/domain.ts`. The backend reaches
it over HTTP at `NODE1_URL` (`POST /analyze`); it does no orchestration itself.

Position in the pipeline:

```
Backend intake ──text──► Node 1 (this) ──clauses──► Node 2 MAP ──maps──► Node 3 Verify
```

## What it does

- **Regulator detection** — RBI / SEBI / IRDAI / MCA by keyword signature (RBI default).
- **Domain classification** — scores text against a banking taxonomy of ~18 domains
  (KYC, AML, Information Security, Data Privacy, Capital Adequacy, Treasury, Credit
  Risk, Vendor Risk, Business Continuity, Fraud, Governance, …).
- **Clause extraction** — segments the circular into clause-sized units, keeps the
  obligation-bearing ones (the chunks Node 2 diffs), and tags each with a rule type
  (e.g. `RECORD_RETENTION`, `MFA_REQUIREMENT`, `MINIMUM_CAPITAL`).
- **Circular facts** — title, issued date, regulatory sections, and a best-effort
  similarity to a linked prior circular (token Jaccard).

Deterministic and **offline by default** — the same text always yields the same
verdict, so the audit trail holds. No internet, no LLM required.

## The taxonomy

`taxonomy.json` is the single source of truth: `domain -> rule_types -> keyword
signatures`, plus regulator and obligation-term lists. Add a domain or rule type
by editing this file only; the classifier picks it up with no code change.

## Optional LLM enrichment (local Gemma via Ollama)

Off by default — with no `.env` (or a blank `NODE1_LLM_URL`) Node 1 is purely
rule-based and offline. Point it at a local LLM to refine the circular title and
the per-clause titles into plain English. Any failure or timeout falls back
silently to the rule-based result, so the pipeline never blocks on the model.

Set up with Ollama + Gemma 3 12B (runs on an RTX 4060):

```bash
ollama pull gemma3:12b
# node1_intelligence/.env (gitignored):
#   NODE1_LLM_URL=http://localhost:11434/v1/chat/completions
#   NODE1_LLM_MODEL=gemma3:12b
#   NODE1_LLM_TIMEOUT=120
```

Ollama exposes an OpenAI-compatible API at `/v1/chat/completions`, so the same
hook works with any hosted endpoint — set `NODE1_LLM_KEY` and `NODE1_LLM_MODEL`.

Notes for the RTX 4060 (8GB):
- `gemma3:12b` Q4 (~8GB weights) does not fully fit; Ollama offloads part to CPU.
  Cold load is ~70s, warm calls ~15–20s. The LLM call is off the hot path.
- Node 1 **warms the model at startup**, so the first real request is already
  warm. The model unloads after ~5 min idle; the next call re-warms (covered by
  the 120s timeout, with rule-based fallback if it overruns).
- For a fully-on-GPU, much faster option, switch `NODE1_LLM_MODEL=gemma3:4b`.

Env vars: `NODE1_LLM_URL`, `NODE1_LLM_KEY`, `NODE1_LLM_MODEL`, `NODE1_LLM_TIMEOUT`.

## Run

```bash
pip install -r node1_intelligence/requirements.txt
uvicorn node1_intelligence.api:app --port 8001
```

Then point the backend at it: `NODE1_URL=http://localhost:8001`.

## Test

```bash
python -m node1_intelligence.test_scenarios   # offline, no server
```

## API

| Method | Path       | Body                                              | Returns              |
|--------|------------|---------------------------------------------------|----------------------|
| GET    | `/health`  | —                                                 | liveness             |
| POST   | `/analyze` | `{ circularId, filename, text, context? }`        | `IntelligenceResult` |
