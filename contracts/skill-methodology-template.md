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

## Citation Link Format (spec 023 Phase 19 T287 — FR-081)

When citing specific pages from SEC filings, skills MUST generate clickable citation links in the format:

```
[📄 {ticker} {form_type} p.{page_no}](https://www.agentii.ai/view?ticker={ticker}&citation_id={citation_id}&page_no={page_no})
```

**Example**: `[📄 LLY 8-K p.19](https://www.agentii.ai/view?ticker=LLY&citation_id=sec129&page_no=page19)`

**URL format specification**:
- `ticker` (required) — uppercase issuer ticker, e.g., `LLY`
- `citation_id` (required) — filing citation ID, e.g., `sec129`
- `page_no` (optional) — page number in `page<N>` format, e.g., `page19`; when omitted, the portal `/view` page scrolls to the document top

**Portal behavior**: The `www.agentii.ai/view` page (spec 019 Phase D1) resolves the document via `pipeline.src_documents JOIN pipeline.sec_filings`, fetches the `combined.htm` from R2 cloud storage (bronze disk fallback), finds the `<!-- PAGE_MARKER:{citation_id}_{page_no}_START -->` marker, and scrolls the browser to that page position. Unauthenticated users are redirected to `/signin`.

**Link rendering**: In iTerm2 and macOS Terminal, URLs are highlighted and Cmd+Click opens them in the default browser. All citation links in output files (FR-079) and evidence-pack entries (FR-046b) MUST use this format. The citation density requirement (≥1 citation per 200 words) applies to these links — each distinct page reference counts as one citation.

## CI Validation

`scripts/check.py` Check 22 validates that every committed `SKILL.md` contains all 5 required subsections under `## Methodology` in order. Violations fail the build.

Additional production-grounded checks (Phase 17):
- Check 28 (FR-014c): no `skills/*/SKILL.md` outside `skills/agentii/` namespace.
- Check 29 (FR-079, optional): every skill `## Output Structure` section MUST mention the `{ticker}/{YYYY-MM-DD_HHMM}_{skill_name}_{affix}.md` template path.
- Check 30 (FR-078a, optional): no bare-integer `page_no` references in `## Methodology` examples — only `{ticker} {citation_id} page<N>` format.
