# peg-valuation — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `search_earnings_calendar` | No consensus LTG | Use historical EPS CAGR from XBRL | "Consensus growth unavailable; using 3yr historical EPS CAGR" |
| `get_realtime_quote` | Rate limit | Use latest quarter EPS from XBRL + manual price input prompt | "Real-time price unavailable; prompt user for current price" |
| Negative earnings | PE < 0 | Flag "PEG not meaningful"; suggest EV/Revenue or P/S | "Negative earnings — PEG not applicable" |
