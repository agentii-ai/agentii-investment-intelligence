---
description: Reverse DCF — solve for implied growth rate/margins from current price
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `reverse-dcf` skill bundled under `quantitative-analysis`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{{YYYY-MM-DD_HHMM}}_reverse-dcf_{{affix}}.md` .

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
