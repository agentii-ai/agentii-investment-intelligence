# Data-Tool Preflight — env-var checks for data-consuming skills

**Spec**: spec 039 US5 (T062, FR — zero-key-first) | **Applies to**: skills that consume `~~macro_data` / `~~market_data` / `~~earnings_data`

Data-consuming skills SHOULD include a `## Preflight` note pointing users at the
opt-in credential wizard. Keys are NEVER required (zero-key paths exist); they only
raise rate limits.

## Recommended `## Preflight` snippet

```
## Preflight
This skill works with no API keys (zero-key sources). For higher rate limits, optionally set:
- `FRED_API_KEY`   — macro series (~~macro_data)
- `FMP_API_KEY`    — earnings estimates (~~earnings_data)
- `FINNHUB_API_KEY`— market/calendar (~~market_data)
Run `python3 data-tools/setup_credentials.py` (wizard) or `--check` (report only).
```

## Which skills need which vars

| Placeholder consumed | Optional vars | Zero-key source |
|----------------------|---------------|-----------------|
| `~~macro_data` | `FRED_API_KEY` | yfinance macro proxy |
| `~~market_data` | `FINNHUB_API_KEY` | yfinance (none) |
| `~~earnings_data` | `FMP_API_KEY` | defeatbeta-api (none) |

CI note: `setup_credentials.py --check` is non-interactive and secret-safe (never echoes values).
