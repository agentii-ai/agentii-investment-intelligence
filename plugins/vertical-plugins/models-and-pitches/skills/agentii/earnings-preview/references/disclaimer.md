# Disclaimer requirement (Q139/T137) — full text

The body of SKILL.md carries only the binding rule; the reasoning lives here, so the
skill body stays inside its context budget (the `ctx-gate-body-size` gate caught this
at 1358 words against a 1300 limit — its own advice was "move detail to references/").

## The rules

1. Include the canonical block from `scenarios/templates/disclaimer.md` as authored.
   Do not write your own, restate it, or paraphrase it.
2. `[WORKSPACE]` / `[AS_OF]` / `[GENERATED]` are FILLED, never shipped. An unfilled
   placeholder fails the output gate (the same structural, case-insensitive check as
   Q108).
3. **Language follows the workspace** (Q126). The canonical file is English; a
   workspace declaring another language supplies its own rendering of the SAME
   clauses. The clause SET is the contract — every `<p>` carries `data-clause="…"`,
   and a rendering that drops one is not a translation, it is a different disclaimer.
4. The disclaimer states what the document IS; the badges, `epistemic_state` and
   coverage-gaps sections state what each claim IS. Do not let the disclaimer carry
   a burden the body should.

## Why this is written down at all — this skill has no template and no producer

Measured 2026-09-18: `scenarios/templates/` holds neither a pitch-deck nor an
earnings-preview template, and no producer script exists. So there is nothing yet to
mount the disclaimer ON, and `check_disclaimer.py` reports both as `nothing to gate
yet` rather than as compliant.

Recording the requirement in the output contract means it is already binding when a
template or producer is written, instead of being rediscovered afterwards — which is
how the thesis report's own disclaimer came to be retrofitted rather than designed in.

## Additional requirement — the footer of every slide carrying a price target

`earnings-preview` is the one presentation-shaped output that repeats a **price
target** across slides, so it carries the disclaimer **twice**: once as the closing
block, and once as a **footer on every slide that states a price target**.

The reason is not redundancy. A deck is read OUT of order and in fragments — a reader
can meet the price-target slide without ever reaching the closing disclaimer, and a
price target is exactly the thing a reader acts on. A disclaimer a reader never
reaches does not discharge the obligation it exists for. `thesis-report.html` needs no
such rule because it is a single continuous document with one ending.
