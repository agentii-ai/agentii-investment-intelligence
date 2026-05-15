# Cross-references: agentii dims ↔ financial-services skills

Per spec 023 T060b (Round 3 cross-reference exercise). Each `equity-research-core` dimension is informally analogous to a task-shaped skill in `anthropics/financial-services/plugins/vertical-plugins/equity-research/skills/`. The analogs are **inspirational only — NOT a port path**. The agentii dimensions are designed for analytical *breadth* (8 dimensions × 4–9 sub-prompt modes each = 48 modes); the upstream financial-services skills are designed for analytical *workflows* (earnings-preview → morning-note → catalyst-calendar).

Every dimension SKILL.md surfaces its analog reference in an `<!-- analog: <skill-name> -->` HTML comment immediately below the frontmatter for auditability.

## Mapping table

| agentii dimension | Analog in `financial-services/equity-research/` | Rationale |
|---|---|---|
| `dim-recent-quarter-performance` | `earnings-preview` / `morning-note` | Both produce a post-print summary anchored to a single fiscal period. agentii adds explicit sub-prompt addressability for revenue/margin/EPS/guidance breakdowns. |
| `dim-competitive-landscape` | `sector-overview` | Both situate a target in its peer set. agentii is per-name with optional peers; the upstream skill is sector-wide. |
| `dim-growth-strategy` | `initiating-coverage` (growth-strategy sub-section) | Both assess TAM expansion, M&A capacity, capital deployment. agentii decomposes into 5 sub-prompts (organic/inorganic/TAM/pipeline/capital-discipline). |
| `dim-secular-tech-trends` | `idea-generation` | Both identify which secular trends a company rides. agentii ports the 5-trend taxonomy (AI / data / EV / automation / renewable energy) from the prompt set. |
| `dim-turnaround-stagnation` | `thesis-tracker` | Both compare current performance against a thesis baseline. agentii's `target_with_required_peers` semantics make peer comparison mandatory (turnaround framing is meaningless solo). |
| `dim-risk-analysis` | (no direct analog; closest: `risk-factors-summary` within `morning-note`) | Risk analysis is a cross-cutting concern in the upstream design; agentii promotes it to a top-level dimension with its own 4 sub-prompts. |
| `dim-earnings-sentiment` | `earnings-analysis` / `catalyst-calendar` | Both analyze call transcripts and Q&A tone. agentii decomposes into 6 sub-prompts (tone / surprise / guide-cut / Q&A-quality / forward-statement-rate / catalyst-density). |
| `dim-valuation-methods` | `initiating-coverage` (valuation section) / `model-update` | Both apply DCF / comps / precedent-transaction valuation. agentii has 3 sub-prompts (DCF, comps, sum-of-parts) and links to `models-and-pitches` for live workbook generation. |

## Why these are inspirational and NOT port paths

1. **Tool surface differs**: financial-services skills reference Daloopa / FactSet / S&P Global MCP connectors. agentii skills reference the spec-019 `mcp.agentii.ai` data plane backed by Neon-hosted `gold.*` schemas. The data-source blocks in `plugins/vertical-plugins/*/data-source-blocks/` are NEW — no upstream analog.

2. **Decomposition philosophy differs**: financial-services models analytical *workflows* (sequence of tasks). agentii models analytical *dimensions* (each dimension is independently addressable; sub-prompts within a dimension share methodology + data context).

3. **Citation format differs**: upstream uses Daloopa / FactSet citation tuples. agentii is frozen at FR-050 (`[📄 TICKER FORM p.N](agentii://source/UUID?accession=ACC&page=N)`).

4. **Multi-ticker semantics are explicit at agentii v1.0** (FR-054). The upstream design implicitly treats every skill as single-target.

5. **Mode addressability** (`--mode=<slug>`, `--modes=...`, `--mode=all`) is an agentii v1.0 invention; upstream commands are monolithic.

## What WAS ported from financial-services

The `models-and-pitches` vertical (DCF / comps / 3-statement / LBO / audit-xls / xlsx-author / pitch-deck — 7 skills) is a true port from `financial-services/plugins/vertical-plugins/financial-modeling/skills/`. Those skills retain their upstream commit SHA in `.upstream-pin.yaml` and pass through `scripts/sync-from-upstream.py` with `tool-name-map.json` rewrites and data-source-block overrides. See Phase 4 tasks.

## Audit guidance

When reviewing or extending an agentii dimension:

- Read the analog skill at `/Users/frank/A/agenzym/financial-services/plugins/vertical-plugins/equity-research/skills/<analog>/SKILL.md` for inspiration on workflow shape, output structure, and error-handling conventions.
- Do NOT copy the analog's data-source block, MCP connector references, or citation format.
- Do NOT consider the analog as authoritative on methodology — the agentii sub-prompts (sourced from `references/prompts/<N>/`) are the analyst-curated source of truth.
