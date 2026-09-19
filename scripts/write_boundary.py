#!/usr/bin/env python3
"""write_boundary.py — the single write boundary (spec 046 T172, Q147).

WHY THIS EXISTS, in one measurement. Q124, Q127 and Q142 each name a location
where their gate must run, and each names the same one: **the artifact write
boundary**. Measured before this file existed:

    named location     "the write boundary"
    implementations     4  (synthesize_report.py, reduce_journals.py,
                            thesis_status.py, portfolio_aggregate.py — each with
                            its own private `_atomic_write`)
    gate families       0 of 3 attached to any of them

So a gate attached to one of four writers would have been **worse than no gate**,
because it would read as enforced. Q147's finding is the shape of this file's
whole reason for being: the location was named, and did not exist as a thing.

This is a CONSOLIDATION, not an attachment. The four writers keep their logic and
call `write()`; what they lose is their private write path. `_atomic_write` was
defined **four times** — the same function, four copies — and every copy was a
place a gate could be bypassed by not existing there.

WHAT RUNS HERE, in order, before anything touches the disk:

    1. credential scan       Q124  — deterministic shape scan; hit BLOCKS the write
    2. second-writer refusal Q127/Q138 — `writer:` in the doc's own frontmatter
    3. mode-independent gates Q142/T175 — the six that hold in BOTH modes

WHAT DOES NOT RUN HERE: the thesis-only gates (FR-090 frontmatter, boundary
gates, promotion, converge/challenge, `_portfolio` aggregation). Those need a
thesis and belong to `dispatch_preflight` / `converge`. Q142 splits the inventory
and `workflow.yml`'s `machine_gates:` carries the split with each gate's `reads:`.

The boundary reports what it examined and what it could not — Q105 applied to the
boundary itself. A `write()` that returned success while checking nothing would
be the same defect this file was built to fix.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ── 1. credential shapes (Q124) ─────────────────────────────────────────────
#
# SHAPE, not provenance. Q124's argument for that is explicit: the observed leak
# came from an unquoted shell expansion whose *intent* was to print `SET`/`NOT
# SET` — so "fix the source" cannot work, because the source looks harmless. A
# shape scan catches the next leak from a different mechanism (a tool-call log, a
# pasted stack trace, a URL in an error message) without knowing the mechanism.
_CREDENTIAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("anthropic-key",     re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai-key",        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github-token",      re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("github-pat",        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("aws-access-key",    re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-api-key",    re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("slack-token",       re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("bearer-token",      re.compile(r"\bBearer\s+[A-Za-z0-9\-_.]{20,}")),
    # The generic assignment. Deliberately requires a VALUE of >=16 chars, so
    # documentation like `FMP_API_KEY=` and `export FMP_API_KEY` (no value) — and
    # this repo's own `contracts/data-tool-preflight.md` — do not trip it.
    #
    # NO leading `\b` before the keyword. The first version had one, and a `\b`
    # cannot fall between `_` and `A` in `FMP_API_KEY` because both are word
    # characters — so the pattern silently missed EVERY prefix-qualified env var,
    # which is the shape real credentials actually take here (`FMP_API_KEY`,
    # `FRED_API_KEY`, `FINNHUB_API_KEY`). Caught by the test for that case.
    ("assigned-secret",   re.compile(
        r"""(?ix) \b [A-Za-z0-9]* [_-]?
                  (api[_-]?key | secret[_-]?key | access[_-]?token | auth[_-]?token
                    | password | passwd | client[_-]?secret) \b
             \s* [:=] \s* ["']? ([A-Za-z0-9+/_\-]{16,}) """)),
]

# A value already redacted by a human or a prior scan is not a leak.
_REDACTED = re.compile(r"(?i)(\*{3,}|<redacted>|\[redacted\]|REDACTED|xxx{3,}|\.\.\.)")

