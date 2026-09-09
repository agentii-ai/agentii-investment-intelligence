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
python3 scripts/agentii_cmd.py specify --workspace /path/to/workspace --slug ai-semiconductors
```

Gate 1 (after specify, informational) shows pillar/`wrong_if` decidability.
