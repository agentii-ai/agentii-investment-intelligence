# competitive-positioning — Methodology

## Retrieval Strategy

Follows the retrieval strategy decision tree in `contracts/retrieval.md`. Primary branch:
**(b)/(c) Unstructured Query via the three-layer protocol**. Resolve the canonical ticker
first (exact → fuzzy alias → share-class) before any data call.

## Tool Fallbacks

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|----------------|---------------------|
| `search_xbrl_facts` | Empty result set | Try alternate concept names via `list_xbrl_concepts` | `xbxl_fallback_used: true` |
| `read_source_outline` | Returned 0 pages | Try `search_documents` keyword search | `document_access_degraded: true` |
| `read_source_deep_outline` | Timeout or empty | Fall back to lightweight outline + flag | `deep_outline_degraded: true` |
| `read_source_pages` | Page not found | Try adjacent pages ±2 | `page_fallback: true` |
| `search_cross_period` | Server error | Sequential single-period retrieval | `cross_period_fallback: true` |

## Porter's Five Forces Framework

This skill applies Porter's framework to the target company and its peers:
1. Rivalry among existing competitors
2. Threat of new entrants
3. Bargaining power of suppliers
4. Bargaining power of buyers
5. Threat of substitute products

Each force is assessed with XBRL-derived financial metrics and SEC filing narrative evidence.
