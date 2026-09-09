---
name: implement
description: Execute research tasks — checklist soft gate, phase dispatch with explicit thesis_dir, budget enforcement (halt + approval card on overrun), skill_pin recording (version_hash content-hashed per skill directory), [x] written on completion.
role: kit
market_data_stage: none
---

# agentii.implement

## Before dispatch

1. **Checklist soft gate (Q29)**: scan `checklists/*.md`; on unchecked items, stop
   and ask — the human may proceed (it is a soft gate, not a hard block).
2. **Budget check (Q58)**: `budget{max_tasks, max_retries_per_task}` — exceeding
   halts with a Q39 approval card; never a silent overrun. The dispatcher checks
   budget first, `max_in_flight` second (Q82).
3. **Resume matrix (Q56)**: absent → run; valid FR-090 → skip; corrupted →
   `--resume`; `stale` → leave for converge. The filesystem IS the checkpoint.
4. **`thesis_dir` passed explicitly** (Q37) — no singleton pointer; cwd fallback is
   human-only and journaled.

## During dispatch

- Cross-vertical handoff passes artifact **paths, never content** (Q13 rule 3).
- `skill_pin: {skill_name: version_hash}` recorded before the first task
  (`version_hash` = content hash of SKILL.md + `references/`); a version change
  mid-thesis uses the new version and **appends** the new hash (Q57).
- `[x]` written on completion — display-only; converge never reads it.

## Invocation

```bash
python3 scripts/dispatch.py --thesis-dir theses/001-ai-semiconductors --task "NVDA recent-quarter default" --journal theses/001-ai-semiconductors/shards/run1.ndjson
```

Gate 4 (before mass dispatch, consequential — never delegable) shows budget and
parallelism; it must attach a budget estimate.
