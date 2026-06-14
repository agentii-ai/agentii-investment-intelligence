---
description: Financial ratio analysis — 24 ratios across 6 categories with cross-company comparison
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `ratio-analysis` skill bundled under `quantitative-analysis`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{{YYYY-MM-DD_HHMM}}_ratio-analysis_{{affix}}.md` .

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
