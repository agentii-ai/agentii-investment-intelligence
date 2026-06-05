# Skill Methodology Template (v1.0)

Canonical `## Methodology` subsection structure for every `SKILL.md` per spec 023 FR-064. All 5 subsections are required and CI-validated (scripts/check.py Check 22). Consumed by `scripts/port-dimension-prompts.py` for auto-generation.

## Required Subsections

### 1. Retrieval Scope

States which FR-056 branch applies:

- **Three-layer protocol applies** (default): this skill performs unstructured document search at scale (candidate document set > 1 filing or > 50 pages). Must encode Layer 1→2→2.5→3 in the Protocol subsection below.
- **`retrieval_scope: structured_only`**: uses only `search_xbrl_facts` / `get_company_financials` / `search_earnings_calendar` — no unstructured document search.
- **`retrieval_scope: single_document`**: user or prior context already identifies the exact document.
- **`retrieval_scope: simple_lookup`**: uses only profile/entity metadata tools.

### 2. Retrieval Strategy

References the retrieval strategy decision tree (FR-057) and declares which of the 4 branches this skill follows:

1. **(a) Structured Data Query** — `search_xbrl_facts` with optional `list_xbrl_concepts` pre-condition for concept discovery.
2. **(b) Multi-Period Unstructured Query** — `search_cross_period` with parallel `period-search-subagent` instances.
3. **(c) Single-Period / Single-Document Query** — direct `read_source_outline` → `read_source_pages`.
4. **(d) Simple Lookup** — `get_company_profile` / `search_earnings_calendar` / `get_entity_knowledge`.

### 3. Temporal Scope

Restates the `temporal_scope` YAML frontmatter block:

- `default_quarters`: number of fiscal quarters searched by default when user does not specify `--lookback=`.
- `max_quarters`: absolute ceiling for `search_cross_period` period list construction.
- `description`: human-readable rationale for why this lookback is appropriate for the analysis.

### 4. Tool Allowlist

Restates the `allowed_tools` YAML frontmatter list with a one-line justification per tool:

- Each tool name matches a canonical MCP surface entry (FR-011 + FR-041).
- Office-plane tools (`xlsx.*`, `pptx.*`) only in `models-and-pitches` skills.
- `retrieval_scope: structured_only` skills exclude document-retrieval tools.

### 5. Protocol

Step-by-step numbered procedure (modeled on `himself65/finance-skills` pattern):

1. **Pre-retrieval** (if multi-period): call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format labels.
2. **Concept discovery** (if structured query with unfamiliar concept): call `list_xbrl_concepts(query=<term>, ticker=<T>)`.
3. **Retrieval**: follow the three-layer protocol if applicable:
   - Layer 1: `search_documents` / `search_sec_filings` to discover candidate filings.
   - Layer 2: `read_source_outline` to scan page-level metadata and identify relevant pages.
   - Layer 2.5 (optional): `search_keyword_in_source` to keyword-filter large documents.
   - Layer 3: `read_source_pages` to deep-read only selected pages.
4. **Multi-period** (if applicable): use `search_cross_period` with parallel `period-search-subagent` instances.
5. **Evidence-pack handoff**: produce `evidence-pack.json` + `evidence-digest.md` per FR-046b.

## Production Reality (spec 023 Phase 17 T269 — 2026-05-25)

The Neon production database and `api.agentii.ai` REST/MCP surfaces are LIVE and AUTHORITATIVE as of 2026-05-25. Every skill MUST treat the following as ground truth and call the FR-075 pre-flight (`get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`) BEFORE any retrieval planning:

- 4.17M `gold.xbrl_facts` (with `is_primary` partial index)
- 11,575 `pipeline.src_documents` (100% non-null `description`, GIN-indexed `secondary_labels`)
- 243K `pipeline.src_silver_pages` covering ALL 5 SEC form types (8-K/10-K/10-Q/6-K/20-F)
- 4,653 `pipeline.earnings_calendar` rows
- 79 `gold.launch_ticker_registry` tickers at 100% processing

Do NOT plan for missing data outside this scope without first calling the pre-flight.

