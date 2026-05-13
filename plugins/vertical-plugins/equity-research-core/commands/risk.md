---
description: Risk analysis
argument-hint: <TICKER> [--mode=<slug>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `dim-risk-analysis` skill bundled under `equity-research-core`.
3. Return the structured deliverable produced by the skill.

*Full workflow authored alongside the skill methodology (Phase 3/4/5).*

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
