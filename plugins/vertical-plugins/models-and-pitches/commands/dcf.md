---
description: DCF valuation model — 5-10 year projection, WACC construction, sensitivity tables
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `dcf` skill bundled under `models-and-pitches`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{{YYYY-MM-DD_HHMM}}_dcf_{{affix}}.md` .

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
