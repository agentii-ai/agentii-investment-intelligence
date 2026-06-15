# residual-income — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action |
|------|-------------|-----------------|
| `get_realtime_quote` | Beta unavailable | Use industry average beta from Damodaran data |
| `search_earnings_calendar` | No consensus | Use historical EPS trend + manual ROE forecast |