## XBRL Retrieval (spec 023 Phase 17 T256 — supersedes FR-055n)

`search_xbrl_facts` returns `source_authority` (integer 1–3: 3=10-K, 2=10-Q, 1=8-K) and `is_primary` (boolean) on every row.

- The API defaults to `WHERE is_primary = true` via the `idx_xf_primary` partial index — duplicates across multiple SEC disclosures are hidden by default.
- Skills MAY surface `source_authority` in deliverables for fact-provenance transparency.
- Skills MUST NOT re-implement client-side dedup logic — this is now an API-side concern.
- The `?include_all_sources=true` flag is reserved for audit-xls and reconciliation workflows; do NOT pass it from analytical skills.

## Layer 2 Page Discovery (spec 023 Phase 17 T262 — page-relevance scoring contract)

Skills performing unstructured document search at scale MUST follow the three-layer retrieval protocol per `retrieval.md`. The Layer 2 page-relevance scoring contract:

- Score pages using BOTH `description` (semantic match) AND `keywords` (entity match).
- Prefer pages with high keyword density for the dimension's analytical focus (e.g., `business-model` skill prefers pages whose keywords contain product/segment/channel terms).
- Use the `dense` outline format by default: `{ticker} {citation_id} page<N>: <description> [keywords: <kw1>, ...]`.
- Use the `dense_keywords_only` opt-in format (`?format=dense_keywords_only`, ~30% smaller payload) for budget-constrained skills.
- **Bare `page_no` integers are forbidden in any LLM-facing output** — always cite as `{ticker} {citation_id} page<N>`.

## Page Labels JSONB Contract (spec 023 Phase 17 T266)

`pipeline.src_silver_pages.labels` is ONE JSONB column merging the LLM-extracted `general` label set AND every `labels_*` silver-layer folder set. Canonical shape:

```json
{
  "general": {
    "description": "<~100-char LLM-generated page summary>",
    "keywords": ["entity", "term", "..."],
    "category": "<page category>"
  },
  "financial_results": { "...": "..." },
  "guidance": { "...": "..." },
  "...": "..."
}
```

- Skills MUST read `labels->>'general'->>'description'` and `labels->>'general'->>'keywords'` as the primary page-relevance signal.
- Secondary labels under other top-level keys are dimension-specific (e.g., a financial-results-focused skill may also read `labels->>'financial_results'->>'reported_period'`).
- The `general` set is populated on 96%+ of 243K silver-pages rows; secondary `labels_*` sets appear in subsets per the dimension match.

## Output File (spec 023 Phase 16 T246 — FR-079)

Every skill MUST write its final deliverable to the user's workspace as a markdown file using the canonical naming convention:

```
{ticker}/{YYYY-MM-DD_HHMM}_{skill_name}_{affix}.md
```

Where:
- `{ticker}` — uppercase issuer ticker (creates a per-issuer subdirectory).
- `{YYYY-MM-DD_HHMM}` — ISO-style date + 24-hour time stamp (chronological sort).
- `{skill_name}` — the skill's `name` from YAML frontmatter (e.g., `business-model`, `recent-quarter`, `competitive`).
- `{affix}` — short descriptive slug capturing the analysis focus (e.g., `product-line-decomp`, `margin-drivers`, `peer-comparison`, `drug-pipeline`).

**Examples**:

- `LLY/2026-05-25_1430_business-model_product-line-decomp.md`
- `NVDA/2026-05-25_1545_recent-quarter_revenue-breakdown.md`
- `AAPL/2026-05-25_1700_competitive_peer-positioning.md`

**Workspace path semantics**: the path is RELATIVE to the agent's invocation cwd, NOT to any plugin install directory. Skills MUST NOT write under absolute system paths.

The skill's `## Output Structure` section MUST specify the affix template and the section ordering of the deliverable. Citation density: ≥1 citation per 200 words, format `{ticker} {citation_id} page<N>` (FR-078a).

### Multi-Ticker Output Convention (FR-093)

Skills producing output covering multiple tickers MUST use shared directories:

