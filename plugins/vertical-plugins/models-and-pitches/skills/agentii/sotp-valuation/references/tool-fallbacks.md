# sotp-valuation — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action |
|------|-------------|-----------------|
| `get_statement_structure` | Tree unavailable | Use `search_documents` for "segment" keyword in 10-K MD&A |
| `read_source_pages` | SQL error | Use `search_documents` for segment narrative; flag as partial |
