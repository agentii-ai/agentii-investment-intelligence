# Report readability — what makes a `synthesize` report readable

**Spec**: 058-skills-api-optimization `FR-063`–`FR-067` · **Derived**: 2026-09-22 · **Corpus**: the
Morgan Stanley sell-side archive at `/Users/frank/JMM/industry/` (73 reports, 3,806 pages)

**Methodology only.** Nothing below quotes, paraphrases or stores report *content*. What was mined is
the **form**: where things sit, how often, in what order. This applies spec 039's standing ruling
(`specs/039-enhance-skills/spec.md:251`, 2026-07-17 — *"Paraphrase methodology only… MUST NOT reproduce
transcript text or verbatim course phrasing"*), which was written for paid course transcripts and is
applied here by extension, because the IP case for licensed sell-side research is at least as strong.

---

## 1. Why this contract exists

`style.md` (139 lines) defines **formatting**. The `synthesize` skill defines **content**. Neither
defines how a report must **read** — a search of `style.md` for *readability, narrative, prose,
argument, lede* or *headline* returns **zero hits**. So a report could carry an Executive Summary,
classification badges and complete citations and still be a heap of figures, which is the failure
reported from real use.

The only readability-adjacent check in the kit was a keyword test for
`implies / means / therefore / argues for` (`scripts/synthesize_report.py`), and a sentence satisfies
it while restating data. Two tiers replace it, and **the split is the contract**: the blocking tier
holds what text can decide; the scored tier holds what it cannot; and a reader must never be able to
read *"passes the gate"* as *"reads well"*.

---

## 2. What the corpus actually shows — and where it contradicts `FR-064`

**This section is the most important one, because the derivation did not confirm the requirement that
commissioned it.** `FR-064` names four mechanically checkable conventions. The corpus supports two of
them cleanly, contradicts one, and contradicts a fourth for the largest family in the archive.

| `FR-064` names | Corpus finding | Verdict |
|---|---|---|
| lede-before-evidence | Ledes are **definitional scope first, headline figure second** — a scope sentence with no numeric token, then the metric with its comparator. Consistent across the long-form families. | **Supported**, as a report-level rule |
| no paragraph consisting only of numbers | The interpretive floor on numeric sentences is **≥0.25** across all 18 sampled documents (observed minimum 0.27). Figures are never bare for long. | **Supported** |
| exhibit-takeaway presence | Only **43–49%** of exhibit sections in the largest family carry interpretive text after them; the rest are numeric-only **by design**. | **Contradicted** — cannot block |
| conclusion-first section ordering | **77–80 of 103–106 sections** in the largest family open preamble-first. Those sections are not defective: the call lives in the document lede, not in every section. | **Contradicted** — cannot block |

**What this means, stated plainly.** `FR-063` mandates deriving the conventions **from the corpus**;
`FR-064` names four in advance. Where they disagree, the derivation wins — a gate that fails 75% of the
largest family's sections is not a readability standard, it is a rule about a different genre. **The
owner should decide whether `FR-064`'s list is amended**, and this note is the evidence for that
decision rather than a silent reinterpretation.

### The family that breaks the most rules

Four families sit in the archive and **they are not one genre**:

| Family | Shape | Consequence for this contract |
|---|---|---|
| **Market_Share** (30 docs, 91–97 pp) | chart-dominant; ~36–39 exhibits each; **no rating, price target or call anywhere in the body** (100% of rating tokens appear after the 70% mark, and the first sits inside the disclosure tail) | A blocking check requiring a call would fail **30 of 73 documents** |
| **CT_tracker** (22 docs, 13–19 pp) | table-and-record dominant; 33–44% table markup; analytical payload is a bulleted record list | Prose checks are near-meaningless here, and its headings embed their exhibit references |
| **Takeaways** (3–30 pp) | the most conventionally prose-like | The family most of `FR-064` was probably imagined from |
| **GLP-1** (18 docs, 6–88 pp) | **not a genre** — 6 to 88 pages spanning food, LatAm, China, healthcare, audio summaries and pharma; two members contain no exhibit at all | Any threshold fitted to its large members fails its small ones |

**Directory membership is not a valid proxy for document type**, and any check that assumes one genre
will mis-score three of the four families.

---

## 3. The blocking tier — what text can decide

Derived in `scripts/check_report_readability.py`. **Eight checks are supported by the corpus; four are
implemented and blocking today** (rows 3, 5 and the two `FR-064` conventions the corpus backs), and this
table is the honest state rather than the finished one: rows 1, 2, 4, 6, 7 and 8 are *specified and
corpus-evidenced* but not yet written, and they are listed here so the gap is recorded rather than
implied. What is implemented is ordered so cheap structural integrity runs before anything interpretive.

| # | Check | Corpus basis | False-positive risk |
|---|---|---|---|
| 1 | Header integrity — a self-declared report-type tag | 73/73 | negligible; **unknown tags warn, never fail** (four of seven observed values are rare) |
| 2 | Disclosure boundary present, body non-empty | 73/73 | negligible for presence; **must not assert a position**: body share ranges 0.056–0.865 |
| 3 | Exhibit numbers monotonic in order of appearance | 58/58 | lowest of any check. **Gaps permitted; need not start at 1** |
| 4 | An exhibit referencing form is present (inline **or** heading-embedded) | 71/73 | low. **Must not require references to resolve** — see §4 |
| 5 | Interpretive floor ≥0.25 on numeric sentences | min 0.27 across 18 | low **at that floor**. A 0.5 floor would fail all 30 Market_Share documents. ⚠️ calibrated on the extracted text layer, applied to rendered HTML — see below |
| 6 | Enumerated-category coverage with placeholders | 22/73 have the structure | low, **family-gated** — conditioned on detecting the structure, never corpus-wide |
| 7 | Series stability against the series median | Market_Share stable to a few % across 8 months | low, but **needs ≥2 documents**; per-series, never per-directory |
| 8 | No section body composed solely of numeric tokens | no sampled document does this | low; weak discriminator, cheap to run |

### What is implemented today, against the eight above

| Implemented | Status |
|---|---|
| `check_lede_before_evidence` | blocking — `FR-064` convention 1, report scope |
| `check_numbers_only_paragraphs` | blocking — `FR-064` convention 3 |
| `check_interpretive_floor` | blocking — corpus row 5 |
| `check_exhibit_monotonicity` | blocking — corpus row 3 |
| `check_exhibit_takeaways` | **reported only** — `FR-064` convention 2, corpus-contradicted |
| `check_conclusion_first` | **reported only** — `FR-064` convention 4, corpus-contradicted |
| header integrity, disclosure boundary, reference presence, category coverage, series stability, numeric-only body | **specified, not yet written** |

### The four `FR-064` conventions, as implemented

Two are blocking, at the scope the corpus supports. Two are **reported, not blocking**, with the
measurement attached to each so the reason is visible in the output rather than only here:

- **lede-before-evidence** (`check_lede_before_evidence`) — blocking, **report scope**. The corpus
  supports a lede rule; it does not support one that fires on every section (§2, row 4).
- **numbers-only paragraph** (`check_numbers_only_paragraphs`) — blocking. Directly supported.
- **exhibit-takeaway** — **reported, not blocking.** The corpus breaks it at ~50% in the largest
  family. Adjacency to an exhibit is also unreliable as a signal: trailing text is frequently an axis
  label, a units note or a source line, and no text-only rule separates those from a reading.
- **conclusion-first** — **reported, not blocking** beyond the lede. The corpus contradicts it at
  section scope in ~75% of the largest family's sections.

**The gate's firing rate on the shipped reports is itself evidence.** Run over the six delivered SPCX
reports (2026-09-22) the four `FR-064` conventions returned 7 findings; one was checked by hand and was
the checker's fault (a four-word `metric=…` annotation sat between an exhibit and its 104-word
takeaway). That is why the annotations are skipped now — and why the remaining findings are reported
rather than obeyed.

