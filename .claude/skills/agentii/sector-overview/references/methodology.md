# sector-overview — Methodology

## Retrieval Strategy

Sector-level analysis combining XBRL aggregate data, SEC filing industry narratives, and
peer-group financials. Primary: `search_xbrl_facts` for sector aggregate metrics. Secondary:
`search_documents` for industry-level MD&A commentary and risk factors.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | No sector-level aggregates | Build from individual peer data | `aggregate_from_peers: true` |
| `search_documents` | No industry narrative found | Proceed with quantitative-only | `narrative_unavailable: true` |
| `read_source_pages` | Page not found | Try adjacent pages | `page_fallback: true` |

## Sector Analysis Framework

- **TAM estimation**: top-down (industry reports via filings) + bottom-up (peer revenue aggregation)
- **Competitive concentration**: HHI from peer revenue shares
- **Regulatory landscape**: extracted from 10-K Item 1 / Risk Factors
- **Growth drivers**: secular trends from MD&A and earnings calls
