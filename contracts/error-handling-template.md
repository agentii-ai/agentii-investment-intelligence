<!-- error-handling-template.md — inserted by quality-scan.py --fix when a skill lacks ## Error Handling (spec 039 FR-016). -->
## Error Handling

- **No data / empty result**: state "no data found for {ticker} in the requested window" and stop; never fabricate values.
- **Coverage gap**: if a required source is unavailable, annotate `coverage_gap` and proceed with partial analysis, naming what is missing.
- **Rate limit / source error**: report the degraded source and the fallback used; surface the AGENT_CONTRACT `error` reason.
- **Ambiguous ticker**: ask for disambiguation rather than guessing.
