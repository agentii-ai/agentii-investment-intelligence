---
name: constitution
description: Scaffold and amend the L1 Investment Constitution — [ALL_CAPS] placeholder bootstrap, SemVer bump rules, Sync Impact Report, MINOR/MAJOR re-examination dispatch after the gate-5 budget confirm. Thesis creation stays refused until ratification (Q83).
role: kit
market_data_stage: none
---

# agentii.constitution

## Bootstrap (empty workspace, Q83)

Scaffolds `constitution.md` (prose, SemVer footer, Sync Impact Report slot) +
`constitution.yaml` (arity constraints, budgets, drift thresholds) +
`assumptions.yaml` + `value-checks.yaml` + `taxonomy.yaml` — all with `[ALL_CAPS]`
placeholders. `constitution_pin: unratified` is legal until ratification.

## Bump rules (Q33 — written in, not advisory)

| bump | meaning | consequence |
|---|---|---|
| MAJOR | a principle removed or incompatibly redefined | `stale` + gate-5 → dispatch re-examination |
| MINOR | a principle added or substantially extended | `stale` + gate-5 → dispatch re-examination |
| PATCH | wording only | **nothing** |

Mislabeling a substantive change as PATCH is the one social failure this mechanism
cannot self-correct — the Sync Impact Report (`old → new`, changed principles,
deferred TODO) makes the diff visible to review.

## Re-examination dispatch (Q33 A+)

MINOR/MAJOR → all `constitution_pin`-older theses marked `stale` → **budget report
first** (affected theses × pillars) → human confirms via gate 5 → dispatch. Scope
is bounded by the Sync Impact Report (only pillars depending on amended principles).

## Invocation

```bash
python3 scripts/agentii_cmd.py constitution scaffold --workspace /path/to/workspace
python3 scripts/agentii_cmd.py constitution amend --workspace /path/to/workspace --bump minor --note "..."
```
