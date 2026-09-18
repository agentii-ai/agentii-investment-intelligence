# Disclaimer — canonical template (spec 046, presentation-shaped outputs)

**Single source of truth.** This file is the only place the disclaimer text is authored. The
presentation-shaped outputs (`thesis-report.html`, `dashboard.html`, `pitch-deck`,
`earnings-preview`) must include it; none of them may restate, paraphrase or fork it.

> **Why a closed set rather than a judgement.** "Consequential output that may be used for
> dissemination" is a criterion, and a criterion applied per-output is applied inconsistently.
> The four outputs above are the ones whose **form implies an audience**. A new output type that
> is presentation-shaped is added here — once — rather than re-litigated at each use.
> (The same move as Q131: a decision made at authoring time, not at use time.)

## Rules

| # | Rule |
|:---:|---|
| 1 | Every presentation-shaped output **includes this block verbatim**. It is template-owned where the output has a template; the author does not write it. |
| 2 | **Placeholders are filled, never shipped.** `[WORKSPACE]` / `[AS_OF]` / `[GENERATED]` must resolve — an unfilled placeholder fails the output gate (the same structural, case-insensitive check as Q108). |
| 3 | **Language follows the workspace** (Q126). This file carries the canonical English text; a workspace declaring another language uses its own rendering of the *same* clauses. The clause set is the contract; the wording is not. |
| 3b | **The CLAUSE SET is what rule 3 is checked against.** Every `<p>` carries `data-clause="…"`; a workspace rendering in another language must carry the **same id set, exactly**. Missing a clause fails the output gate; adding one is allowed only by adding it here first. Without stable ids, "the clause set is the contract" is unenforceable — a translation could silently drop the liability clause and still read as compliant. |
| 4 | **A disclaimer is not a substitute for the document's own epistemic discipline.** It states what the document *is*; the badges, `epistemic_state` and coverage-gaps sections state what each claim *is*. Do not let the disclaimer carry a burden the body should. |
| 5 | **Never present the disclaimer as a substitute for an absent one.** If a rendering cannot carry it (a format with no text layer), the output is not presentation-ready and must not be disseminated. |

## The block (markdown/canonical)

```markdown
---

### Disclaimer

This document is **research and analysis**, produced by an automated research system for
internal use. It is **not investment advice**, and it is **not an offer or solicitation** to
buy or sell any security.

It is based on the sources cited inline. Those sources may be incomplete, delayed, or wrong,
and the analysis may have misread them; no representation or warranty is made as to accuracy
or completeness. Figures are as of their stated `as_of` date and are not updated.

**This document contains hypotheses, not established conclusions.** Where a claim is a
projection, an inference, or a judgement rather than a reported fact, it is marked as such.
Statements about the future are forward-looking and inherently uncertain. Past performance is
not indicative of future results.

Recipients must do their own due diligence and consult their own advisers before acting on
anything here. The authors and distributors accept no liability for any loss arising from
reliance on this document.

© [WORKSPACE] · [AS_OF] · generated [GENERATED]
```

## The block (HTML rendering — for `thesis-report.html` and `dashboard.html`)

Styled to the letter-page geometry. `.disclaimer` is a **reserved class** — the assembler
injects it, the author never emits it (same reserved-class discipline as `sheet-head` /
`page-mark`).

```html
<section class="disclaimer">
  <h3>Disclaimer</h3>
  <p data-clause="not-advice">This document is <b>research and analysis</b>, produced by an automated research system
     for internal use. It is <b>not investment advice</b>, and it is <b>not an offer or
     solicitation</b> to buy or sell any security.</p>
  <p data-clause="sources-fallible">It is based on the sources cited inline. Those sources may be incomplete, delayed, or
     wrong, and the analysis may have misread them; no representation or warranty is made as
     to accuracy or completeness. Figures are as of their stated <code>as_of</code> date and
     are not updated.</p>
  <p data-clause="hypotheses-not-conclusions"><b>This document contains hypotheses, not established conclusions.</b> Where a claim is a
     projection, an inference, or a judgement rather than a reported fact, it is marked as
     such. Statements about the future are forward-looking and inherently uncertain. Past
     performance is not indicative of future results.</p>
  <p data-clause="own-due-diligence">Recipients must do their own due diligence and consult their own advisers before acting
     on anything here. The authors and distributors accept no liability for any loss arising
     from reliance on this document.</p>
  <p class="disclaimer-meta">© [WORKSPACE] · [AS_OF] · generated [GENERATED]</p>
</section>
```

## Placement

| Output | Where it goes | Why there |
|---|---|---|
| `thesis-report.html` | **Last page**, after coverage gaps and before the closing sheet-foot | A reader who has finished the document reads it in place; it does not consume front-page budget |
| `dashboard.html` | **Footer band**, always visible | Interactive and scrollable — a last page can be missed entirely |
| `pitch-deck` | **Final slide** | The deck's own convention |
| `earnings-preview` | **Final slide**, and repeated in the footer of every slide carrying a price target | A slide can be extracted and forwarded alone; the disclaimer must travel with the number |

## Optional — the derived line (not required, worth considering)

Because spec 046 already tracks what each claim *is*, the report can state its own epistemic
posture in one derived sentence rather than leaving the reader to infer it:

> *Of N pillars, M were supported by evaluated evidence; K could not be evaluated at all.*

This is **derived, not declared** — the same discipline as Q113/Q134. It is listed here as a
possibility, **not** as part of the required block: a legal disclaimer must not depend on a
computation that can fail, and a wrong count in a disclaimer is worse than no count.
