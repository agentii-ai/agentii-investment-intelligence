---
description: Business model classification and structural analysis (product/service/platform, distribution channels, revenue composition, market sizing, management)
argument-hint: <TICKER> [--mode=<slug>] [--modes=<slug1>,<slug2>] [--mode=all]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `business-model` skill bundled under `equity-research-core`.
3. Return the structured deliverable produced by the skill. Output written to `{ticker}/{YYYY-MM-DD_HHMM}_business-model_{affix}.md` per FR-079.

*Full methodology (5 modes, output structure, error handling) authored in the skill body.*

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` invocation rules.
