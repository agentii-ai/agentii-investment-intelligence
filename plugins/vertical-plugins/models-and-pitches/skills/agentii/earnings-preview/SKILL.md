---
name: earnings-preview
multi_ticker_semantics: single_target
description: Earnings preview deck, quarterly earnings presentation, earnings summary slides, consensus vs actual presentation, earnings preview report, pre-earnings analysis, earnings expectations deck, quarterly preview, upcoming earnings summary, earnings announcement preview
temporal_scope:
 default_quarters: 4
 max_quarters: 8
 description: "Typical lookback: 4 quarters, max: 8"
allowed_tools:
 - search_companies
 - search_xbrl_facts
 - search_earnings_calendar
 - get_company_financials
 - get_company_profile
 - list_xbrl_concepts
retrieval_scope: structured_only
min_tool_diversity: 5
---

## Preflight

Run the canonical pre-flight sequence — MCP health probe, ticker resolution, workspace `style.md` override, memory load, and coverage check. See `contracts/preflight.md`.

```bash
# Tier 1: agentii-office MCP (recommended)
OFFICE_BACKEND="mcp"
curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/office/mcp/health 2>/dev/null || echo "UNREACHABLE"

# Tier 2: Python+LibreOffice local fallback
if [ "$OFFICE_BACKEND" = "unreachable" ]; then
 python3 -c "import openpyxl; import pptx" 2>/dev/null && OFFICE_BACKEND="python" || echo "DEPS_MISSING"
fi

# Tier 3: OfficeCLI single-binary fallback
if [ "$OFFICE_BACKEND" = "unreachable" ]; then
 officecli --version 2>/dev/null && OFFICE_BACKEND="officecli" || echo "OFFICECLI_MISSING"
fi

if [ "$OFFICE_BACKEND" = "unreachable" ]; then
 echo "AGENTII_OFFICE_UNREACHABLE: No office backend available."
 echo "Options: (a) set AGENTII_API_KEY, (b) pip install openpyxl python-pptx, (c) install OfficeCLI"
fi
```

Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md`.
## Triggers

- generate earnings preview deck
- build earnings preview presentation
- create quarterly earnings slides
- earnings preview pptx
- earnings summary presentation
- consensus estimates presentation
- earnings surprise summary deck
- quarterly results presentation
- earnings catalyst calendar slides
- pre-earnings analyst deck

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| slide_count | 4-6 | Title, Company Overview, Consensus Estimates, Historical Surprises, Catalysts, Outlook |
| lookback_quarters | 4 | Trailing 4 quarters for trend analysis |
| peer_count | 3-5 | From search_companies sector peers |
| source_footers | required | Every slide has standard agentii citation footer |
| template | institutional-default | Dark header bar, agentii blue accent, 12pt body |

## Methodology

### Retrieval Scope

This skill performs structured data retrieval (earnings calendar, XBRL facts, company profile) with simple lookups — no unstructured document search. `retrieval_scope: structured_only` applies. See references/formula-sheet.md for presentation structure guidelines.

### Retrieval Strategy

See `contracts/retrieval.md` for the canonical decision tree; skill-specific retrieval detail is in `references/methodology.md`.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Trailing 4 quarters captures current estimates and YoY comparisons. Maximum 8 quarters for analysts who want 2-year trend context on the estimates slide.

### Tool Allowlist

See frontmatter `allowed_tools`. This skill produces a polished `.md` slide-deck specification; `.pptx` rendering is available via the companion `financial-analysis:pptx-author` skill (separate install; see `contracts/office-tooling.md`).

### Protocol

Step-by-step execution detail is in `references/methodology.md`.

## Deliverable Chain

**Inputs** → **Build** → **Validate** → **Output** → **Next**

1. **Inputs**: resolved ticker + earnings calendar, consensus estimates, and trailing XBRL facts (`search_earnings_calendar`, `search_xbrl_facts`, `search_companies`, `get_company_profile`).
2. **Build**: write the polished 4–6 slide `.md` slide-deck specification per `## Output Structure`. `.pptx` rendering is available via the companion `financial-analysis:pptx-author` skill (see `contracts/office-tooling.md`).
3. **Validate**: run the `## Validation Gates` below.
4. **Output**: write the artifact path per `## Output File`.
5. **Next**: append to `agentii.md`; hand off to a downstream pitch/review skill if requested.

