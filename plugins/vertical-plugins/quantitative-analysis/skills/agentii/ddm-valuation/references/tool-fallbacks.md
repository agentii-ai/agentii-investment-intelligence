# ddm-valuation — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action |
|------|-------------|-----------------|
| `get_realtime_quote` | Beta unavailable | Use industry average beta or prompt user for manual input |
| `search_earnings_calendar` | No consensus EPS | Use historical EPS trend for payout projection |
