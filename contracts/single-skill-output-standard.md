# The single-skill output standard

**Status**: in force for the nine `equity-research-core` skills since 2026-09-25 (spec 062 `T084`).
**Scope**: every skill that produces one artifact for one ticker. Adoption by the rest of the kit is
the kit's work — §6 states what that requires and what is already known to diverge.

**Why this document exists, in the owner's words**: *"要求事实的后面有 agentii.ai/v 引用定位到页的链接
（往往不需要在最后再输出 citation list，人们更希望看到事实或者数据旁边紧挨着的位置的链接）"* — the link belongs
**beside** the fact, and a trailing list replaces proximity with a hop.

**Authority, stated so no reader has to guess.** This document is the **bar** — what the standard is and
what it was measured against. `contracts/citation-and-memory.md` is the **operational contract** — the
rules a skill applies at run time. They state the same rules; where they could drift, the operational
contract is what the skills read and this document is what says why. Neither is a copy of the other's
purpose.

---

## 1. The file shape

1. **Every material fact, table row and metric carries its clickable link immediately beside it.**
   "Beside" is the same line or **one line either side** — an artifact that cites on the line beneath is
   citing beside the fact, and an artifact that defers it to the end is not.
   The link is `https://agentii.ai/v/{ticker}/{citation_id}/{N}` (path-based; see
   `contracts/skill-methodology-template.md` § *Citation Link Format*).
2. **Citation density ≥ 1 per 200 words**, counted over those links.
3. **A bottom Citations roll-up is OPTIONAL** — never required, and where kept it must not repeat a link
   the prose already carries. It was a required element until 2026-09-25; it is not one now, because an
   artifact whose every fact carries its link needs no second hop.
4. **Coverage gaps are required.** What could not be retrieved is part of the deliverable — a gap that is
   not written down reads as coverage.
5. **Findings are tagged `[FACT]` / `[DEDUCTED]` / `[VIEW]`**, so a reader can tell what was observed
   from what was inferred.
6. **The five pins** (`as_of`, `constitution_pin`, `assumption_pin`, `corpus_version`, `skill_pin`) are
   present **with values that carry information** — a key test passes 206 of 206 corpus artifacts and a
   placeholder is not a value.

## 2. The chat shape

The closing reply is a **summary a reader can use without opening the file**, in this order: **title**
(`{ticker} · {skill} · {as_of}`) · **key conclusions** (3–5 one-liners, tagged) · **key metrics** (3–6
numbers a reader would repeat to someone else) · **Executive Summary** · **Key Citations** (the headline
**5–10** facts, each a clickable `/v/` link).

**It is a summary, not a copy**: every headline in the chat must already appear in the file beside its
link, and nothing may appear in the chat that the file does not carry.

## 3. What checks it, and what each instrument cannot see

| instrument | asks | cannot see |
|---|---|---|
| `scripts/check_output.py` | R1 pins · R2 density · R3 no duplicated roll-up · R4 a material fact carries a link beside it | whether a link **resolves**, whether it is the **right** page, and whether the prose is any good |
| `scripts/check_output_quality.py` (058 `T024`/`T025`) | each skill's **own** declared `## Output Structure`: elements present, executive-summary budget, density, badges, the five pins **by value** | the same two, plus anything the skill did not declare |
| `T083`'s rubric (062) | conclusion quality, honest tagging, whether a reader would pay for the answer | — it is the only one of the three that judges the *content* |

Both scripts are **advisory by default**; `--strict` gates. That split is deliberate and is `FR-050`'s:
a *defect* is wrong at any size, a *below-standard* artifact may be a shorter document. `R3` fires on 49
of 50 artifacts in the corpus this standard was calibrated against, so it cannot be a blocking gate
before its own backlog is cleared.

**The two instruments disagreed until 2026-09-25** — `check_output.py` R3 rejects a trailing roll-up
while `check_output_quality.py` criterion 5 required one — and neither read the skill's own text. The
repair made the skill the authority (`FR-002`) and gave R4's definition one implementation instead of
two. Recorded because a reader who finds only one of the two scripts should know the other exists.

## 4. The measurements the standard rests on

Corpus: the held-out workspace's **50 artifacts**, one per skill class
(`B/agentii-physical-ai/theses/00{1,2,3}-*/artifacts/{TICKER}/*.md` — **the `-*` matters**: a path written
without it is a glob that matches nothing). Re-measured 2026-09-25; the reproduction is in
`specs/062-page-retrieval-evaluation/evidence/output-lint-calibration.md`.

| | before the standard | |
|---|---|---|
| duplicated trailing roll-up present | **49 of 50** | so the roll-up was duplication, not the only citation channel |
| cites nothing inline | **1 of 50** | 1,756 words, density 0.0 — the red case `T082` is registered on |
| a material fact with no link beside it | **26 of 50** | the `T084` backlog |
| citation density | 0.0 – 8.77, median **6.225** | the standard is not uniform today |

**Two figures in the first version of that record did not reproduce** (R4 said 28, the code produces 26;
the median said 6.24, the upper middle value rather than the median). Corrected, and the correction is
kept in place rather than overwritten — a number that reads as measured and is not reproducible from its
producer is the defect this specification is about, and it was found in this specification's own evidence.

**`T084`'s effect is not yet measurable.** The lint reads *artifacts*; `T084` changed *skill
instructions*. Until the nine skills run again and emit new artifacts (058 `T096`/`T098`), `R3` reads 49
of 50 **before and after**, by construction. The 49 must not be quoted as a verdict on `T084`.

## 5. What is deliberately NOT part of the standard

A lint that tried to judge quality would be a blocking check wearing a rubric's clothes. So the standard
does **not** require: a minimum artifact length, a minimum number of citations in absolute terms, a
particular section order beyond the skill's own declaration, or any particular prose style. Those are
`T083`'s rubric and the skills' own `## Output Structure`, not this document's.

## 6. Adoption by the rest of the kit — what is known to diverge

- **40 skills across the other vertical plugins** declare `### Key Citations` with a **0–10** bound
  (canonical wording in `CHANGELOG.md`'s `FR-081` entry) and teach the roll-up as a required element. The
  nine use `**Key Citations**` with **5–10**. **0–10 admits an empty list where 5–10 does not**, and that
  is the substantive difference, not the heading level.
- `README.md` and `CHANGELOG.md` state the roll-up as part of the policy. The CHANGELOG is a record of
  what shipped and should not be rewritten; the README describes the kit's current standard and should
  follow whoever resolves the divergence.
- **Resolving it is the kit's work, not spec 062's** — 062's fence is the nine (`FR-022`). This section
  exists so the divergence is a recorded state rather than a silent one.
