# peer-bench — Methodology

## Retrieval Strategy

Multi-ticker structured comparison. Resolve all peer tickers via `search_companies` (exact →
fuzzy alias → share-class). Retrieve financial metrics for each ticker via `search_xbrl_facts`
and `get_company_financials`. Compare across standardized metrics.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | Peer ticker returns empty | Skip ticker; note in Coverage Gaps | `peer_skipped: <ticker>` |
| `get_company_financials` | Partial data | Flag missing periods | `partial_peer_data: true` |
| `search_companies` | Peer not in coverage | Exclude from comparison | `peer_not_covered: <ticker>` |

## Benchmarking Framework

Metrics compared across peers:
- **Growth**: revenue growth (1yr/3yr CAGR), EPS growth
- **Profitability**: gross margin, operating margin, net margin, ROE, ROA
- **Valuation**: P/E (TTM), EV/EBITDA, P/B, P/S
- **Financial health**: D/E, current ratio, interest coverage

Statistical summary: mean, median, Q1, Q3, high, low per metric. Z-score ranking for
composite performance.
