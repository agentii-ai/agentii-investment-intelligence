# Subagent Handoff Contract (v1.0 frozen)

Human-readable companion to `failure-policy.yaml` + `evidence-pack.schema.json` + `../subagents/*.yaml`. Codifies which Cowork subagent produces/consumes which artifact, the invocation order, and the fail-safe semantics for each handoff edge. Per **the inter-subagent handoff contract** (subagent decomposition by capability axis, not by task name) + **the failure-recovery policya** (max-1-bounce policy, deterministic halts).

## Subagents

Four YAML-defined Cowork subagents, each capability-isolated:

| Subagent | Capability axis | MAY do | MUST NOT do |
|---|---|---|---|
| `retrieval-subagent` | Data gathering | Call data-plane MCP tools (`search_*`, `get_*`, `read_*`); shape evidence pack | Call any office-plane tool; author analytical prose; use Write tool |
| `analytical-subagent` | Reasoning + .md authoring + xlsx_spec construction | Read evidence pack; write deliverable `.md`; emit `xlsx_spec.json` | Execute office tools; gather new data; deliver final workbook |
| `bi-subagent` | Business-intelligence reasoning + scenario sensitivity reads | Read evidence pack; run scenario calculations; emit BI deliverables | Execute office tools; gather new data |
| `visualization-subagent` | Office-plane execution + final deliverable rendering | Invoke `xlsx.*` / `pptx.*` tools per `tool_alias_map`; deliver R2-presigned URLs | Gather data; author independent analytical prose |

**Capability axis** (the capability-isolated subagent decomposition) — decomposition is by *what the subagent can do* (retrieve / reason / render), not by *what task it serves* (DCF / comps / pitch). The same `analytical-subagent` handles every dimension's analytical work; the same `visualization-subagent` renders every workbook.

## Invocation order (deterministic)

```
 ┌────────────────────┐
 user request │ parent agent │ agentii-equity-agent.md
 ──────► │ (orchestrator) │ decides dimension(s)
 └─────────┬──────────┘
 │
 ▼
 ┌────────────────────┐
 │ retrieval-subagent │ ALWAYS first
 └─────────┬──────────┘
 │ evidence_pack.json (the inter-subagent handoff contract)
 ▼
 ┌─────────────────────────────┐
 │ analytical OR bi subagent │ (based on dim/skill kind)
 │ — never both in parallel │
 └─────────────┬───────────────┘
 │ deliverable.md (+ xlsx_spec.json if applicable)
 ▼
 ┌─────────────────────────────┐
 │ visualization-subagent │ (only if office plane invoked)
 │ — runs xlsx.audit FIRST │
 └─────────────┬───────────────┘
 │ R2 URLs (.xlsx, .pptx)
 ▼
 user reply
```

**Invariant**: `retrieval-subagent` ALWAYS precedes any reasoning subagent. the hard gate against hardcoded cells hard-gate is a *process* invariant (orchestrator refuses to invoke analytical/bi before evidence pack exists), not a *prompt* convention. This is the entire reason for the the capability-isolated subagent decomposition capability-axis decomposition.

## Handoff edges

### Edge A: parent → `retrieval-subagent`

- **Input**: user query, target dimension(s), `tickers[]`, `--peers=` (if any), `--mode=`/`--modes=` (if any)
- **Output**: `evidence_pack.json` conforming to `evidence-pack.schema.json` v1.0
- **Failure**: see `failure-policy.yaml#failures.retrieval_gaps` — partial evidence pack is acceptable; `coverage_attestation.gaps[]` documents what was missing
- **Order constraint**: this is always the first subagent call; orchestrator MUST refuse parallel analytical/bi invocations until the retrieval pack lands

### Edge B: `retrieval-subagent` → `analytical-subagent`

- **Input**: `evidence_pack.json`, dimension methodology (resolved from skill's `## Mode: <slug>` body), target output mode list
- **Output**: deliverable `.md` (per skill's `## Output Structure`) + optional `xlsx_spec.json` (for `models-and-pitches` skills)
- **Failure**: `analytical_context_exhausted` (chunk by ticker → demote model → halt with `AGENTII_ANALYTICAL_EXHAUSTED`) and `analytical_api_failure` (30s backoff → halt with `AGENTII_ANALYTICAL_API_FAILURE`)

### Edge B': `retrieval-subagent` → `bi-subagent`

- Mirror of Edge B but for `business-intelligence` vertical skills. Same evidence pack format. Same failure modes. `bi-subagent` does NOT emit `xlsx_spec.json`; it emits BI deliverables (revenue waterfall, KPI dashboard) inline as Markdown tables.

### Edge C: `analytical-subagent` → `visualization-subagent`

- **Input**: deliverable `.md`, `xlsx_spec.json` (per `xlsx_spec.schema.json`), `pptx_spec.json` (per `pptx_spec.schema.json`)
- **Output**: presigned R2 URLs for rendered `.xlsx` / `.pptx`
- **Hard gate**: `visualization-subagent` MUST invoke `xlsx.audit` BEFORE `xlsx.build`. If audit reports a hardcoded projection cell:
 1. Return audit report to `analytical-subagent`. Analytical revises the `xlsx_spec` to replace hardcoded values with formula expressions.
 2. **MAX 1 bounce** (`failure-policy.yaml#failures.audit_hardcode_fail`). On second audit failure, halt with `AGENTII_AUDIT_HARDCODE_FAIL` and deliver ZERO workbook (the spec attached for human review).
- **Recalc timeout** (`recalc_timeout`): retry once with `safe_mode:true`; halt with `AGENTII_RECALC_TIMEOUT` on second failure.

### Edge D: any subagent → halt

- **Halt error codes** (the auth-required error contract stable, the failure-recovery policya frozen): `AGENTII_ANALYTICAL_EXHAUSTED`, `AGENTII_ANALYTICAL_API_FAILURE`, `AGENTII_AUDIT_HARDCODE_FAIL`, `AGENTII_RECALC_TIMEOUT`, `AGENTII_SPEC_VERSION_MISMATCH`.
- **Never silent**: every halt MUST emit (i) the error code, (ii) the user-facing message from `failure-policy.yaml`, (iii) a telemetry event per the telemetry emission contract with `error_code` populated.
- **No auto-coercion**: `AGENTII_SPEC_VERSION_MISMATCH` halts immediately — no schema migration is attempted across version boundaries.

## Cross-references

| Failure policy entry | Owning edge | Affected subagent(s) |
|---|---|---|
| `retrieval_gaps` | Edge A | retrieval-subagent (action_1: widen window; action_2: proceed with gaps) |
| `analytical_context_exhausted` | Edge B / Edge B' | analytical / bi (action_1: chunk by ticker; action_2: demote model; halt) |
| `analytical_api_failure` | Edge B / Edge B' | analytical / bi (action_1: 30s backoff retry; halt) |
| `audit_hardcode_fail` | Edge C | visualization → analytical bounce (max 1; halt) |
| `recalc_timeout` | Edge C | visualization (action_1: safe_mode retry; halt) |
| `spec_version_mismatch` | Any edge | all (halt_immediate; no auto-migration) |

## Validation

- `scripts/check.py` Check 4 verifies `subagents/*.yaml` files reference existing tools and skills.
- `scripts/test-cookbooks.sh` dry-runs `deploy-managed-agent.sh --dry-run` and asserts depth-1 constraint (no subagent declares `callable_agents[]`).
- `scripts/validate.py` validates `failure-policy.yaml` against `failure-policy.schema.json`.
- Manual review checkpoint: every PR touching this document OR the schemas requires a SECOND reviewer per `.constitution` Principle V (Frozen Contracts).
