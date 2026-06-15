---
description: Business model classification and structural analysis — product/service/platform, distribution channels, revenue composition, market sizing
argument-hint: <TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `business-model` skill bundled under `equity-research-core`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{YYYY-MM-DD_HHMM}_business-model_{affix}.md` — write to the bare-ticker directory `{ticker}/` (e.g. `NVDA/`), NEVER `{ticker}-recent-quarter/` or any dimension-suffixed variant.

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
