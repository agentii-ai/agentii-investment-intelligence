# unit-economics — Methodology

## Retrieval Strategy

Combines XBRL revenue/cost data with filing-derived customer metrics. Extracts implied
unit economics from segment disclosures, revenue recognition policies, and operating
metrics in 10-K Item 1 and Item 7.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | No unit-level data | Estimate from aggregate revenue/customer counts | `unit_estimates: true` |
| `search_documents` | No customer metrics disclosed | Flag as unavailable | `customer_metrics_unavailable: true` |

## Unit Economics Framework

- **CAC estimation**: sales & marketing spend / new customers (where disclosed)
- **LTV estimation**: average revenue per customer × gross margin × avg lifetime
- **LTV/CAC ratio**: benchmark ≥3 for healthy unit economics
- **Churn inference**: revenue retention rates, cohort disclosures
- **Gross margin per unit**: segment-level gross profit / unit volume