---

## 4. What must NOT be checked, with the measurement

Each of these is a plausible-sounding rule that the corpus falsifies. They are listed because **the
tempting wrong check is the expensive one** — it ships, fires on real work, and gets disabled.

| Rejected check | Why |
|---|---|
| A call / rating / price target in the body | Fails **30 of 73**. Market_Share is descriptive by design |
| Every inline exhibit reference resolves to a defined exhibit | Fails **essentially every document**. Referenced-but-never-defined runs to 126–132 per document — cross-references to companion and prior notes |
| Exhibit numbers are contiguous, or start at 1 | Fails freely. Numbers skip, and Market_Share's headings are a *subset* of its numbered exhibits |
| Analytical body must be ≥X% of the document | Body share ranges **0.056–0.865**, and varies within families. Any X above ~0.05 fails real documents |
| No empty sections | Fails **22 documents**. Empty enumerated categories carry a deliberate placeholder |
| Infer document type from its directory | The GLP-1 directory spans 6–88 pages and a 0.00–0.54 lead-in rate. Directory ≠ genre |

---

## 5. The scored tier — what structure cannot see (`FR-065`)

Implemented in `scripts/score_report_readability.py`. **Non-blocking by construction**: it exits 0, and
its rubric cannot be answered by a regex. The author scores it as part of the authoring step.

