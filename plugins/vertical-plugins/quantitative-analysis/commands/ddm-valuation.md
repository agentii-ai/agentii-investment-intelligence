---
description: Dividend Discount Model — multi-stage DDM for mature dividend payers and financials
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `ddm-valuation` skill bundled under `quantitative-analysis`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{YYYY-MM-DD_HHMM}_ddm-valuation_{affix}.md` .

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
