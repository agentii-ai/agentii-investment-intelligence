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

## CI Validation

`scripts/check.py` Check 22 validates that every committed `SKILL.md` contains all 5 required subsections under `## Methodology` in order. Violations fail the build.
