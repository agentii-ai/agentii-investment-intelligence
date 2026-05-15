---
name: pitch-deck
description: 'Pitch deck builder: 12-16 slide investment-thesis presentation with
  sourced-footers, financial highlights, comps, risks, and catalysts.'
multi_ticker_semantics: single_target
parameter_free: false
temporal_scope:
  default_quarters: 12
  max_quarters: 20
  description: 'Financial modeling: trailing 12 quarters (3 fiscal years) for long-range
    projection inputs'
allowed_tools:
- search_xbrl_facts
- list_xbrl_concepts
- get_company_financials
- get_company_profile
- search_earnings_calendar
- search_documents
- read_source_outline
- read_source_pages
- pptx.build
- pptx.edit
- pptx.refresh
---

<!-- composite_origin: pptx-author + ppt-template-creator + deck-refresh + ib-check-deck -->

## Preflight

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

## Triggers

- build pitch deck
- generate investment thesis presentation
- create pitch deck for
- investment banking presentation
- sell-side deck for
- institutional investor presentation
- management presentation with financials
- board deck with financial highlights
- investor day presentation
- roadshow presentation

## Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| slide_count | 12-16 | Title, exec-summary, thesis, financials, comps, risks, catalysts, appendix |
| source_footers | required | Every slide has standard agentii citation footer |
| template | institutional-default | Dark header bar, agentii blue accent, 12pt body |

## Methodology

### Retrieval Scope

This skill performs unstructured document search at scale across SEC filings (10-K, 10-Q, 8-K). The three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read) applies to all unstructured document search at scale.

### Retrieval Strategy

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (b) for multi-period unstructured queries via `search_cross_period`.
- Branch (c) for single-period document queries via direct `read_source_outline` → `read_source_pages`.
- Branch (d) for simple lookups via `get_company_profile` / `search_earnings_calendar`.

### Temporal Scope

Default: 12 fiscal quarters (max 20). Financial modeling: trailing 12 quarters (3 fiscal years) for long-range projection inputs.

### Tool Allowlist

See frontmatter `allowed_tools` — 11 tools declared. PPT tools (`pptx.build`, `pptx.edit`, `pptx.refresh`) resolve via the abstract tool layer (the office tools resolve via your available backend).

### Protocol

1. Pre-retrieval: call `get_company_fiscal_calendar/{ticker}` to resolve fiscal period format.
2. Concept discovery: call `list_xbrl_concepts(query=<term>, ticker=<T>)` for unfamiliar XBRL concepts.
3. Retrieval: follow the three-layer protocol.
4. PPT construction: construct `pptx_spec` per `contracts/pptx_spec.schema.json` with 12–16 slides.
5. Build: call `pptx.build(pptx_spec)` to render the .pptx.
6. Review: call `pptx.edit` for content review.
7. Evidence-pack handoff: produce `evidence-pack.json` + `evidence-digest.md` per the evidence-pack output contract.

## Deliverable Chain

```
[get_company_profile + search_xbrl_facts + search_earnings_calendar] → pptx_build → pptx.edit(review) → [.pptx output]
```

## Validation Gates

1. **slide count**: between 12 and 16. *If failed*: If outside range: refuse delivery, report expected vs actual count.
2. **executive summary**: present and is slide #2. *If failed*: If missing or wrong position: refuse delivery.
3. **source footers**: every slide has source_footer with standard agentii citation. *If failed*: If any slide missing footer: list slide numbers lacking footers, refuse delivery.
4. **body text density**: no slide has > 50 words of body text. *If failed*: If any slide exceeds: flag slides, suggest splitting content.

## Output Structure

1. **Slide 1 — Title**: Company name, ticker, "Investment Thesis Presentation", date
2. **Slide 2 — Executive Summary**: 3-5 bullet thesis points, key financial metrics callout
3. **Slides 3–5 — Financial Highlights**: Revenue trend, margin waterfall, ROIC tree
4. **Slides 6–8 — Valuation**: DCF output summary, comps table, implied valuation range
5. **Slides 9–10 — Competitive Position**: Market share, moat assessment, peer comparison
6. **Slide 11 — Risks**: Risk matrix (probability × impact), mitigants
7. **Slides 12–13 — Catalysts**: Timeline of upcoming events, expected impact
8. **Slides 14–16 — Appendix**: Detailed financials, methodology notes, disclaimer

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {ticker} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {n} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data available; analysis adjusted." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
| Office backend unreachable | All 3 office backends fail Preflight | Halt with AGENTII_OFFICE_UNREACHABLE | "No office backend available." |
| Knowledge Store unavailable | `get_entity_knowledge` returns 503 | Fall back to `get_company_profile` + `search_companies`; flag with `knowledge_store_degraded: true` | "Knowledge Store not yet available; analysis based on filing-derived entity context." |
