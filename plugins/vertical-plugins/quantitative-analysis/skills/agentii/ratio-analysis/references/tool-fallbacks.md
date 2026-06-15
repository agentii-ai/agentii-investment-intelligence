# ratio-analysis — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `get_realtime_quote` | Rate limit / unavailable | Use `search_earnings_calendar` for EPS estimates; flag valuation ratios as "price data unavailable" | "Real-time price unavailable; valuation ratios omitted" |
| `search_xbrl_facts` | Concept not found | Try alternative concept names via `list_xbrl_concepts` | "XBRL concept unavailable; used alternative" |
| `search_companies` | Sector undefined | Use SIC code from `get_company_profile` | "Peer identification via SIC code" |
