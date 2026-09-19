---
# thesis.md — the HUMAN's file. Prose, with this frontmatter at byte 0.
#
# `writer:` is not decoration. The write boundary refuses a write to a document that
# declares a different writer, and treats an UNDECLARED document as append-only — so
# omitting this line does not mean "anyone may write it", it means "nobody may
# rewrite it", silently. Machine state lives in `thesis.reduce.json`, written by
# reduce_journals. See `contracts/thesis.md`.
writer: agentii.specify
mode: thesis
thesis_id: [THESIS_ID]
claim: ""                 # one sentence; empty until the human states it. NOT a placeholder —
                          # `[TBD]` is truthy, so it would satisfy a presence check while meaning nothing.
pillars: []               # the spec schema wants minItems 1; a fresh scaffold is deliberately
                          # incomplete, and pillar population is the G1/promotion moment.
known-open: []
depends_on: []
macro_sensitivity: medium
expiry_triggers: []
budget: {max_tasks: 40, max_retries_per_task: 2}
as_of: [AS_OF]
constitution_pin: [CONSTITUTION_PIN]
assumption_pin: [ASSUMPTION_PIN]
# corpus_version and skill_pin are ABSENT until earned, and that is deliberate:
# a thesis has retrieved nothing at scaffold time. Writing `skill_pin: [TBD]` would be
# truthy, so `g1_gate.check_frontmatter` would pass it while it pinned nothing.
---

# Thesis: [THESIS_NAME] — the living file

**Two files, one writer each** (Q5/Q15, and the fix for a real defect):

| file | who writes it | what it holds |
|---|---|---|
| `thesis.md` (this file) | you, and `agentii.specify` once | the prose, and the identity fields above |
| `thesis.reduce.json` | `reduce_journals` — only | `judgment` (conviction, claims, wrong_if) + `mechanical` |

`reduce_journals` used to write JSON to *this* path. The boundary refused it (this file
declared no writer, so it read as append-only) and the refusal was silent — the reducer
printed success over a write that never happened, and this file stayed a scaffold
forever. The split is what makes each half writable by exactly one writer.

## Claim History *(conviction is a function of evidence — Q8)*

| version | date | conviction | trigger |
|---|---|:---:|---|

## Wrong If *(machine-checkable — Q8 contract 4)*

| pillar | metric | threshold | source | op |
|---|---|---:|---|---|

## Known Open

- (unresolved items; converge re-proposes them next cycle — Q14)
