# recent-quarter — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `search_xbrl_facts` | Empty result | Re-check the resolved `period_id`; do not widen the date range; return the typed absence | "XBRL facts unavailable for this ticker/period" |
| `search_earnings_calendar` | Empty result | Use the resolved period and `date_basis`/`fiscal_source`; never derive a quarter from a calendar month | "Earnings calendar unavailable for the resolved period" |
| `get_company_financials` | 404 / error | Use individual `search_xbrl_facts` calls for each concept | "Financials overview unavailable; using granular XBRL facts" |