# Nor is a PLACEHOLDER. Measured against this repo (1,243 text files): the scan
# found 12 hits, of which **4 were documentation placeholders** —
# `AGENTII_API_KEY=sk_live_YOUR_KEY_HERE` in QUICKSTART.md, README.md and
# docs/install/global-mcp-setup.md, and `sk_live_BAD_KEY_FOR_GATE_TEST` in
# smoke-test.sh (a deliberately invalid key). Zero were real leaks.
#
# This matters because Q124's hit semantics are BLOCKING: without this, writing a
# README would be refused. A gate that fires on its own documentation gets
# disabled rather than fixed — the same failure mode the number-form gate is
# scoped narrowly to avoid. The words are deliberately specific; a real key does
# not contain `YOUR_KEY` or `REPLACE_ME`.
_PLACEHOLDER = re.compile(
    r"(?i)(YOUR[_-]?[A-Z]*[_-]?(KEY|TOKEN|SECRET)|REPLACE[_-]?ME|CHANGE[_-]?ME|"
    r"PLACEHOLDER|EXAMPLE[_-]?KEY|DUMMY|FAKE[_-]?KEY|BAD[_-]?KEY|"
    r"TEST[_-]?KEY|SAMPLE[_-]?KEY|INSERT[_-]?|REDACT|<[A-Z_]{4,}>|TODO)")


