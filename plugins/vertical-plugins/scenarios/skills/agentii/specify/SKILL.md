---
name: specify
description: Create a research thesis — theses/{nnn}-{slug}/ via mkdir-as-CAS, pillar-prioritized spec.md, initialized thesis.md, and the thesis-quality checklist. Refuses creation while the workspace constitution is unratified (spec 046 Q83 A+).
role: kit
market_data_stage: none
---

# agentii.specify

Creates a research thesis directory and its specification.

## Hard rules

- **Refuse creation while `constitution_pin: unratified`** (Q83 A+): no research may
  be produced under placeholder governance. Aggregate checks and staged orders
  hard-fail on `unratified` — a thesis created early could never be re-reviewed
  properly (no old constitution to diff against).
- ID allocation is **mkdir-as-CAS** (Q27): `os.mkdir()`; `FileExistsError` →
  increment and retry. Never `exist_ok=True`.
- Pillars are priority-ordered and **independently falsifiable** (Q30): P1 = the
  Minimum Defensible View; every `wrong_if` is `{metric, threshold, source}` —
  prose is rejected (Q8 contract 4).

## What it produces

```
theses/{nnn}-{slug}/
├── spec.md                       # pillar-prioritized (spec-template.md)
├── thesis.md                     # initialized living file (thesis-template.md)
└── checklists/thesis-quality.md  # machine-maintained, bidirectional (Q32)
```

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

python3 "$KIT/scripts/agentii_cmd.py" specify --workspace /path/to/workspace --slug ai-semiconductors
```

Gate 1 (after specify, informational) shows pillar/`wrong_if` decidability.
