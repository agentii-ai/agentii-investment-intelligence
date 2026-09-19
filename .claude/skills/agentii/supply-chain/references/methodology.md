# supply-chain — Methodology

## Retrieval Strategy

XBRL segment/geography data for customer and supplier concentration. SEC filings (10-K Item 1
Business, Item 1A Risk Factors) for supply-chain narrative. `search_documents` with
`secondary_label=supply_chain` where available.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | No segment/geography dimensions | Use Item 1 narrative only | `segment_data_unavailable: true` |
| `search_documents` | No supply-chain labeled docs | Keyword search in filings | `keyword_fallback: true` |
| `read_source_pages` | Page not found | Try adjacent pages | `page_fallback: true` |

## Supply Chain Analysis Framework

- **Supplier concentration**: % revenue from top suppliers, single-source dependencies
- **Customer concentration**: % revenue from top customers (10-K Item 1 disclosure)
- **Geographic exposure**: manufacturing/sourcing by region, tariff sensitivity
- **Bottleneck identification**: single points of failure, lead-time risks
