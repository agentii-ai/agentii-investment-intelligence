---
description: Secular technology trends analysis — technology adoption cycles, disruption risk, strategic positioning
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `secular-trends` skill bundled under `equity-research-core`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{{YYYY-MM-DD_HHMM}}_secular-trends_{{affix}}.md` .

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
