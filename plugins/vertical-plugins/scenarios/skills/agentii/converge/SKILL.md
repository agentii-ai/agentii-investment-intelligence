---
name: converge
description: Append-only gap closure and the cadence engine for research theses. Evaluates artifact CURRENT state (never git history, never task checkboxes) against current pins and wrong_if falsifiers, then appends a Convergence section to tasks.md re-proposing the gaps. A clean run leaves tasks.md byte-identical. Deterministic gaps (stale, invalidated) are uncapped; judgment-class gaps are capped per spec 046 Q40.
role: kit
market_data_stage: none
allowed_tools: []
retrieval_scope: structured_only
---

# agentii.converge

Append-only gap closure — the cadence engine of the research orchestration system (spec 046 Q26).

## When to run

- After every `agentii.implement` batch (the system detects its own staleness).
- On any cadence cycle (quarterly re-visits, post-earnings, post-constitution-bump).
- Before any IC review (the conflict list must be current).
- When the cross-stock synthesis tasks complete, close the loop with the report
  workflow — see `skills/agentii/synthesize/SKILL.md` (pack → author
  content.html → assemble). An `html_stale` finding below means that workflow
  must re-run.

## What it does

1. **Evaluates current state** — artifacts on disk, pins in frontmatter, `wrong_if`
   falsifiers in `thesis.md`. It never reads git history and never trusts `[x]`
   checkboxes (Q26 A+: the ledger may lie; the correction is deterministic and has
   a bounded expiry — the next converge).
2. **Appends, never rewrites** — the only write is a `## Phase N: Convergence`
   section at the end of `tasks.md`, with `src:` refs and content-derived finding
   IDs. Existing lines, including previous Convergence sections, are untouched.
3. **Clean run = byte-identical** — no gaps means no empty section header.

## Gap types

| Type | Class | Cap |
|---|---|---|
| `stale` (pins older than current) | deterministic | uncapped |
| `invalidated` (`wrong_if` metric+threshold triggered) | deterministic | uncapped |
| `missing` / `partial` / `contradicts` / `unrequested` | judgment | Q40 cap (≈50) |

## Invocation

```bash
# Resolve the kit root first — contracts/kit-root.md. The kit's scripts do NOT ship
# with the skills, so never assume the CWD is the checkout.
KIT=""
for c in "${AGENTII_KIT_ROOT:-}" \
         "$(cat "$HOME/.claude/skills/agentii/.kit-root" 2>/dev/null)" \
         "${CLAUDE_PLUGIN_ROOT:-}"; do
  [ -n "$c" ] && [ -f "$c/scripts/agentii_cmd.py" ] && { KIT="$c"; break; }
done
if [ -z "$KIT" ]; then d="$PWD"; while [ "$d" != "/" ]; do
  [ -f "$d/scripts/agentii_cmd.py" ] && { KIT="$d"; break; }; d="$(dirname "$d")"; done; fi
[ -n "$KIT" ] || { echo "agentii kit not found — see contracts/kit-root.md" >&2; exit 1; }

python3 "$KIT/scripts/converge.py" --thesis theses/001-ai-semiconductors \
  --pins '{"assumption_pin": 1, "corpus_version": "2026-08", "as_of": "2026-09-08", "constitution_pin": "0.1.0", "skill_pin": "recent-quarter:abc"}'
```

## Hard rules (Q26)

- Never modify `spec.md` or `plan.md`.
- Never rewrite, renumber, reorder, or delete any existing task.
- Finding IDs are content-derived (`hash(entity+metric+period+gap_type)`) — an
  unchanged re-run appends nothing.