- **`_cross/{descriptive-slug}_{YYYY-MM-DD_HHMM}_{skill}_{affix}.md`** — for peer-comparison and cross-company analyses (e.g., `_cross/LLY-vs-peers_2026-06-03_comps_peer-comparison.md`).
- **`_sector/{sector_name}/{YYYY-MM-DD_HHMM}_{skill}_{affix}.md`** — for pure sector/thematic analyses with no primary ticker (e.g., `_sector/pharma/2026-06-03_sector-overview.md`). Sector names are lowercase-hyphenated.

YAML frontmatter uses `tickers: [LLY, NVO, PFE]` (plural array) for multi-ticker files vs `ticker: LLY` (singular) for single-ticker. Exactly one of `ticker` or `tickers` MUST be present — never both. Skills producing multi-ticker output: `comps-analysis`, `competitive-landscape`, `sector-overview`, and any skill invoked with `--peers=<T1>,<T2>`.

## agentii.md Append Protocol (spec 023 Phase 20 T293 — FR-087)

As the FINAL mandatory action after writing the output file, every skill MUST append a structured YAML frontmatter block to `agentii.md` at the workspace root:

```yaml
---
ticker: LLY
date: 2026-06-03
skill: recent-quarter
output_file: LLY/2026-06-03_1430_recent-quarter_consolidated-p-and-l.md
key_conclusions: Q1 2026 revenue $18.5B (+12% QoQ), EPS $2.34 beat consensus by 4%.
---
```

- If `agentii.md` does not exist, create it with a `# Project Memory Index` heading.
- Entries are APPEND-ONLY — never modify or delete existing entries.
- Multi-ticker outputs use `tickers: [LLY, NVO]` instead of `ticker: LLY`.
- The agent auto-reads `agentii.md` on session start for memory discovery (FR-087).

## Two-Tier Output Model (spec 023 Phase 20 T296 — FR-091)

Skills MUST follow a two-tier output model:

**Tier 1 — Raw Analysis**: Per-skill output files in `{ticker}/` (or `_cross/`, `_sector/`) per FR-079. Detailed, citation-dense, full methodology. These are the evidence.

**Tier 2 — Curated Snapshots**: After completing 2+ skills on the same ticker in a single session, the agent MUST synthesize a snapshot at `snapshots/{ticker}/{YYYY-MM-DD}_thesis.md`. The snapshot:
- Distills conclusions across all skills run in the session.
- Flags changes from the prior snapshot (if one exists) with a "## Changes from Prior Snapshot" section.
- References the prior snapshot's path for audit trail continuity.
- Updates `agentii.md` with the new `snapshot_ref` field.

Snapshots are cumulative — each references the prior one, forming an audit trail of evolving investment beliefs.

## FACT/DEDUCTED/VIEW Classification Taxonomy (spec 023 Phase 20 T297 — FR-092)

Every claim in a Tier 2 snapshot MUST be classified into exactly one of three categories:

| Badge | Meaning | Example |
|-------|---------|---------|
| `**[FACT]**` | Verifiable from SEC filings | "Q1 2026 revenue was $18.5B (10-Q, page12)" |
| `**[DEDUCTED]**` | Direct logical/mathematical deduction from facts | "QoQ revenue growth = +12% ($16.5B → $18.5B)" |
| `**[VIEW]**` | Subjective assessment, opinion, synthesis | "GLP-1 pipeline undervalued relative to $100B TAM" |

The inline badge format is `**[FACT]**`, `**[DEDUCTED]**`, `**[VIEW]**` placed at the beginning of each claim. Every snapshot MUST include a summary table:

```markdown
| Category | Count | % |
|----------|-------|---|
| [FACT] | 12 | 52% |
| [DEDUCTED] | 8 | 35% |
| [VIEW] | 3 | 13% |
| **Total** | **23** | 100% |
```

## Workspace style.md Override Check (spec 023 Phase 20 T307 — FR-094)

During FR-075 pre-flight, the agent MUST check for `./style.md` in the workspace root. If found, parse override fields and apply them:

| Override | Effect |
|----------|--------|
| `default_lookback_quarters: 12` | Override skill's temporal scope default |
| `reporting_currency: EUR` | Prefer EUR over USD for non-US companies |
| `sector_focus: pharma` | Limit analysis to specified sectors |
| `output_verbosity: comprehensive` | concise / standard / comprehensive |
| `peer_universe: [NVO, PFE, MRK]` | Default peer list for comps analysis |

Precedence: workspace `style.md` > package `style.md` > skill defaults.

## Scenario Analysis Cross-Cutting Mode (spec 023 Phase 21 T324 — FR-104)

Scenario Analysis is a cross-cutting mode (`--mode=scenario`) available to ALL valuation skills. NOT a standalone skill — it wraps existing valuation outputs.

**Framework**: (1) identify 2-4 key value drivers from prior analyses (YAML frontmatter per FR-090) and MD&A narrative. (2) Construct Bear/Base/Bull scenarios with probabilities summing to 100%. (3) Run underlying valuation for each scenario. (4) Compute probability-weighted expected value: Σ(Scenario_Value × Probability). (5) Rank key drivers by value impact. (6) Assign conviction: High (narrow spread), Medium, Low (wide spread).

**Skill entry**: every valuation skill's `## Protocol` section MUST include: `**Scenario mode (--mode=scenario)**: constructs Bear/Base/Bull probability-weighted valuation. See contracts/skill-methodology-template.md for the framework.`

## Citation Link Format (spec 023 Phase 19 T287 — FR-081)

When citing specific pages from SEC filings, skills MUST generate clickable citation links. The preferred format is the path-based short URL:

```
[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
```

**Example**: `[📄 LLY 8-K p.19](https://agentii.ai/v/LLY/sec129/19)`

**URL format specification**:
- `{ticker}` (required) — uppercase issuer ticker, position 1 in path, e.g., `LLY`
- `{citation_id}` (required) — filing citation ID, position 2 in path, e.g., `sec129`
- `{N}` (optional) — bare page number, position 3 in path, e.g., `19`; auto-normalized to `page19` by the server. When omitted (e.g., `/v/LLY/sec129`), the viewer scrolls to the document top.

**Legacy query-param format** (backward compatible, still accepted):
```
[📄 {ticker} {form_type} p.{N}](https://agentii.ai/v/{ticker}/{citation_id}/{N})
```
Short query param aliases (`t=`, `c=`, `p=`) are also accepted: `agentii.ai/view?t=LLY&c=sec129&p=19`

**Token efficiency**: The path-based format uses ~7 tokens vs ~18 for the legacy query-param format (~61% savings). For a 50-citation report, this saves ~550 tokens.

**Portal behavior**: The `agentii.ai/v/{ticker}/{citation_id}/{N}` route (spec 019 Phase D) issues a redirect to `api.agentii.ai/v1/view_document/{ticker}/{citation_id}?page_no=page{N}`, which resolves the document via `pipeline.src_documents JOIN pipeline.sec_filings`, fetches the `combined.htm` from R2 cloud storage (bronze disk fallback), finds the `<!-- PAGE_MARKER:{citation_id}_{page_no}_START -->` marker, injects a sidebar with page navigation, and scrolls the browser to that page position. The view_document endpoint is public (no auth required).

**Link rendering**: In iTerm2 and macOS Terminal, URLs are highlighted and Cmd+Click opens them in the default browser. All citation links in output files (FR-079) and evidence-pack entries (FR-046b) MUST use this format. The citation density requirement (≥1 citation per 200 words) applies to these links — each distinct page reference counts as one citation.

## CI Validation

`scripts/check.py` Check 22 validates that every committed `SKILL.md` contains all 5 required subsections under `## Methodology` in order. Violations fail the build.

Additional production-grounded checks (Phase 17):
- Check 28 (FR-014c): no `skills/*/SKILL.md` outside `skills/agentii/` namespace.
- Check 29 (FR-079, optional): every skill `## Output Structure` section MUST mention the `{ticker}/{YYYY-MM-DD_HHMM}_{skill_name}_{affix}.md` template path.
- Check 30 (FR-078a, optional): no bare-integer `page_no` references in `## Methodology` examples — only `{ticker} {citation_id} page<N>` format.
