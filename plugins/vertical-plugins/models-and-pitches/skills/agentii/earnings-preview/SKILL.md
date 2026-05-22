---
name: earnings-preview
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
retrieval_scope: structured_only
min_tool_diversity: 5
---

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

Follow the retrieval strategy decision tree in `retrieval.md`. This skill uses:
- Branch (a) for structured financial metrics via `search_xbrl_facts` with `list_xbrl_concepts` pre-condition for unfamiliar concepts.
- Branch (d) for simple lookups via `search_earnings_calendar` / `get_company_profile` / `search_companies`.

### Temporal Scope

Default: 4 fiscal quarters (max 8). Trailing 4 quarters captures current estimates and YoY comparisons. Maximum 8 quarters for analysts who want 2-year trend context on the estimates slide.

### Tool Allowlist

See frontmatter `allowed_tools` — 8 tools declared. All office tools (`pptx.build`, `pptx.edit`, `pptx.refresh`) resolve via the abstract tool layer (the office tools resolve via your available backend); concrete backend determined by Preflight probe.

### Protocol

1. **Earnings calendar lookup**: call `search_earnings_calendar(ticker, fiscal_year=current)` to get the most recent reported quarter, next earnings date, and consensus estimates.
2. **Financial highlights**: call `search_xbrl_facts(ticker, concept=["Revenues","NetIncomeLoss","OperatingIncomeLoss","DilutedEPS"], fiscal_period=["Q1","Q2","Q3","Q4","FY"], fiscal_year=[current, current-1])` for trailing data.
3. **Company context**: call `get_company_profile(ticker)` for company name, sector, industry.
4. **Peer discovery**: call `search_companies(sector=<sector>, limit=5)` for peer comparison slide.
5. **PPT construction**: construct `pptx_spec` per `contracts/pptx_spec.schema.json` with 4–6 slides.
6. **Build**: call `pptx.build(pptx_spec)` to render the .pptx.
7. **Review**: call `pptx.edit` for content review if needed.
8. **Output**: presigned URL to the .pptx file.

## Deliverable Chain

```
[search_earnings_calendar + search_xbrl_facts + search_companies + get_company_profile] → pptx_build → pptx.edit(review) → [.pptx output]
```
## Validation Gates

1. **slide count**: between 4 and 6. *If failed*: If outside range: refuse delivery.
2. **estimates slide**: includes consensus, high, and low estimates. *If failed*: If missing: flag in Coverage Gaps.
3. **source footers**: every slide has source_footer with standard agentii citation. *If failed*: If any missing: refuse delivery.
4. **peer comparison**: has >= 3 peers. *If failed*: If < 3: flag in Coverage Gaps.
## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `read_source_pages` | SQL error / PROXY_ERROR | Use `search_keyword_in_source(document_id, keyword)` if document_id known; otherwise `search_documents` with same query | "source file unavailable; used keyword search instead" |
| `read_source_outline` | PROXY_ERROR / 404 | Use `list_sources` for document-level metadata | "page map unavailable; used document listing instead" |
| `list_xbrl_concepts` | Timeout / 503 | Use direct `search_xbrl_facts` with standard US-GAAP concepts (Revenues, NetIncomeLoss, EarningsPerShareDiluted, OperatingIncomeLoss, Assets) | "concept discovery skipped due to timeout; using standard US-GAAP concepts" |
| `get_company_fiscal_calendar` | Cross-validation failed | Use XBRL-derived period grid from `search_xbrl_facts` `period_end` dates | "fiscal calendar mismatch; using XBRL-derived period grid" |
| `search_unified` | Intermittent error | Use parallel `search_documents` + `search_xbrl_facts` with the same query | "unified search unavailable; used parallel document + XBRL search" |
| `batch_search` | PROXY_ERROR | Use sequential individual calls (one per sub-query) | "batch search unavailable; used sequential calls" |

Tool errors are retried ONCE with the fallback action before escalating to the retrieval gaps failure policy. If both Layer 2 and Layer 3 tools are unavailable, enter document access degradation mode (structured data + metadata only, flag output as degraded).

11. **tool diversity**: distinct MCP tools used in this invocation >= `min_tool_diversity` (5). *If failed*: flag as depth-insufficient in Coverage Gaps, listing which tool categories were unused (structured data / document retrieval / company metadata / earnings calendar / coverage). This gate does NOT block analysis completion — it is a quality signal for your review.

## Output Structure

1. **Slide 1 — Title**: Company name, ticker, "Earnings Preview — Q<N> FY<YYYY>", report date
2. **Slide 2 — Company Overview**: Business description, sector, market cap, key products/segments (from `get_company_profile`)
3. **Slide 3 — Consensus Estimates**: Table with consensus/high/low for Revenue, EPS, EBITDA; YoY comparison; estimate count (from `search_earnings_calendar`)
4. **Slide 4 — Historical Surprises**: Table of last 4 quarters: estimate vs actual, surprise %, direction (from `search_earnings_calendar` + `search_xbrl_facts`)
5. **Slide 5 — Peer Comparison**: Peer table with ticker, EV/EBITDA, P/E, Revenue growth (from `search_companies` + `search_xbrl_facts`)
6. **Slide 6 — Catalysts & Outlook**: Forward catalysts from earnings transcript, upcoming events, guidance summary (from `search_earnings_calendar`)

Slide 6 is optional (4–6 range). If peer data or catalyst data is unavailable, merge into fewer slides.

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