| Criterion | The question the author answers |
|---|---|
| argument | Does each key argument state a call an analyst could disagree with — or merely describe? |
| lede | Does the opening state the RIGHT call — the one the evidence actually supports? |
| exhibits | Do the takeaways interpret the figures, or restate them? |
| balance | Is the report prose with evidence in it, or evidence with prose attached? |
| read-through | Read end to end, does the conclusion follow from the evidence presented? |

**The score has a named consumer and a consequence**, because `FR-040` requires that a field recording a
condition either triggers an action or is removed, and a score nobody reads is that same defect. The
consumer is the **human reviewer**; the score is recorded in the report's frontmatter beside the pins
(`T091`); and a score **below the previous release's** must be explained in the deliverable itself. The
trigger is a **regression, not a threshold**, so no score is decided in advance and the first report
sets its own baseline. A threshold-with-a-warning is what `check_disclaimer.py` was before Check 48 —
described in its own comments as the enforcement point, and invoked by nothing.

---

## 6. Derived vs not yet sourced (`FR-066`, `SC-017`)

**Derived from the corpus:** every convention in §3 and §5, from the Morgan Stanley archive.

**NOT derived, and stated as a gap rather than presented as a finding:**

- **Buy-side conventions.** The corpus is not on disk. `references/bridgewater/` turned out to hold
  **arXiv machine-learning papers, not investment writing**, and the top-50 fund material is crawled by
  spec 037 rather than stored. So this contract describes **sell-side** readability and says so; it does
  not claim to describe what a top equity fund's internal memo looks like, which is a different genre
  with different conventions (and plausibly a different relationship to the call — an internal memo has
  no need to persuade).
- **Any convention inferred from a family of one.** The archive's four families disagree with each
  other often enough that a rule supported by one and untested against the others is recorded as
  **family-specific**, not general.

### The interpretive-floor finding on the delivered reports, with its caveat

Run against the six SPCX reports, `interpretive-floor` is the **only** blocking finding that survives
(two reports, 17% against the 0.25 floor). It is the closest thing in this contract to a measurement of
the reported symptom — *a heap of facts and data* — and it is deliberately not presented as proof:
the floor was calibrated on the corpus's **extracted text layer**, while the check runs on **rendered
HTML** where table cells flatten into the sentence stream and are numeric without interpretation. That
inflates the denominator, so 17% here is not strictly comparable to 27% there. Settling it needs the
same extraction on both sides.

It is recorded rather than resolved because a threshold that looks precise and is applied to a different
layer than it was measured on is exactly the number that gets quoted without its caveat.

### A note on the extraction layer

All measurements come from the corpus's extracted text artefacts. That is the right layer for a
text-only contract, but it is not identical to the rendered PDF — footers, sidebars and chart axis
labels flatten differently. Every check in §3 operates on signals robust to that flattening (heading
text, token sequences, counts). The **bold-lead-in rate** and **table-markup share** are
extraction-dependent and are deliberately **not** used in any check until re-baselined against whatever
extraction this contract runs on.