## Validation Gates

1. **slide count**: between 4 and 6. *If failed*: If outside range: refuse delivery.
2. **estimates slide**: includes consensus, high, and low estimates. *If failed*: If missing: flag in Coverage Gaps.
3. **source footers**: every slide has source_footer with standard agentii citation. *If failed*: If any missing: refuse delivery.
4. **peer comparison**: has >= 3 peers. *If failed*: If < 3: flag in Coverage Gaps.
## Tool Fallbacks

Per-tool failure modes and fallback actions are tabulated in `references/tool-fallbacks.md`.

## Output File

Write the final deliverable to `{ticker}/{YYYY-MM-DD_HHMM}_earnings-preview_{affix}.md` .

## Output Structure

The deliverable is a structured markdown report written to the path in `## Output File`. Full section-by-section template (headings, tables, and field definitions) lives in `references/output-structure.md`. Required elements:

1. **Executive Summary** — headline conclusions (≤200 words).
2. **Core analysis sections** — per this skill's methodology and analyst modes.
3. **Data classification** — tag findings `[FACT]` / `[DEDUCTED]` / `[VIEW]` per `contracts/snapshot-synthesis.md`.
4. **Coverage Gaps & Citations** — inline `/v/` citations are PRIMARY (immediately after each fact); the bottom **Citations** section is a non-duplicative roll-up index.
5. **Output frontmatter** — emit the FR-090 structured block per `contracts/output-frontmatter-schema.md`.

**Citations & memory**: follow `contracts/citation-and-memory.md` — ≥1 citation per 200 words; every material fact, table row, and metric is immediately followed by its inline clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link; a bottom **Citations** section provides a non-duplicative roll-up index; the closing TUI reply includes a compact **Key Citations** list (headline 5–10 facts) of clickable `/v/` URLs; and append the run to `agentii.md` per `contracts/agentii-md-schema.md`.

## Memory & Snapshot

- **Memory load** (pre-flight): load prior workspace context for the ticker before retrieval — see `contracts/memory-load.md`.
- **Structured output frontmatter**: emit the FR-090 block (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`) per `contracts/output-frontmatter-schema.md`.
- **Snapshot synthesis**: after writing the deliverable, update the two-tier snapshot and classify findings as `[FACT]`/`[DEDUCTED]`/`[VIEW]` — see `contracts/snapshot-synthesis.md`.
- **Session archival**: record the run under `sessions/{YYYY-MM-DD}/` and update `sessions/INDEX.md` per `contracts/session-format.md`.

## Final Summary (TUI)

End the closing chat reply with a compact **Key Citations** list (headline 5–10 facts), each a clickable `https://agentii.ai/v/{ticker}/{citation_id}/{N}` link, so the user can cmd+click straight to the exact SEC page. See `contracts/citation-and-memory.md`.

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing earnings data | `search_earnings_calendar` returns empty | Use `search_xbrl_facts` for historical actuals only; flag estimates as unavailable | "Consensus estimates not available for {ticker}; presentation based on historical actuals only." |
| Partial data | <80% expected fields returned | Proceed with coverage gaps section | "Presentation based on partial data; see Coverage Gaps." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | <4 quarters of data available | Downgrade to limited-history presentation (3 slides min) | "Limited historical data available; presentation adjusted." |
| MCP unreachable | agentii Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection and AGENTII_API_KEY." |
| Office backend unreachable | All 3 office backends fail Preflight | Halt with AGENTII_OFFICE_UNREACHABLE | "No office backend available. Options: (a) set AGENTII_API_KEY for agentii-office, (b) pip install python-pptx, (c) install OfficeCLI." |
| Knowledge Store unavailable | `get_entity_knowledge` returns 503 | Fall back to `get_company_profile` + `search_companies`; flag with `knowledge_store_degraded: true` | "Knowledge Store not yet available; peer analysis based on filing-derived entity context." |