def scan_credentials(text: str) -> list[tuple[str, int, str]]:
    """Return [(kind, line_no, masked_excerpt)] for every credential SHAPE found.

    The excerpt is masked: this function is called on the content of a leak, and
    echoing the secret into a report or a log would reproduce the exact harm Q124
    exists to stop. Only the shape and first/last two characters survive."""
    hits: list[tuple[str, int, str]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if _REDACTED.search(line) or _PLACEHOLDER.search(line):
            continue
        for kind, rx in _CREDENTIAL_PATTERNS:
            m = rx.search(line)
            if not m:
                continue
            raw = m.group(m.lastindex) if m.lastindex else m.group(0)
            masked = (raw[:2] + "*" * max(0, len(raw) - 4) + raw[-2:]
                      if len(raw) > 6 else "*" * len(raw))
            hits.append((kind, line_no, masked))
            break                      # one finding per line is enough to block
    return hits


# ── 2. second-writer refusal (Q127 / Q138) ──────────────────────────────────

_FRONTMATTER_RX = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
_WRITER_RX = re.compile(r"^writer\s*:\s*(.+?)\s*$", re.M)


def declared_writer(text: str) -> str | None:
    """Q138: `writer: <role>` lives in the document's OWN frontmatter.

    Q138 chose that location over a workspace-level registry for the reason that
    makes the refusal decidable: at the moment of the second write, the ONLY
    thing you can read is the document. A registry would be a ledger of document
    state — which Q4 rejected five times, and which would drift from the
    documents it describes (Q120's class).

    **Two carriers, one field.** A markdown document declares its writer in `---`
    frontmatter; a JSON document cannot contain that delimiter at all, so it
    declares the same thing as a top-level `"writer"` key. Reading only the
    frontmatter form meant a JSON file declared nothing, and "declares nothing"
    means append-only — so a JSON writer's own SECOND write was refused as
    `refuse-append-only`, silently, because the caller discarded the Result. That
    is the same defect as the markdown case, one format over, and it is why the
    split into a JSON reduce file could not work until this function learned it.

    Returns None when the key is absent **in either form**. **Absent means
    append-only**, which is Q127's fail-safe: "undeclared" must never silently
    mean "anyone may overwrite" — that is Q105's family again, silence read as
    permission, and its observed consequence was a document two sessions
    interleaved."""
    m = _FRONTMATTER_RX.match(text)
    if m:
        w = _WRITER_RX.search(m.group(1))
        return w.group(1).strip().strip("'\"") if w else None
    # JSON does not permit a `---` frontmatter block, so the field lives at the top
    # level. Guarded on the first character as well as the parse, so a large
    # markdown file is never handed to json.loads — the parse is the expensive half
    # and the cheap test is exact.
    if text.lstrip()[:1] == "{":
        try:
            doc = json.loads(text)
        except (ValueError, TypeError):
            return None
        w = doc.get("writer") if isinstance(doc, dict) else None
        return w.strip() if isinstance(w, str) and w.strip() else None
    return None


def second_writer_verdict(path: Path, new_text: str, writer: str | None) -> tuple[str, str]:
    """(verdict, why) where verdict ∈ {allow, refuse-append-only, refuse-second-writer}."""
    if not path.exists():
        return "allow", "new file — no existing writer to conflict with"
    try:
        old_text = path.read_text(encoding="utf-8")
    except OSError as e:
        return "allow", f"unreadable ({e.__class__.__name__}) — treated as new"
    old_writer = declared_writer(old_text)
    if old_writer is None:
        return ("allow", "no `writer:` declared — append-only, so an append is allowed"
                ) if _is_append(old_text, new_text) else (
                "refuse-append-only",
                "document declares no `writer:` ⇒ APPEND-ONLY (Q127's fail-safe), and "
                "this write is not an append — it removes or rewrites existing content")
    if writer is not None and writer != old_writer:
        return ("refuse-second-writer",
                f"document declares `writer: {old_writer}`; this write comes from "
                f"`{writer}` — refused, NOT merged (Q127). Interleaved output is "
                f"neither writer's intent; the observed case grew a plan document 2.2×")
    return "allow", f"`writer: {old_writer}` — same writer"


def _is_append(old: str, new: str) -> bool:
    """An append keeps every existing line, in order, and adds after them."""
    return bool(old.strip()) and new.startswith(old.rstrip("\n"))


# ── 3. the mode-independent gates (Q142 / T175) ─────────────────────────────
#
# The six that hold in BOTH modes. Q142's reason for the split is that a
# single-skill artifact and a thesis artifact are the SAME KIND of thing — both
# are claims about agentii.ai data. A gate that reads `tasks.md` cannot cross;
# these six can.
#
# Each is deterministic, zero-LLM. Q146 is the reason `claim_class` is a FIELD
# rather than a text scan: making a determinism gate parse prose injects
# non-determinism into the gate whose purpose is determinism.

_CITATION_RX = re.compile(r"\[\[?|agentii\.ai/v/|citation_id|\[\d+\]|`sec\d+`")


@dataclass
class Check:
    gate: str
    problems: list[str] = field(default_factory=list)
    examined: int = 0
    # Whether this gate's problems STOP the write. A gate can find a real problem
    # and still not refuse — resolved per gate rather than by a global name list,
    # because the first version used a global set and it blocked every report.
    blocking: bool = False


def _gate_citation_density(text: str, min_per_200: int = 1) -> Check:
    """Q142/contracts/citation-and-memory.md: >=1 citation per 200 words."""
    c = Check("citation-density")
    words = len(re.findall(r"\S+", text))
    cites = len(_CITATION_RX.findall(text))
    c.examined = words
    if words >= 200:
        need = max(1, (words // 200) * min_per_200)
        if cites < need:
            c.problems.append(f"{cites} citation(s) for {words} words; need >= {need}")
    return c


def _gate_number_form(text: str) -> Check:
    """Q102: rates and ratios as decimals, not percentages-with-a-sign.

    Deterministic and narrow. It flags a rate expressed with a trailing `%` in a
    key_metrics binding, not every `%` in prose — a gate that fires on prose is
    a gate that gets disabled."""
    c = Check("number-canonical-form")
    for m in re.finditer(r"^\s*(\w*(?:rate|ratio|growth|margin|yield)\w*)\s*[:=]\s*([^\n#]+)$",
                         text, re.I | re.M):
        val = m.group(2).strip()
        c.examined += 1
        if "%" in val:
            c.problems.append(
                f"`{m.group(1)}` is a rate expressed as `{val}` — Q102 requires the "
                f"canonical form (a decimal), with the percentage as presentation")
    return c


def _gate_vacuous(text: str) -> Check:
    """Q105: a declared mechanism that examined nothing must SAY so.

    Scans for the shape this session found eight times: a gate/check section that
    reports a clean result with no stated count of what it examined."""
    c = Check("vacuous-reporting")
    for m in re.finditer(r"(?im)^\s*(?:[-*]\s*)?(G1|G2|gate|check|preflight)\b[^\n]{0,120}"
                         r"(?:pass(?:ed)?|clean|OK|✓)\b[^\n]{0,60}$", text):
        line = m.group(0)
        c.examined += 1
        if not re.search(r"\d", line):
            c.problems.append(
                f"a gate reports a clean result with no count of what it examined: "
                f"`{line.strip()[:70]}` — Q105")
    return c


def _gate_prose_safety(text: str) -> Check:
    """Q109/prose-safety: no unframed reference to a source the artifact cannot cite."""
    c = Check("prose-safety")
    c.examined = len(text)
    for m in re.finditer(r"(?i)\b(?:according to|sources say|it is (?:widely )?reported|"
                         r"reportedly|analysts (?:say|expect))\b", text):
        c.problems.append(f"unframed attribution at offset {m.start()}: "
                          f"`{text[m.start():m.start()+60].strip()}`")
    return c


def _gate_evidence_class(text: str) -> Check:
    """Q84: refuse when ALL support is analogy / similarity-retrieval / KOL.

    Reads the `support:` field when present (Q146's field-not-scan principle).
    When the field is absent it reports that it could not run — rather than
    guessing from prose."""
    c = Check("evidence-class")
    m = re.search(r"^support\s*:\s*(.+?)\s*$", text, re.M)
    if not m:
        c.problems.append(
            "NO `support:` field — this gate cannot determine the evidence class. "
            "Q84 refuses promotion when all support is analogy / similarity-retrieval "
            "/ KOL, and Q146 requires that determination be a FIELD, not a text scan.")
        return c
    c.examined = 1
    if m.group(1).strip().lower() in ("analogical", "analogy", "kol"):
        c.problems.append(f"`support: {m.group(1).strip()}` — analogy/KOL-only support "
                          f"cannot be promoted (Q84)")
    return c


# ── the artifact citation gate (Q102 / T124) ────────────────────────────────
#
# Q102's requirement, stated exactly: *"要求**不是"更多引用"，而是"可跟随的引用"**"*
# — not more citations, FOLLOWABLE ones. The measured state it was written from:
# `theses/001-technology-baseline/artifacts/` held **44 artifacts, 0 occurrences
# of `agentii.ai/v/`, 0 files containing `agentii.ai`** — they carried bare
# accession text. Those artifacts are *honest and unfollowable*, and a report
# whose citations a reader cannot open is, for usability, the same as a report
# with none.
#
# Q102 also settled WHERE: at the artifact boundary, "earliest boundary where the
# information exists" — the sourcing skill is the only party that knows the
# `citation_id`. Downstream, the fix is re-doing 44 artifacts.

# A followable viewer link: https://agentii.ai/v/{ticker}/{citation_id}/{page}
_VIEWER_RX = re.compile(r"https?://agentii\.ai/v/[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/\d+")
# A bare SEC accession, e.g. 0001819994-26-000062. Honest, and not followable.
_ACCESSION_RX = re.compile(r"\b\d{10}-\d{2}-\d{6}\b")
# Any citation-ish marker at all, so "none" and "unfollowable" stay distinct.
_ANY_CITE_RX = re.compile(r"agentii\.ai|accession|\[\[|\[\d+\]|`sec\d+`", re.I)


def _gate_citation_form(text: str) -> Check:
    """Q102: bare accessions fail; the resolvable form is required.

    Deliberately distinguishes three states, because they need three different
    fixes and Q102's whole point is that a single error message cannot serve
    them: no citations at all (a writing problem), citations present but
    unfollowable (the measured 44-artifact case), and followable citations."""
    c = Check("citation-form")
    c.blocking = True          # Q102: an unfollowable artifact does not count as produced
    viewer = _VIEWER_RX.findall(text)
    bare = _ACCESSION_RX.findall(text)
    c.examined = len(viewer) + len(bare)
    if viewer:
        return c
    if bare:
        c.problems.append(
            f"{len(bare)} bare accession(s) and 0 followable `agentii.ai/v/` links. "
            f"The artifact is honest and UNFOLLOWABLE — a reader cannot open the "
            f"source. Q102 requires the resolvable form "
            f"`https://agentii.ai/v/{{ticker}}/{{citation_id}}/{{N}}`. Fix here, at "
            f"the boundary where the citation_id is known; fixing at the report "
            f"layer costs a redo of every artifact.")
    elif _ANY_CITE_RX.search(text):
        c.problems.append(
            "citation-like text present but no followable `agentii.ai/v/` link")
    else:
        c.problems.append(
            "0 citations of any form. Q102 is about followability, not density — "
            "but zero is the bright line, and this artifact cannot be traced to "
            "any source.")
    return c


# ── the evidence-image gate (Q96 / T126) ────────────────────────────────────
#
# T126 says "an image from a licence-restricted source is refused; unknown
# licence counts as restricted". Q96 says something narrower AND says why:
#
#   * step 4 (in scope): an image must trace to a citation that IS in the pack;
#     an image with no citation is refused.
#   * licence review (OUT of scope): Q96 places it in the VERTICAL (054's
#     `_quarantine/` pattern), "不在本 spec", and calls the provenance gate a
#     NECESSARY condition but not a sufficient one — explicitly because 046
#     cannot settle redistribution.
#
# So this implements the MECHANISM with T126's fail-safe and takes the POLICY as
# an argument. With no registry the gate REPORTS that it could not evaluate
# rather than passing — Q105, not a weakening.
_IMG_RX = re.compile(r"<img\b[^>]*>", re.I)
_IMG_SRC_RX = re.compile(r'src\s*=\s*["\']([^"\']+)["\']', re.I)
_IMG_SOURCE_RX = re.compile(r'data-source\s*=\s*["\']([^"\']+)["\']', re.I)
_PERMISSIVE = {"public-domain", "cc0", "cc-by", "cc-by-sa", "mit", "own-work"}


def _gate_image_licence(text: str, licences: dict[str, str] | None = None) -> Check:
    """Q96 step 4 + T126's fail-safe, scoped to images that CLAIM a source.

    The first version judged EVERY `<img>` and blocked on each — which blocked
    every report, because Q48's charts are inline base64 **SVG generated from
    `data-chart` tokens**, not images fetched from a source document. Caught by
    tests/test_s7_verification.py::test_chart_token_rendered, an existing test
    that renders a real report.

    Q96 introduced this gate for **source-document evidence images** — retrieved
    from a viewer page and embedded. Those are `data:image/{png,jpeg,webp}` and
    carry a provenance marker. A generated chart is `data:image/svg+xml`, has no
    source to license, and is not what Q96 is about. So:

      * a generated SVG               — not judged, and SAID so
      * a raster image with `data-source`  — full check, BLOCKING
      * a raster image without one         — reported, not blocking: Q96 step 4's
        "no citation ⇒ refuse" governs the retrieval pipeline, and refusing here
        would refuse every hand-drawn figure without adding provenance"""
    c = Check("image-licence")
    imgs = _IMG_RX.findall(text)
    c.examined = len(imgs)
    if not imgs:
        return c
    judged = 0
    for tag in imgs:
        m_src = _IMG_SRC_RX.search(tag)
        src = (m_src.group(1) if m_src else "").lower()
        if src.startswith("data:image/svg+xml"):
            continue                       # Q48 generated chart — no source to trace
        if not src.startswith("data:image/"):
            c.problems.append(
                f"image is not a base64 data URI (`{src[:50]}`) — Q46 requires a "
                f"single offline-printable file, so an external image is an "
                f"external dependency")
            c.blocking = True
            continue
        judged += 1
        m_srcid = _IMG_SOURCE_RX.search(tag)
        if not m_srcid:
            c.problems.append(
                "a raster image carries no `data-source`, so it cannot be traced "
                "to a citation — Q96 step 4 requires provenance for retrieved "
                "evidence images. Reported, not refused: an untraced figure is a "
                "finding, and refusing here would block every report over a "
                "hand-drawn figure without adding the provenance.")
            continue
        key = m_srcid.group(1)
        lic = (licences.get(key) or "").strip().lower() if licences else ""
        if licences is None:
            c.problems.append(
                f"image source `{key}` cannot be evaluated — no licence registry "
                f"supplied. Q96 places licence POLICY in the vertical and requires "
                f"the MECHANISM here; the caller must pass `licences=`.")
            continue
        if lic not in _PERMISSIVE:
            c.problems.append(
                f"image source `{key}` has licence {lic!r}, which is "
                f"{'UNKNOWN' if not lic else 'not permissive'} — T126: unknown "
                f"counts as restricted")
            c.blocking = True
    c.examined = judged
    return c


def run_mode_independent_gates(text: str, citable: bool = False,
                               licences: dict[str, str] | None = None) -> list[Check]:
    gates = [_gate_citation_density(text), _gate_number_form(text), _gate_vacuous(text),
             _gate_prose_safety(text), _gate_evidence_class(text),
             _gate_image_licence(text, licences)]
    if citable:
        gates.append(_gate_citation_form(text))
    return gates


# ── the boundary ────────────────────────────────────────────────────────────

@dataclass
class Result:
    path: Path
    verdict: str                      # written | blocked | refused
    reasons: list[str] = field(default_factory=list)
    examined: list[str] = field(default_factory=list)
    producer: str = ""

    def ok(self) -> bool:
        return self.verdict == "written"

    def describe(self) -> str:
        if self.ok():
            return (f"written {self.path.name} by {self.producer} "
                    f"(examined: {', '.join(self.examined)})")
        return (f"{self.verdict.upper()} {self.path} by {self.producer}: "
                + "; ".join(self.reasons))


# Gates that may block a write outright, versus those that report. Q124's
# credential hit is BLOCKING; the rest are advisory at this stage because their
# population is incomplete (measured: `support:` absent on the artifacts in both
# workspaces). Making them blocking today would refuse every real write, which is
# how a gate gets disabled rather than fixed.
# Q124's credential hit and Q127's second writer both stop the write outright.
# `citation-form` is blocking TOO, but only where it applies: Q102's completion
# semantics are explicit — "低于下限、或引用不可解析 → **不算已产出的工件**" —
# an unfollowable artifact does not count as produced, and the task re-dispatches
# (Q56). It is listed here and gated by `citable=`, because applying it to
# INDEX.md or a portfolio view would refuse every write those tools make.
# Names here force-block regardless of a gate's own `blocking` flag. Kept for
# the two structural refusals; citation-form blocks via the gate itself, and
# image-licence does too — putting it here as well made an unsourced raster
# image block a report, which is the class of over-blocking that turns a gate off.
BLOCKING_GATES = {"credential-scan", "second-writer"}


def write(path: Path, content: str, *, producer: str, writer: str | None = None,
          mode: str = "single-skill", kind: str = "markdown", citable: bool = False,
          licences: dict[str, str] | None = None, gate: bool = True) -> Result:
    """The one write path. Every persistent artifact in every mode goes through it.

    `producer` is REQUIRED and is recorded on a credential hit — Q124's "record the
    command that produced the content", which is what makes a leak traceable and a
    rotation targeted rather than blanket.

    `citable=True` asserts this is a **skill artifact** — the output of a sourcing
    skill — and turns on Q102's citation-form gate, which is BLOCKING. It defaults
    off because INDEX.md, portfolio views and thesis.md are not artifacts: Q102's
    line is "the sourcing skill is the only party that knows the `citation_id`",
    and refusing a portfolio view for lacking viewer links would disable a gate
    rather than enforce one.

    `kind` selects which gates can run. The credential scan runs on EVERY kind —
    Q124 names session records and journal shards as the highest-exposure surface,
    and those are not prose. The five prose gates run on `markdown`/`html` only:
    running a citation-density check over `thesis.reduce.json` would report
    `examined: 0` and pass, which is the vacuous success this file exists to stop.
    (`thesis.md` is prose and IS a markdown write; the reduce document is the JSON
    one, and it lives in its own file — see contracts/thesis.md.)"""
    path = Path(path)
    res = Result(path=path, verdict="written", producer=producer)

    if not gate:
        res.examined.append("NOTHING — gate=False bypasses all checks")
        _atomic_write(path, content)
        return res

    # 1. credential scan (Q124) — BLOCKING
    hits = scan_credentials(content)
    res.examined.append(f"credential-shapes ({len(_CREDENTIAL_PATTERNS)} patterns)")
    if hits:
        res.verdict = "blocked"
        for kind, line_no, masked in hits:
            res.reasons.append(
                f"{kind} at line {line_no} ({masked}) — BLOCKED. Producer: `{producer}`. "
                f"Rotate the credential, then re-run.")
        return res

    # 2. second-writer refusal (Q127/Q138)
    if writer is not None or path.exists():
        verdict, why = second_writer_verdict(path, content, writer)
        res.examined.append("second-writer (`writer:` frontmatter)")
        if verdict.startswith("refuse"):
            res.verdict = "refused"
            res.reasons.append(why)
            return res
        res.examined.append(f"second-writer: {why}")

    # 3. mode-independent gates (Q142/T175)
    if kind in ("markdown", "html"):
        for c in run_mode_independent_gates(content, citable=citable,
                                            licences=licences):
            res.examined.append(f"{c.gate} ({c.examined})")
            if c.problems:
                if c.blocking or c.gate in BLOCKING_GATES:
                    res.verdict = "blocked"
                res.reasons.extend(f"{c.gate}: {p}" for p in c.problems)
    else:
        res.examined.append(
            f"prose gates SKIPPED for kind={kind} — they cannot read this format, "
            f"and reporting `examined: 0` would be a vacuous success (Q105)")
    if kind in ("markdown", "html") and not citable:
        res.examined.append(
            "citation-form NOT RUN — `citable` is False, so this write is not "
            "asserted to be a skill artifact. Q102's gate applies to artifacts; "
            "applying it here would refuse every INDEX.md and portfolio view. "
            "Recorded so that a clean result is not read as a citation verdict.")

    if res.verdict == "blocked":
        return res
    _atomic_write(path, content)
    return res


def _atomic_write(path: Path, content: str) -> None:
    """One implementation, replacing the four that existed.

    Same-directory temp + os.replace: atomic on POSIX, and same-directory so it
    cannot cross a filesystem boundary (which would silently degrade to a copy)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="write_boundary.py",
                                 description="the single write boundary (T172)")
    ap.add_argument("--scan", metavar="FILE",
                    help="scan a file for credential shapes and exit 1 on a hit")
    ap.add_argument("--writer-of", metavar="FILE",
                    help="print the `writer:` a document declares (blank = append-only)")
    ap.add_argument("--self-test", action="store_true",
                    help="prove the boundary checks something")
    a = ap.parse_args(argv)

    if a.scan:
        hits = scan_credentials(Path(a.scan).read_text(encoding="utf-8"))
        for kind, line_no, masked in hits:
            print(f"{a.scan}:{line_no}: {kind} ({masked})")
        print(f"{len(hits)} credential shape(s)" if hits else "clean")
        return 1 if hits else 0
    if a.writer_of:
        w = declared_writer(Path(a.writer_of).read_text(encoding="utf-8"))
        print(w if w else "(none declared ⇒ append-only)")
        return 0
    if a.self_test:
        return _self_test()
    ap.print_help()
    return 2


def _self_test() -> int:
    """The boundary must prove it examines something (Q105)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.md"
        # a clean write passes and says what it examined
        r = write(p, "# t\n\n" + "word " * 60 + "[[cite]]\n", producer="self-test",
                  writer="self-test")
        assert r.ok(), r.describe()
        assert len(r.examined) >= 3, r.examined
        print("  clean write       : OK —", r.describe())
        # a credential blocks, and it does NOT touch the disk
        before = p.read_text()
        r = write(p, "# t\nkey = sk-ant-aaaaaaaaaaaaaaaaaaaaaaaa\n", producer="self-test",
                  writer="self-test")
        assert r.verdict == "blocked", r.describe()
        assert p.read_text() == before, "a blocked write must not modify the file"
        print("  credential        : BLOCKED —", r.reasons[0][:80])
        # a second writer is refused, not merged
        r = write(p, "# t\nsomebody else's content entirely\n", producer="other",
                  writer="other")
        assert r.verdict == "refused", r.describe()
        print("  second writer     : REFUSED —", r.reasons[0][:80])
    print("\nboundary self-test passed: it writes, it blocks, it refuses.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
