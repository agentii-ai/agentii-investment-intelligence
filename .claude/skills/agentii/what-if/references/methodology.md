# what-if — Methodology

## Retrieval Strategy

Structured retrieval for baseline financial data, then scenario modeling. Primary:
`search_xbrl_facts` for historical baseline. `get_company_financials` for consolidated
context. `search_documents` for risk factors and management guidance.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | Partial history | Use available periods | `partial_history: true` |
| `search_documents` | No guidance found | Flag in assumptions | `guidance_unavailable: true` |

## Scenario Framework

Three scenarios built from historical baseline:
- **Bear case**: demand shock, margin compression, multiple contraction
- **Base case**: consensus-aligned growth, stable margins
- **Bull case**: above-consensus growth, operating leverage, multiple expansion

Key drivers sensitized: revenue growth, gross margin, operating margin, tax rate,
WACC, terminal multiple. Probability-weighted EV reported.
