---
name: tasks
description: "Decompose the plan into research tasks — one task per ticker × skill × mode, grouped by pillar, [P]-marked by the different-files-and-no-incomplete-deps rule, with source-refs. mode: all expands to N tasks at generation, never exists as one task (Q79)."
role: kit
market_data_stage: none
---

# agentii.tasks

## Task identity (Q79)

**One task = `ticker × skill × 单个 mode`.** `--mode=all` is a generation-time
expansion — it never exists as a single task (matching `validate-mode-syntax.py`'s
`all` reserved rule). Pre-M1: mode is `default` for the 53/62 skills without
`references/modes.md`; Depth-Tier Light falls back to the tier's explicit skill
list until `essentials_modes` exists.

## Format (plan contract)

`- [ ] T### [P] [pillar] TICKER × SKILL × MODE — purpose (src: pillar-id)`

- `[P]` = different files **and** no incomplete deps; `_cross/` synthesis tasks are
  never `[P]`.
- Every task carries a `src:` ref — traceability survives into converge (Q26).
- `tasks.md` is **strictly append-only** thereafter.

## Invocation

```bash
python3 scripts/agentii_cmd.py tasks --thesis theses/001-ai-semiconductors --spec theses/001-ai-semiconductors/spec.md
```

Gate 3 (after tasks, informational) shows task count × cost estimate.
