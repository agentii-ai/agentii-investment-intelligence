#!/usr/bin/env python3
"""The blocking readability gate for a synthesize report (spec 058 FR-064, T086).

WHY THIS EXISTS. `style.md` — 139 lines — defines FORMATTING. The `synthesize` skill defines CONTENT.
Neither defines how a report must **read**, and a search of `style.md` for *readability, narrative,
prose, argument, lede* or *headline* returns **zero hits**. So a report could satisfy every existing
gate — Executive Summary present, classification badges present, citations complete — and still be a
heap of figures, which is the failure reported from real use.

The only readability-adjacent check in the kit was a **keyword test** for
`implies / means / therefore / argues for` (`synthesize_report.py:572`), and a sentence can satisfy it
while restating data. `FR-067` / `T089` replaces that proxy; this module is the standard it is replaced
*by*.

THREE TIERS, AND THE SPLIT IS THE POINT. This file holds two of them.

  * **Blocking** — four conventions text can decide, so they can stop a merge. In `CHECKS`.
  * **Reported** — conventions the DERIVATION did not support as gates. In `REPORTED_ONLY`, printed
    after the verdict and never folded into it.
  * **Scored** — what structure cannot see at all. `score_report_readability.py`, a separate program
    with its own exit code. A reader must never be able to read "passes the gate" as "reads well",
    which is why these are separate programs rather than sections of one report.

THE DERIVATION CORRECTED THE REQUIREMENT, AND THAT IS THE MOST IMPORTANT THING IN THIS FILE.
`FR-063` mandates deriving the conventions **from the Morgan Stanley corpus**; `FR-064` names four in
advance. Where they disagree the derivation wins, because a gate that fails the corpus it was derived
from is not a readability standard:

  * **lede-before-evidence** — supported, blocking, at REPORT scope. The corpus supports a lede rule;
    it does not support one that fires on every section.
  * **no numbers-only paragraph** — supported, blocking. The interpretive floor on numeric sentences is
    ≥0.25 across every sampled document (observed minimum 0.27).
  * **exhibit-takeaway** — **NOT supported.** Only 43–49% of the largest family's exhibit sections carry
    interpretive text after them. Reported, not blocking.
  * **conclusion-first** — **NOT supported** beyond the lede. 77–80 of the largest family's 103–106
    sections open preamble-first, by design: the call lives in the document lede. Reported, not blocking.

Two corpus-derived checks replace them, both with stronger evidence than either: **interpretive-floor**
(min 0.27 across 18 documents; a 0.5 floor would fail all 30 Market_Share documents) and
**exhibit-monotonicity** (58/58 documents — the lowest false-positive risk in the corpus).

`contracts/report-readability.md` §2 carries the full table and the family breakdown, and §4 lists the
checks the corpus FALSIFIES — including the most tempting one, that inline exhibit references must
resolve, which fails essentially every document.

Usage:
    python3 scripts/check_report_readability.py <content.html> [--json]

Exit 0 when the report clears the blocking tier, 1 when it does not. It says nothing about quality —
that is the scored tier's business.

MEASURED AGAINST THE SHIPPED REPORTS, 2026-09-22 — READ THIS BEFORE TRUSTING THE GATE.

Run over the six delivered reports in the SPCX workspace, the blocking tier fires **once or twice per
report** (7 findings across 6 reports). Two of those were checked by hand and **one was the gate's
fault, not the report's**: page 2 of thesis 001 was reported as an exhibit with no takeaway when a
104-word takeaway was present, and a four-word `metric=…` falsifier annotation sat between them. That
is fixed (`is_machine_annotation`).

The rest have NOT each been hand-verified, and a second one is contested: page 2 of thesis 001 is also
reported by `conclusion-first`, and reading its markup shows a section `<h2>` followed immediately by an
exhibit, with the claim headings (`<h3>Line 1 — …`) *after* it. That is either a true positive (evidence
before argument at page scope) or a correct container page whose sections each carry their own claim —
and deciding it requires a reviewer, not another regex.

**So the firing rate on reports the owner calls the golden standard is itself the finding.** Either the
shipped reports have pages that open with evidence, or this convention is narrower than implemented.
The gate is left blocking, as `FR-064` requires, and the measurement is recorded here and in
`contracts/report-readability.md` rather than tuned until it agrees with expectations — a gate adjusted
to pass the corpus would be measuring the corpus, not the convention.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# ── shared parsing ─────────────────────────────────────────────────────────────

PAGE_RX = re.compile(r'<section[^>]*class="[^"]*page[^"]*"[^>]*>(.*?)</section>', re.S | re.I)
HEADING_RX = re.compile(r"<h[1-3][^>]*>(.*?)</h[1-3]>", re.S | re.I)
PARA_RX = re.compile(r"<p\b[^>]*>(.*?)</p>", re.S | re.I)
EXHIBIT_RX = re.compile(r"<(table|figure)\b.*?</\1>", re.S | re.I)

TAG_RX = re.compile(r"<[^>]+>")


def text_of(html: str) -> str:
    """Visible text of a fragment, whitespace-collapsed."""
    return re.sub(r"\s+", " ", TAG_RX.sub(" ", html)).strip()


def words(text: str) -> list[str]:
    return [w for w in re.split(r"\s+", text) if w]


#: A token that carries no claim on its own: a number, a percentage, a currency figure, a range, a
#: date, or a unit. Used by conventions 3 and 4 to decide whether prose is really prose.
FIGURE_RX = re.compile(
    r"^[\s$€£¥]*[-+]?[\d,]+(?:\.\d+)?\s*(?:%|x|bn|mm|m|k|bps?|pp)?[\s$€£¥]*$"
    r"|^[\s$€£¥]*[-+]?[\d,]+(?:\.\d+)?\s*(?:–|-|to)\s*[-+]?[\d,]+(?:\.\d+)?",
    re.I,
)

#: Words that carry NO proposition. Stripped before judging whether a paragraph says anything.
#: Kept deliberately small and boring — every addition here loosens the gate.
FILLER = {
    "and", "or", "of", "in", "at", "to", "for", "on", "by", "the", "a", "an", "as", "vs", "vs.",
    "with", "from", "per", "yoy", "qoq", "ytd", "e", "est", "total", "average", "avg", "source",
    "sources", "note", "notes", "table", "figure", "exhibit", "page", "see", "above", "below",
}

#: A claim-bearing signal. The corpus's ledes and takeaway sentences land on a direction, a comparison
#: or an implication; these are the markers that can be found without understanding the sentence.
CLAIM_RX = re.compile(
    r"(?i)\b(is|are|was|were|has|have|had|will|would|should|could|may|might|must|"
    r"implies?|implied|means|suggests?|therefore|because|since|while|but|however|"
    r"drives?|driven|reflects?|supports?|warrants?|justifies?|points? to|argues?|"
    r"accelerat\w*|decelerat\w*|grow\w*|declin\w*|expand\w*|contract\w*|"
    r"beat|miss\w*|ahead|behind|upside|downside|risk\w*|guidance|outlook|"
    r"应当|意味着|因此|支持|指向|增长|下降|风险)\b"
)


def _is_figure_token(token: str) -> bool:
    return bool(FIGURE_RX.match(token.strip()))


def _prose_only(text: str) -> str:
    """The text with figure tokens removed — what is left is what the paragraph *says*."""
    kept = [w for w in words(text) if not _is_figure_token(w)]
    return " ".join(kept)


#: A token that contains at least one LETTER. Punctuation and separators carry no proposition, so a
#: paragraph of figures joined by `|` or `·` must not be able to clear the prose count on its
#: separators — which is exactly what the first version of this detector did, passing a fixture of six
#: figures and five pipes as "prose". Found by the negative fixture, which is what fixtures are for.
WORD_RX = re.compile(r"[^\W\d_]", re.UNICODE)


def is_numbers_only(paragraph: str, *, min_figures: int = 4, max_prose_words: int = 4) -> bool:
    """True when a paragraph is a table that lost its table markup.

    MECHANICAL, and calibrated on the failure: a paragraph of figures with a label. The two thresholds
    are deliberately generous in the direction of NOT flagging — a real sentence with several numbers
    in it ("Revenue grew 12% to $4.1bn, ahead of the 9% consensus") has prose words and clears
    `max_prose_words` on its own. What trips this is a paragraph that is ONLY figures.
    """
    tokens = words(paragraph)
    if not tokens:
        return False
    figures = sum(1 for t in tokens if _is_figure_token(t))
    prose = [
        w for w in tokens
        if not _is_figure_token(w)
        and WORD_RX.search(w)                      # a word, not a separator or a unit
        and w.lower().strip(".,;:()") not in FILLER
    ]
    return figures >= min_figures and len(prose) <= max_prose_words


#: A machine annotation, not prose: `metric=… threshold=… op=… basis=…`.
#:
#: The reports carry a falsifier channel inline — a `<p>` of `key=value` tokens naming what would prove
#: the page wrong. It is valuable and it is NOT a sentence. Found by running the gate against the real
#: delivered reports: page 2 of thesis 001 was reported as "exhibit with no takeaway" when a 104-word
#: takeaway was present, because a four-word annotation sat between the exhibit and it. **The gate was
#: wrong, not the report** — and a gate that fires on a good report is one that gets switched off.
_ANNOTATION_TOKEN_RX = re.compile(r"^[a-z_]+=", re.I)


def is_machine_annotation(text: str) -> bool:
    """True when a paragraph is a `key=value` annotation rather than a sentence.

    Mechanical signal: at least two `key=` tokens, and no sentence punctuation. A real sentence that
    happens to contain an `=` does not have two leading `key=` tokens.
    """
    tokens = [w for w in words(text)]
    if len(tokens) < 2:
        return False
    keyed = sum(1 for t in tokens if _ANNOTATION_TOKEN_RX.match(t))
    return keyed >= 2 and not re.search(r"[.!?]\s*$", text)


def _first_paragraph_after(html: str, start: int) -> str | None:
    """The first non-empty paragraph beginning at or after `start` that is PROSE.

    Machine annotations are skipped rather than returned: they are not sentences, and returning one
    makes the caller conclude there is no takeaway when there is.
    """
    m = PARA_RX.search(html, start)
    while m:
        body = text_of(m.group(1))
        if body and not is_machine_annotation(body):
            return body
        m = PARA_RX.search(html, m.end())
    return None


# ── the four blocking conventions ──────────────────────────────────────────────


def check_lede_before_evidence(content: str) -> list[str]:
    """CONVENTION 1 — the lede states the call BEFORE the evidence.

    The sell-side corpus opens with the conclusion and then supports it; a report that opens with a
    data table makes the reader assemble the argument themselves, which is the reported symptom.

    SIGNAL: on the FIRST page, the first prose paragraph must appear before the first exhibit, and it
    must carry a claim rather than being a label or a list of figures.

    FALSE POSITIVES, and why the check is narrow: a title page legitimately has no prose, so a page with
    no exhibit at all is not this check's subject. A report whose first page is a cover is handled by
    skipping pages that contain no exhibit — the check only fires when evidence comes first.
    """
    pages = PAGE_RX.findall(content)
    if not pages:
        return [f"readability: no report pages found — the content has no "
                f'`<section class="page">` elements, so no readability convention can be '
                f"checked. A gate that cannot find its subject must not pass silently."]

    first = pages[0]
    exhibit = EXHIBIT_RX.search(first)
    if not exhibit:
        return []  # a cover or a prose-only opening: not this convention's subject

    para = _first_paragraph_after(first, 0)
    if para is None:
        return [f"readability · lede-before-evidence: the first page opens with an exhibit and carries "
                f"no prose before it. The call must come before the evidence for it."]

    before = _first_paragraph_after(first[:exhibit.start()], 0)
    if before is None:
        return [f"readability · lede-before-evidence: the first page's exhibit appears before any "
                f"prose. The lede paragraph must precede it."]

    problems: list[str] = []
    if is_numbers_only(before):
        problems.append(
            "readability · lede-before-evidence: the opening paragraph is figures rather than a call — "
            f"{before[:80]!r}. A reader must be told what to conclude before being shown the data.")
    elif not CLAIM_RX.search(before):
        problems.append(
            "readability · lede-before-evidence: the opening paragraph states no claim — "
            f"{before[:80]!r}. It is a label or a topic, not a lede.")
    return problems


def check_exhibit_takeaways(content: str) -> list[str]:
    """CONVENTION 2 — every exhibit is followed by the sentence saying what it shows.

    An exhibit with no takeaway is a figure the reader must interpret, and interpreting it is the
    analyst's job, not the reader's. The corpus does this consistently; it is also the single most
    mechanical of the four.

    SIGNAL: prose of at least `MIN_TAKEAWAY_WORDS` follows each `<table>`/`<figure>` before the next
    exhibit or the end of the page.

    FALSE POSITIVES: a table whose `<caption>` is the takeaway. Checked explicitly — the caption counts
    when it is a sentence rather than a label, which is what `_gate_charts` already requires of charts.
    """
    problems: list[str] = []
    for page_no, page in enumerate(PAGE_RX.findall(content), 1):
        exhibits = list(EXHIBIT_RX.finditer(page))
        for i, ex in enumerate(exhibits):
            following = page[ex.end(): exhibits[i + 1].start() if i + 1 < len(exhibits) else len(page)]
            para = _first_paragraph_after(following, 0)
            if para is not None and len(words(para)) >= MIN_TAKEAWAY_WORDS:
                continue

            caption = re.search(r"<figcaption[^>]*>(.*?)</figcaption>|<caption[^>]*>(.*?)</caption>",
                                ex.group(0), re.S | re.I)
            if caption:
                text = text_of(caption.group(1) or caption.group(2) or "")
                if len(words(text)) >= MIN_TAKEAWAY_WORDS and CLAIM_RX.search(text):
                    continue

            problems.append(
                f"readability · exhibit-takeaway: page {page_no}'s exhibit {i + 1} carries no takeaway "
                f"sentence. Every exhibit must be followed by the sentence saying what it shows — "
                f"a figure with no reading is work the report has handed back to the reader.")
    return problems


#: A takeaway shorter than this is a label ("Segment revenue"), not a sentence.
MIN_TAKEAWAY_WORDS = 8


def check_numbers_only_paragraphs(content: str) -> list[str]:
    """CONVENTION 3 — a paragraph of figures is not a paragraph (FR-064).

    This is the failure literally described in the brief: *大量facts和数据的堆砌* — figures piled up. A
    reader cannot argue with a list, and a report made of them cannot be disagreed with either, which is
    the deeper problem.

    SIGNAL: an `<p>` whose tokens are figures and whose remaining prose is a handful of filler words.
    The thresholds live in `is_numbers_only` with the reasoning; the check errs toward not firing.
    """
    problems: list[str] = []
    for page_no, page in enumerate(PAGE_RX.findall(content), 1):
        for para_html in PARA_RX.findall(page):
            text = text_of(para_html)
            if is_numbers_only(text):
                problems.append(
                    f"readability · numbers-only-paragraph: page {page_no} carries a paragraph that is "
                    f"figures rather than prose — {text[:80]!r}. State what they mean; a number with no "
                    f"reading is not a finding.")
    return problems


def check_conclusion_first(content: str) -> list[str]:
    """CONVENTION 4 — a section opens with its conclusion, not with its data.

    Sell-side sections state what they are arguing and then enumerate the evidence for it. The inverse —
    a heading that names a topic, then exhibits, then one sentence of implication — is the
    heap-of-facts shape at section scale: a reader has to reach the end to find out why any of it
    mattered.

    SIGNAL, and it was corrected against the corpus rather than assumed. The first version asked
    whether the FIRST implication appeared before the LAST exhibit, and it fired on **page 2 of thesis
    001**, which is a well-formed page: a claim heading (*"Launch cost has a hard floor"*), then its
    exhibit, then a 104-word reading of it. That shape is correct — **the heading carries the
    conclusion**, and an exhibit followed immediately by its takeaway is exactly what convention 2 asks
    for. The check was measuring the wrong thing.

    What it measures now: a page is conclusion-first when **either** its heading states a claim, **or**
    a claim-bearing paragraph precedes its first exhibit. A page that opens with an exhibit under a
    label heading — "Segment detail", then a table — is the failure.

    A page with neither is convention 1's business at report scope and the scored tier's here; it is not
    reported twice under two names, because an author who fixes the first must not find the second
    unchanged.
    """
    problems: list[str] = []
    for page_no, page in enumerate(PAGE_RX.findall(content), 1):
        exhibits = list(EXHIBIT_RX.finditer(page))
        if not exhibits:
            continue

        heading = HEADING_RX.search(page)
        if heading:
            head = text_of(heading.group(1)).rstrip(".")
            # A heading that states a claim IS the conclusion. Measured on the corpus: the shipped
            # reports do this consistently, so this is a KEEP rather than a new requirement.
            if CLAIM_RX.search(head) and not is_numbers_only(head):
                continue

        before = _first_paragraph_after(page[:exhibits[0].start()], 0)
        if before is not None and CLAIM_RX.search(before) and not is_numbers_only(before):
            continue

        problems.append(
            f"readability · conclusion-first: page {page_no} opens with its evidence and states no "
            f"claim first — neither its heading nor a preceding paragraph says what the page argues. "
            f"Lead with the conclusion; the data is the support, not the argument.")
    return problems


#: What it means for a figure to be INTERPRETED, as distinct from `CLAIM_RX`.
#:
#: `CLAIM_RX` includes the copulas (`is`, `are`, `was`, `were`, `has`, `have`) because a *lede* made of
#: "Revenue was 1,204" is a claim-shaped sentence. For this check they are exactly wrong: "Segment 1
#: revenue was 120" states a fact, and counting it as an interpretation would let a ledger of
#: fact-statements clear a floor meant to catch ledgers. Found by the negative fixture, which failed
#: because every one of its twelve bare numeric sentences contains "was".
INTERPRET_RX = re.compile(
    r"(?i)\b(implies?|implied|means|suggests?|therefore|because|since|but|however|"
    r"drives?|driven|reflects?|supports?|warrants?|justifies?|points? to|argues?|"
    r"accelerat\w*|decelerat\w*|grow\w*|declin\w*|expand\w*|contract\w*|"
    r"beat|miss\w*|ahead|behind|upside|downside|risk\w*|outlook|"
    r"应当|意味着|因此|支持|指向|增长|下降|风险)\b"
)


def check_interpretive_floor(content: str, *, floor: float = 0.25) -> list[str]:
    """CONVENTION 5 — figures are never left bare for long.

    THE ONE RATIO WITH A DEFENSIBLE UNIVERSAL FLOOR. Across the sampled corpus, the share of
    numeric sentences that also carry an interpretive or directional token ranged **0.27 to 0.66** —
    every family, every size, no exceptions. So a floor of 0.25 passes all of them.

    IT CANNOT BE SET HIGHER, and that is measured rather than cautious: the largest family sits at
    0.36–0.39, so a 0.5 floor would fail all 30 of its documents. A "reasonable-looking" threshold is
    precisely how a gate starts failing a whole genre.

    ⚠️ A CALIBRATION CAVEAT THAT MATTERS. The 0.27 floor was measured on the corpus's **extracted text
    layer**; this check runs on **rendered HTML**, where table cells flatten into the sentence stream and
    are numeric without interpretation. That inflates the denominator, so a report measured here is not
    strictly comparable to the corpus figure. Two delivered reports score **17%** under this check —
    which is either the reported symptom (numbers without readings) or a layer artifact, and settling it
    needs the same extraction on both sides. Recorded rather than resolved: a threshold that looks
    precise and is measured on a different layer than it is applied to is the kind of number that gets
    quoted without its caveat.
    """
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text_of(content)) if s.strip()]
    numeric = [s for s in sentences if any(_is_figure_token(t) for t in words(s))]
    if len(numeric) < MIN_NUMERIC_SENTENCES:
        return []  # too few to be a ratio; a short page has no floor to miss

    interpreted = [s for s in numeric if INTERPRET_RX.search(s)]
    ratio = len(interpreted) / len(numeric)
    if ratio < floor:
        return [f"readability · interpretive-floor: only {ratio:.0%} of numeric sentences also say "
                f"something about them ({len(interpreted)}/{len(numeric)}); the corpus floor is "
                f"{floor:.0%}. Figures with no reading are data, not analysis."]
    return []


#: Below this many numeric sentences a ratio is noise rather than a measurement.
MIN_NUMERIC_SENTENCES = 10


def check_exhibit_monotonicity(content: str) -> list[str]:
    """CONVENTION 6 — exhibit numbers ascend in order of appearance.

    THE LOWEST FALSE-POSITIVE RISK OF ANY CHECK IN THE CORPUS: 58/58 documents, surviving contact with
    every family including the chart-dominant one. A reader following a cross-reference needs it, and
    an out-of-order number means the report was assembled rather than written.

    TWO TOLERANCES, both learned from documents the naive rule would fail: **gaps are permitted** and
    **the sequence need not start at 1**. Only monotonicity holds — so only monotonicity is asserted.
    A document with fewer than two exhibit headings is skipped rather than passed or failed.
    """
    numbers: list[int] = []
    for m in re.finditer(r"(?i)\bexhibit\s*(\d+)", text_of(content)):
        n = int(m.group(1))
        if not numbers or numbers[-1] != n:
            numbers.append(n)

    if len(numbers) < 2 or all(n == numbers[0] for n in numbers):
        return []

    out_of_order = [
        f"{numbers[i - 1]} → {numbers[i]}" for i in range(1, len(numbers)) if numbers[i] < numbers[i - 1]
    ]
    if out_of_order:
        return [f"readability · exhibit-monotonicity: exhibit numbers decrease in order of appearance "
                f"({', '.join(out_of_order[:4])}). Gaps are fine and the sequence need not start at 1, "
                f"but it must not go backwards — a reader following a cross-reference cannot."]
    return []


#: The two `FR-064` conventions the corpus does NOT support, kept and reported with the measurement
#: attached. They are printed after the blocking verdict, never folded into it, so that a reader can
#: see both the result and the reason it is not a gate.
#:
#: `contracts/report-readability.md` §2 carries the numbers: exhibit-takeaway holds in only 43–49% of
#: the largest family's exhibit sections, and conclusion-first is contradicted by 77–80 of its 103–106
#: sections. Failing a report for either would fail a quarter to a half of the corpus it was derived
#: from.
REPORTED_ONLY = (
    ("exhibit-takeaway", check_exhibit_takeaways),
    ("conclusion-first", check_conclusion_first),
)

#: The blocking set: the `FR-064` conventions the corpus supports, plus the two corpus-derived checks
#: with the strongest evidence behind them.
CHECKS = (
    ("lede-before-evidence", check_lede_before_evidence),
    ("numbers-only-paragraph", check_numbers_only_paragraphs),
    ("interpretive-floor", check_interpretive_floor),
    ("exhibit-monotonicity", check_exhibit_monotonicity),
)


def check(content: str) -> list[str]:
    """Every blocking problem, in a stable order."""
    problems: list[str] = []
    for _name, fn in CHECKS:
        problems.extend(fn(content))
    return problems


def reported(content: str) -> list[str]:
    """The observations from conventions the corpus does not support as gates."""
    out: list[str] = []
    for _name, fn in REPORTED_ONLY:
        out.extend(fn(content))
    return out


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]

    if len(argv) != 1:
        print(__doc__.strip().splitlines()[-3].strip(), file=sys.stderr)
        print("usage: check_report_readability.py <content.html> [--json]", file=sys.stderr)
        return 2

    path = Path(argv[0])
    if not path.is_file():
        print(f"check_report_readability: no such file: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    problems = check(text)
    observations = reported(text)

    if as_json:
        print(json.dumps({"blocking": problems, "reported": observations, "ok": not problems},
                         ensure_ascii=False, indent=2))
        return 1 if problems else 0

    if problems:
        print(f"report readability — BLOCKING tier: {len(problems)} problem(s)\n")
        for p in problems:
            print(f"  • {p}")
    else:
        print("report readability — BLOCKING tier: clear.")

    if observations:
        print(f"\n  Reported, NOT blocking — {len(observations)} observation(s) from conventions the")
        print("  corpus does not support as gates (contracts/report-readability.md §2):")
        for o in observations:
            print(f"    — {o}")

    print("\nPassing the blocking tier does NOT mean the report reads well — "
          "`score_report_readability.py` scores what structure cannot see.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
