---
description: LBO model — sources & uses, debt schedule, exit-multiple analysis, sponsor IRR sensitivity
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `lbo` skill bundled under `models-and-pitches`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{YYYY-MM-DD_HHMM}_lbo_{affix}.md` .

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
