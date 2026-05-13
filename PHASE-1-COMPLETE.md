# Phase 1 Complete (T001–T043)

Spec: `specs/023-agentii-financial-analysis/tasks.md`
Status: All 43 Phase-1 tasks delivered. CI green.

## What ships in Phase 1

### Repository skeleton
- `.claude-plugin/marketplace.json` — 5 plugins declared
- `LICENSE` (Apache 2.0), `NOTICE` (upstream attribution preamble)
- `.gitignore`, `.github/workflows/ci.yml`, `.github/workflows/release.yml`

### 5 plugin manifests
- `plugins/vertical-plugins/equity-research-core/.claude-plugin/plugin.json`
- `plugins/vertical-plugins/business-intelligence/.claude-plugin/plugin.json`
- `plugins/vertical-plugins/industry-analysis/.claude-plugin/plugin.json`
- `plugins/vertical-plugins/models-and-pitches/.claude-plugin/plugin.json`
- `plugins/agent-plugins/agentii-equity-agent/.claude-plugin/plugin.json`

### Contracts (frozen v1.0)
- `contracts/tool-name-map.json` — system_v2_7 + upstream_fsi rewrites + citation rules + preflight templates
- `contracts/sharp-edges.yaml` — 5 catalogued sharp edges
- `contracts/prose-safety.md` — FR-020e prose constraints
- `contracts/telemetry.schema.json` — FR-053 frozen event schema
- `contracts/agentii-config.schema.json` — `~/.agentii/config.json` schema

### Partner-built reservation
- `plugins/partner-built/README.md` (curation criteria)
- `plugins/partner-built/partner-plugin-spec.md` (technical requirements)

### CLI surface docs
- `docs/cli-surfaces/telemetry-and-inspect.md` — `agentii plugin telemetry` + `inspect`

### 11 scripts (5 ported + 6 new + 4 port-scaffolds)
Ported from `anthropics/financial-services` (Apache 2.0):
- `scripts/check.py` (extended with 12 SKILL.md structural checks)
- `scripts/validate.py`
- `scripts/sync-agent-skills.py`
- `scripts/deploy-managed-agent.sh`
- `scripts/test-cookbooks.sh` (with Phase-1 tolerance for empty cookbooks)

New validators (FR-020e, FR-050, FR-052b, FR-053b, FR-054b, FR-049):
- `scripts/validate-citations.py`
- `scripts/validate-mode-syntax.py`
- `scripts/validate-multi-ticker-syntax.py`
- `scripts/validate-telemetry-redaction.py`
- `scripts/validate-prose-safety.py`
- `scripts/validate-partner-plugin.py`

Port-script scaffolds (full impl in Phase 3/4/6/7):
- `scripts/port-system-prompt.py` (Phase 6 / US6)
- `scripts/port-dimension-prompts.py` (Phase 3 / US2)
- `scripts/sync-from-upstream.py` (Phase 4 / US3)
- `scripts/render-cookbook.py` (Phase 7 / US7)

Bootstrap helper:
- `scripts/bootstrap-scaffolds.py` — generated the 24 SKILL.md + 21 command files

### 24 SKILL.md scaffolds
All have valid frontmatter (name, description, multi_ticker_semantics) and the
6 mandatory sections (Preflight, Triggers, Defaults, Methodology, Output
Structure, Error Handling). Methodology is intentionally empty pending
Phase 3/4/5 authoring.

| Vertical | Skills |
|---|---|
| equity-research-core | 8 dimensions: dim-recent-quarter-performance, dim-competitive-landscape, dim-growth-strategy, dim-secular-tech-trends, dim-turnaround-stagnation, dim-risk-analysis, dim-earnings-sentiment, dim-valuation-methods |
| business-intelligence | 5: business-model-analysis, revenue-decomposition, unit-economics, what-if-scenario, operational-kpi-tracker |
| industry-analysis | 4: peer-benchmarking, sector-overview, competitive-positioning, supply-chain-map |
| models-and-pitches | 7: dcf-model, comps-analysis, 3-statement-model, lbo-model, audit-xls, xlsx-author, pitch-deck |

### 21 command files
Frontmatter (description + argument-hint) + placeholder ## Workflow.

## Verification (T041–T043)

All seven validators exit 0:

```
=== check ===                            OK — 36 file(s), 0 issues.
=== validate-citations ===               OK — 47 file(s), 0 violations.
=== validate-mode-syntax ===             OK — 24 skill(s), 0 violations.
=== validate-prose-safety ===            OK — 45 file(s), 0 violations.
=== validate-multi-ticker-syntax ===     OK — 24 skill(s), 0 violations.
=== validate-telemetry-redaction ===     OK — 0 emission file(s), 0 violations.
=== validate-partner-plugin ===          OK — partner-plugin checks passed.
```

`bash scripts/test-cookbooks.sh` exits 0 (cookbook not yet populated; tolerated).

## Local verification

The repo uses Python 3.12+ with `pyyaml` and `jsonschema`. On macOS / Homebrew
Python (PEP 668), use a venv:

```bash
python3 -m venv .venv
.venv/bin/pip install pyyaml jsonschema
.venv/bin/python3 scripts/check.py
```

CI uses `actions/setup-python@v5` and a fresh pip install; no venv needed.

## What does NOT ship in Phase 1

The following are deliberately deferred:

- **Methodology bodies** — every SKILL.md has a `## Methodology` placeholder.
  Authored in Phase 3 (equity-research-core, US2), Phase 4 (models-and-pitches,
  US3), and Phase 5 (business-intelligence + industry-analysis, US4/5).
- **Agent system prompt** — `port-system-prompt.py` is a scaffold. Phase 6 (US6).
- **Managed-agent cookbook content** — `agent.yaml`, subagent prompts, golden
  fixtures all populated in Phase 7 (US7).
- **CLI install docs for non-Claude-Code hosts** — Phase 8.
- **Release artifacts and Sigstore signing** — Phase 9.
- **MCP server schemas** — `.mcp.json` files for each vertical, evidence-pack /
  failure-policy / xlsx_spec / pptx_spec JSON Schemas. These are Phase 2 (T044–T059).

## Coexistence with the existing MCP server stub

The existing `tools/`, `adapters/`, `SKILL.md`, and `README.md` (single-file
spec-024 distribution path) are preserved unchanged at the repo root. The
spec-023 plugin/marketplace architecture lives alongside in `plugins/`,
`managed-agent-cookbooks/`, `contracts/`, `scripts/`, `docs/`, and `.claude-plugin/`.

The README.md still references MIT — this conflicts with the new Apache 2.0
LICENSE required by FR-029. Reconcile in Phase 2 by either:
1. Splitting into two licensed artifacts (MCP server stays MIT in `tools/`,
   plugin package is Apache 2.0), or
2. Re-licensing the whole repo to Apache 2.0.

## Next steps

Per spec 023 Phase 2 (T044–T059):
1. Author 4 JSON Schemas (`evidence-pack`, `failure-policy`, `xlsx_spec`, `pptx_spec`).
2. Author 2 `.mcp.json` files (data-plane + office-plane MCP server declarations).
3. Author agentic-commerce forward-compat test fixtures (FR-006a).
4. Wire Preflight snippets into the 24 scaffold SKILL.md files.
