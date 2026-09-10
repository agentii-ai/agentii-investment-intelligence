---
name: clarify
description: "The research-domain clarification skill — find underspecified items in a thesis spec.md (prose wrong_if, universe rows without rationale, missing budget/expiry/pins, ambiguous pillars), ask the human structured questions WITH options (max 5 per round), encode the answers back into spec.md's Clarifications section, and re-evaluate checklists/thesis-quality.md after every write (Q32 bidirectional maintenance)."
role: kit
market_data_stage: none
---

# agentii.clarify

The 8th kit command — closes the gap Q32 itself assumed: upstream
`speckit-clarify` re-evaluates the quality checklist after every spec write, but
spec 046 never named the command that performs the clarification.

## Two phases

### 1. Analyze (deterministic)

```bash
python3 kit-scripts/agentii_cmd.py clarify --thesis theses/001-… --questions
```

Emits a JSON list of candidate questions, each with:
- `id` (stable — content-derived from the target)
- `target` (pillar id / field / universe row)
- `question` (exact, in the spec's working language)
- `options` (derived where possible; null = free-form)

Candidates come from a **deterministic scanner** (never vibes): prose `wrong_if`
(missing `metric=`/`threshold=`/`source=`), universe rows without rationale,
missing `budget`, missing `expiry_triggers`, subscription tokens not in
`TICKER × skill` form, missing `as_of`/pins, pillars without priority.

### 2. Encode (after the human answers)

```bash
python3 kit-scripts/agentii_cmd.py clarify --thesis theses/001-… --answers '<json>'
```

- Appends each answer to `spec.md`'s `## Clarifications` section
  (`- [YYYY-MM-DD] Q: … → A: …`).
- **Re-evaluates `checklists/thesis-quality.md` after the write** (Q32: the
  machine-maintained checklist is bidirectional — report "N/M items passing"
  plus regressions).

## Rules

- **Max 5 questions per round** (upstream v1.0.4's tightened limit; spec recorded
  it as the convention to follow).
- Only ask what blocks the next step — every question must name the field it
  unblocks.
- Answers are encoded verbatim (professional English); a Chinese question is
  translated to English before encoding (the project's first language is English).
- Never ask about facts obtainable from the platform (that's the skills' job);
  clarify **intent** only.
