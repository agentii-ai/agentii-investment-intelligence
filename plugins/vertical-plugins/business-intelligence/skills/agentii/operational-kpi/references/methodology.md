# operational-kpi — Methodology

## Retrieval Strategy

Structured-only retrieval via XBRL facts and financial metrics. Primary data sources:
`search_xbrl_facts` for headcount, revenue-per-employee, and operational metrics;
`get_company_financials` for consolidated financial context.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | No operational metrics in XBRL | Extract from MD&A via search_documents | `operational_from_filings: true` |
| `get_company_financials` | Partial data | Flag missing periods | `partial_data: true` |

## KPI Framework

- **Headcount trends**: YoY employee growth, revenue per employee
- **Utilization rates**: where disclosed (professional services, manufacturing)
- **Backlog / book-to-bill**: order backlog trends, book-to-bill ratio
- **Operational efficiency**: COGS/revenue, SG&A/revenue, capacity utilization
- **Productivity metrics**: same-store sales, units per employee
