---
description: Turnaround vs stagnation analysis
argument-hint: <TICKER> --peers=<T1>,<T2> [--mode=<slug>]
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `dim-turnaround-stagnation` skill bundled under `equity-research-core`.
3. Return the structured deliverable produced by the skill.


> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
