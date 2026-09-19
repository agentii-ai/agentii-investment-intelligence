# revenue-decomp — Methodology

## Retrieval Strategy

Primary: `search_xbrl_facts` with `view=detailed` for segment/product/geography revenue
breakdowns. Secondary: `search_documents` for MD&A revenue narrative (Item 7, 10-K).
Uses `search_cross_period` for multi-quarter revenue progression.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` (detailed) | No segment dimensions | Use standard view + filing narrative | `segment_data_unavailable: true` |
| `search_cross_period` | Server error | Sequential single-period retrieval | `cross_period_fallback: true` |
| `read_source_pages` | Page not found | Try adjacent pages | `page_fallback: true` |

## Decomposition Framework

- **Segment breakdown**: revenue by reportable segment (IFRS 8 / ASC 280)
- **Geographic split**: domestic vs international, regional breakdowns
- **Product-line waterfall**: product category revenue progression
- **Channel analysis**: direct vs indirect, digital vs physical where disclosed
