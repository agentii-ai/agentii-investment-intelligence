# recent-quarter — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `search_xbrl_facts` | Empty result | Try prior fiscal year; if still empty, flag as data-unavailable | "XBRL facts unavailable for this ticker/period" |
| `search_earnings_calendar` | Empty result | Use `get_company_fiscal_calendar` to determine correct fiscal period format | "Earnings calendar unavailable; using fiscal calendar for period orientation" |
| `get_company_financials` | 404 / error | Use individual `search_xbrl_facts` calls for each concept | "Financials overview unavailable; using granular XBRL facts" |
