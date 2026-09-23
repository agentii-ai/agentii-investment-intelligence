#!/usr/bin/env python3
"""synthesize_report.py — thesis HTML synthesis (spec 046 Q49/Q50), v0.3.0.

The report CONTENT is authored by an LLM (skills/agentii/synthesize/SKILL.md);
this module is the deterministic scaffolding around that authorship:

  pack      — bundle every source markdown file verbatim into report-input.md
              (the LLM's sole input, plus header facts and the sources_hash)
              AND write report/metrics.json (per-ticker key_metrics/conclusions/
              counts, values verbatim — machine-ready numbers for KPI tiles
              and kpi_trend charts).
  assemble  — validate the LLM-authored report/content.html against hard gates
              (fragment-only, element whitelist, no <img>, citation anti-
              fabrication gate, chart-token contract), render chart tokens to
              base64 SVG (Q48), inject the page sequence + running sheet
              head/foot into the template, fill the cover + TOC, embed the Q50
              pins, run the Q47 overflow gate with the 3-tier font fallback,
              write thesis-report.html — or degrade to a markdown fallback +
              draft banner. Non-blocking quality advisories go to stderr.
  render    — the visual QA loop lives in render_report.py (Chrome headless →
              per-page PNGs); the LLM reads the renders and iterates.

Skills emit MARKDOWN only (Q49); ONE thesis-report.html per thesis is produced
here, at the synthesis step. Python never selects or renders narrative content
— that judgment is the LLM's (the pack is verbatim source material).
"""
from __future__ import annotations

import argparse
import hashlib
import html as _html
import html.parser
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_boundary  # noqa: E402 — the single write boundary (T172)
import check_page_overflow  # noqa: E402
import chart_render  # noqa: E402
import check_report_readability  # noqa: E402 — the corpus-derived bound (T089)

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates" / "thesis-report.html"


def _template_version() -> str:
    """`<semantic>+<content-hash>` — the version MOVES when the template does.

    Hand-maintained, it did not: the template changed by 23+/17- in one session
    while the constant stayed "0.3.0", so converge.py's
    `emb_tv != TEMPLATE_VERSION` was False for a report built from the OLD
    template — a template-staleness gate that could not fire. That is the
    Q101 defect one layer down, and the same reason landing-items.yaml and the
    spec header are derived rather than declared (Q113/Q134).

    The semantic half is kept for humans; the hash half is what enforces.

    CONSEQUENCE, deliberate and stated: reports generated before this change
    now compare unequal and converge will flag them stale. That is correct —
    they WERE built from an older template — but it does mean the first converge
    after this lands proposes a regeneration for every existing thesis report.
    """
    digest = hashlib.sha256(TEMPLATE.read_bytes()).hexdigest()[:7]
    return f"0.3.0+{digest}"


TEMPLATE_VERSION = _template_version()
PACK_VERSION = "2.0"

# Q50: all source markdown artifacts — artifacts, the cross-stock synthesis and
# the snapshot all feed the report, so all of them pin it (v0.1.0 hashed only
# artifacts/). Outputs (report-input.md, report/content.html, thesis-report.*)
# are deliberately excluded — a regenerated report must not self-stale.
#
# `report/assets/**/*` (added 2026-09-19) pins the FILING FIGURES a thesis fetches
# for itself. Without it a report could embed a raster that sources_hash did not
# cover — it would pin the prose it rests on while carrying a picture it does not,
# which is the exact asymmetry this programme spends its time removing. Non-
# breaking by construction: source_files() collects only what the globs MATCH, so
# for any thesis with no report/assets/ the file list is unchanged and the hash is
# bit-identical. Note pathlib needs the trailing `/*` — `report/assets/**` alone
# matches directories, never files, and would have pinned nothing while looking
# like it pinned something.
SOURCE_GLOBS = ["artifacts/**/*.md", "_cross/**/*.md", "snapshots/**/*.md",
                "report/assets/**/*"]

PAGES_COMMENT = ("<!-- PAGES — assembler injects the LLM-authored "
                 '<section class="page"> sequence -->')

# Q139: the disclaimer is a presentation-shaped output's legal tail. Its text is
# authored exactly once — in disclaimer.md — and read from that file here. This
# script never restates it, so the two renderings cannot drift apart.
DISCLAIMER_MD = TEMPLATE.parent / "disclaimer.md"
# Structural and case-insensitive: any [BRACKETED] token surviving substitution
# fails assembly. Same rule as Q108 — a placeholder that ships is a defect.
_UNFILLED_RE = re.compile(r"\[[A-Za-z][A-Za-z0-9_ -]{1,60}\]")


class ContentMissingError(Exception):
    """report/content.html absent — the LLM authorship step has not run."""


def source_files(thesis: Path) -> list[Path]:
    """All existing markdown sources, sorted — the Q50 sources_hash input."""
    files: list[Path] = []
    for glob in SOURCE_GLOBS:
        files.extend(p for p in sorted(thesis.glob(glob)) if p.is_file())
    return sorted(set(files))


def sources_hash(thesis: Path) -> str:
    """Aggregate hash over (relpath + content) of every source markdown file."""
    h = hashlib.sha256()
    for p in source_files(thesis):
        h.update(str(p.relative_to(thesis)).encode("utf-8"))
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def _frontmatter(text: str) -> dict:
    import g1_gate  # shared parser

    return g1_gate.parse_frontmatter(text)


def _newest_file(globs: list[str], thesis: Path) -> Path | None:
    hits = [p for g in globs for p in thesis.glob(g) if p.is_file()]
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


def _header_facts(thesis: Path) -> dict:
    """Lenient header facts for the cover + pack. Missing → placeholder, never crash."""
    facts = {"name": thesis.name, "claim": "", "pin": "", "as_of": "",
             "universe": [], "entry_count": None}
    spec_md = thesis / "spec.md"
    spec_text = spec_md.read_text(encoding="utf-8") if spec_md.is_file() else ""
    m = re.search(r"^# Research Thesis:\s*(.+)$", spec_text, re.MULTILINE) \
        or re.search(r"^#\s+(.+)$", spec_text, re.MULTILINE)
    if m:
        facts["name"] = m.group(1).strip()
    m = re.search(r"^\*\*Claim\*\*:\s*(.+)$", spec_text, re.MULTILINE)
    if m:
        facts["claim"] = m.group(1).strip()
    # Universe rows: the spec's ticker table (first cell a bare ticker, weight
    # cell carries a % — filters out the skill/deep/full matrix tables).
    for line in spec_text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if (len(cells) >= 4 and re.fullmatch(r"[A-Z]{1,5}", cells[0].strip("`"))
                and re.search(r"\d+(\.\d+)?\s*%", cells[3])):
            facts["universe"].append((cells[0], cells[3]))
    # Pin / as_of from the newest cross-stock synthesis.
    synth = _newest_file(["_cross/*_synthesis.md"], thesis)
    if synth:
        fm = _frontmatter(synth.read_text(encoding="utf-8"))
        facts["pin"] = str(fm.get("constitution_pin") or "")
        facts["as_of"] = str(fm.get("as_of") or "")
        if not facts["universe"]:
            facts["universe"] = [(t, "") for t in fm.get("tickers_covered") or []]
    # Entry count from the newest snapshot rollup.
    snap = _newest_file(["snapshots/**/*_thesis.md"], thesis)
    if snap:
        try:
            doc = json.loads(snap.read_text(encoding="utf-8"))
            facts["entry_count"] = (doc.get("mechanical") or {}).get("entry_count")
        except (ValueError, AttributeError):
            pass
    return facts


READABILITY_JSON = "report/readability.json"


def _readability(thesis: Path) -> dict:
    """The author's scored-tier record (058 FR-065, T091), read leniently like the header facts.

    NOT IN `SOURCE_GLOBS`, deliberately. The score is a judgement ABOUT the report, not a source of it:
    hashing it would make writing the score invalidate the sources hash that `pack` recorded, so an
    author recording their own score would flip the report's staleness bar. The one field that says how
    well the report reads must not be able to make the report look out of date.

    Keys: `score` (1–25, the rubric total), `previous` (the last release's, or null), `explanation`
    (required only when the score DROPPED — FR-065's consequence, and the reason the field is allowed
    to exist at all: `FR-040` forbids a field that records a condition without triggering anything).
    """
    f = thesis / READABILITY_JSON
    out = {"score": None, "previous": None, "explanation": "",
           "cover": "not scored (058 FR-065)", "problems": []}
    if not f.is_file():
        # Absent is a STATE, not an error: a thesis whose report predates this tier still assembles.
        # It is visible on the cover as "not scored" rather than as a number nobody earned — which is
        # the difference between an unfilled field and a claim.
        return out
    try:
        doc = json.loads(f.read_text(encoding="utf-8"))
    except ValueError as e:
        out["problems"].append(f"{READABILITY_JSON} is not valid JSON: {e}")
        return out
    if not isinstance(doc, dict):
        out["problems"].append(f"{READABILITY_JSON} must be a JSON object")
        return out

    score, previous = doc.get("score"), doc.get("previous")
    out["previous"] = previous
    out["explanation"] = str(doc.get("explanation") or "").strip()

    if score is None:
        # Absent is not an error: a thesis whose report predates this tier still assembles. It is
        # visible on the cover as "not scored" rather than as a number nobody earned.
        out["cover"] = "not scored (058 FR-065)"
        return out
    if not isinstance(score, int) or not 1 <= score <= 25:
        out["problems"].append(
            f"{READABILITY_JSON}: `score` must be an integer 1–25 (five rubric criteria, 1–5 each), "
            f"got {score!r}")
        return out

    out["score"] = score
    out["cover"] = f"{score}/25"
    # FR-065: a drop MUST be explained in the deliverable. The trigger is a REGRESSION, never an
    # absolute threshold — no score is refused for being low, and the first report sets its own
    # baseline. What is refused is a regression with no explanation, which is the one outcome that
    # would leave the score recorded without consequence.
    if isinstance(previous, int) and score < previous and not out["explanation"]:
        out["problems"].append(
            f"{READABILITY_JSON}: the readability score DROPPED from {previous} to {score} and no "
            f"`explanation` is recorded. FR-065: a drop below the previous release's MUST be explained "
            f"in the deliverable itself — add `explanation` (it is rendered on the cover beside the "
            f"score), or restore the previous standard. The score is not a gate and is never refused "
            f"for being low; an unexplained regression is what is refused.")
    return out


def _truncate_artifact(body: str, limit: int, path: Path) -> str:
    """Cut an artifact body at a paragraph boundary, with an explicit marker."""
    cut = body[:limit]
    if "\n\n" in cut:
        cut = cut.rsplit("\n\n", 1)[0]
    return cut.rstrip() + f"\n\n[... truncated at {limit} chars — read {path} directly]"


def pack_text(thesis: Path, body_limit: int | None = None) -> str:
    """The LLM's deterministic input bundle — every source verbatim, no timestamps."""
    facts = _header_facts(thesis)
    shash = sources_hash(thesis)
    universe = " ; ".join(f"{t} {w}".strip() for t, w in facts["universe"]) or "(none)"
    lines = [
        f"# Report Input — {facts['name']}",
        "",
        f"<!-- pack_version: {PACK_VERSION} · sources_hash: {shash} "
        "· deterministic — no timestamps -->",
        "",
        "## Header facts",
        f"- thesis_id: {thesis.name}",
        f"- name: {facts['name']}",
        f"- claim: {facts['claim'] or '(none)'}",
        f"- constitution_pin: {facts['pin'] or '(none)'}",
        f"- as_of: {facts['as_of'] or '(none)'}",
        f"- entry_count: {facts['entry_count'] if facts['entry_count'] is not None else '(none)'}",
        f"- universe: {universe}",
        "",
    ]
    for glob in ["_cross/*_synthesis.md", "snapshots/**/*.md"]:
        for p in sorted(thesis.glob(glob)):
            if not p.is_file():
                continue
            lines += [f"## Source — {p.relative_to(thesis)}",
                      "````markdown", p.read_text(encoding="utf-8").rstrip(),
                      "````", ""]
    artifacts = thesis / "artifacts"
    if artifacts.is_dir():
        for ticker_dir in sorted(p for p in artifacts.iterdir() if p.is_dir()):
            for p in sorted(ticker_dir.glob("*.md")):
                body = p.read_text(encoding="utf-8")
                if body_limit and len(body) > body_limit:
                    body = _truncate_artifact(body, body_limit, p)
                lines += [f"## Artifact — {p.relative_to(thesis)}",
                          "````markdown", body.rstrip(), "````", ""]
    return "\n".join(lines) + "\n"


def _json_default(obj):
    """Deterministic fallback for YAML-native scalars (date/datetime) inside
    frontmatter — ISO strings, never locale-dependent."""
    import datetime as _dt

    if isinstance(obj, (_dt.date, _dt.datetime)):
        return obj.isoformat()
    return str(obj)


def extract_metrics(thesis: Path) -> dict:
    """Deterministic per-ticker metrics bundle for report authoring (v0.3.0).

    KPI tiles and kpi_trend charts draw from this. Raw values verbatim (ints stay
    ints, strings like ">10,000x" / "900-3700" preserved — only the LLM formats),
    key names lowercased, first-sorted-file wins for the value while
    metric_sources lists every contributing file. Never fed to the citation
    gate; never timestamped (byte-deterministic)."""
    tickers: dict[str, dict] = {}
    artifacts = thesis / "artifacts"
    if artifacts.is_dir():
        for ticker_dir in sorted(p for p in artifacts.iterdir() if p.is_dir()):
            entry: dict = {"artifacts": [], "key_metrics": {}, "metric_sources": {},
                           "entity_claims": [], "conclusions": [], "counts": {}}
            for p in sorted(ticker_dir.glob("*.md")):
                rel = str(p.relative_to(thesis)).replace(os.sep, "/")
                entry["artifacts"].append(rel)
                fm = _frontmatter(p.read_text(encoding="utf-8"))
                for key, value in (fm.get("key_metrics") or {}).items():
                    lkey = str(key).lower()
                    if lkey not in entry["key_metrics"]:
                        entry["key_metrics"][lkey] = value
                    entry["metric_sources"].setdefault(lkey, []).append(rel)
                entry["entity_claims"].extend(fm.get("entity_claims") or [])
                entry["conclusions"].extend(fm.get("conclusions") or [])
                for field in ("facts_count", "deducted_count", "views_count",
                              "citation_count"):
                    entry["counts"][field] = entry["counts"].get(field, 0) + (fm.get(field) or 0)
            tickers[ticker_dir.name] = entry
    synthesis: dict = {}
    synth = _newest_file(["_cross/*_synthesis.md"], thesis)
    if synth:
        fm = _frontmatter(synth.read_text(encoding="utf-8"))
        synthesis = {"pillar_verdicts": fm.get("pillar_verdicts") or {},
                     "capability_timeline": fm.get("capability_timeline") or {}}
    return {"pack_version": PACK_VERSION, "thesis": thesis.name,
            "tickers": tickers, "synthesis": synthesis}


class MetricsMissingError(ValueError):
    """Q97(1) — a metrics bundle with no series is a FAILURE, not a result."""


def _require_metrics(metrics: dict, thesis: Path) -> None:
    """Refuse to write a `metrics.json` that carries no series (Q97(1)).

    Before this check, `pack()` wrote whatever `extract_metrics()` returned. A
    thesis whose artifacts lacked FR-090 frontmatter therefore produced an EMPTY
    `metrics.json` **and a success exit** — the report then rendered with no KPI
    tiles and nothing anywhere said why. Measured on
    `agentii-space-tech-SPACE/theses/001-technology-baseline`, which is the run
    the plan calls the single measurable proof that Part II is real.

    The message names what was examined and what would populate it, because a
    hard failure that does not say where to look just moves the silence.
    """
    tickers = metrics.get("tickers") or {}
    with_kpi = [t for t, e in tickers.items() if e.get("key_metrics")]
    if with_kpi:
        return
    artifacts = sum(len(e.get("artifacts") or []) for e in tickers.values())
    raise MetricsMissingError(
        f"PACK REFUSED (Q97(1)): the metrics bundle has no series.\n"
        f"  thesis    : {thesis}\n"
        f"  scanned   : {len(tickers)} ticker dir(s), {artifacts} artifact(s) "
        f"under {thesis / 'artifacts'}\n"
        f"  with KPIs : 0\n"
        + (f"  tickers   : {', '.join(sorted(tickers)) or '(none)'}\n"
           if tickers else "")
        + "  an artifact contributes metrics only through FR-090 frontmatter: "
          "`key_metrics` (the KPI source), `conclusions`, `entity_claims`.\n"
          "  An EMPTY bundle means the artifacts are missing those fields — not "
          "that the thesis has no metrics.\n"
          "  Fix the artifacts, then re-run pack. Nothing was written.")


def pack(thesis: Path, body_limit: int | None = None) -> tuple[Path, str]:
    thesis = Path(thesis)
    # Q97(1) runs BEFORE any write. The first version checked after writing
    # report-input.md and still told the user "Nothing was written" — a message
    # asserting something the code did not do, which is the defect this whole
    # spec is about arriving inside its own fix.
    metrics = extract_metrics(thesis)
    _require_metrics(metrics, thesis)
    out = thesis / "report-input.md"
    _write_generated(out, pack_text(thesis, body_limit))
    metrics_path = thesis / "report" / "metrics.json"
    _write_generated(metrics_path,
                     json.dumps(metrics, indent=2, ensure_ascii=False,
                                default=_json_default) + "\n")
    return out, sources_hash(thesis)


# ─────────────────────────── content.html contract ───────────────────────────

_ALLOWED_TAGS = {
    "section", "h1", "h2", "h3", "p", "ul", "ol", "li", "table", "thead",
    "tbody", "tr", "th", "td", "b", "strong", "i", "em", "code", "a", "div",
    "span", "br", "hr", "blockquote",
}
_CHART_REQUIRED = {
    "football_field": ("labels", "lows", "highs"),
    "peer_bars": ("labels", "values"),
    "kpi_trend": ("x", "y"),
    "scatter": ("x", "y"),
    "scenario_tree": ("edges",),
    # The one kind that is NOT drawn from data: `asset` names a filing figure the
    # thesis fetched for itself (tools/fetch_filing_figures.py). `alt` is optional
    # here but `_gate_charts` requires an accompanying .fig-caption, because a
    # raster has no textual content of its own.
    "filing_figure": ("asset",),
}

# HARD CAP on filing figures per report. This is a PLATFORM-PROTECTION limit, not
# a layout one, and it is deliberate that it is a REFUSAL rather than a warning.
#
# agentii.ai serves each document from a rate-limited R2 origin, and obtaining a
# figure means a full-document GET — there is no per-image endpoint, because the
# filer's JPEGs are carried inline in the exhibit HTML. A report that embeds many
# is therefore indistinguishable from a scraping job no matter what its author
# intends, and it competes with every other reader for the same origin. The
# product position is that people may READ filings on the platform; a report may
# QUOTE a handful with attribution. Five is the quoted-with-attribution budget.
#
# The load-bearing limit is here rather than in the fetch tool because the report
# is what a reader distributes, and a cap the assembler enforces cannot be
# exceeded by any route into it — including an author who fetched assets by hand.
MAX_FILING_FIGURES = 5
_FORBIDDEN_DOC_RE = re.compile(r"(?i)<\s*!doctype\b|<\s*/?\s*(html|head|body|style|script)\b")
_RESERVED_ID_RE = re.compile(r"^(cover-|stale-bar$)")

# Q139: assembler-owned classes. The author writes none of them — the chrome, the
# cover and the disclaimer tail are injected. A collision is a hard validation
# error, the same shape as a reserved id.
_RESERVED_CLASSES = frozenset({"disclaimer", "sheet-head", "sheet-foot", "reg",
                               "page-mark", "cover", "stale-bar", "draft-banner"})
_CITE_HREF_RE = re.compile(r"https://agentii\.ai/v/([A-Z0-9]+)/([a-z0-9_-]+)/\S*")


class _ContentParser(html.parser.HTMLParser):
    """One pass over content.html: whitelist, section nesting, ids, hrefs,
    chart tokens. Deterministic; reports every violation, not just the first."""

    def __init__(self):
        super().__init__()
        self.problems: list[str] = []
        self.section_depth = 0
        self.page_count = 0
        self.ids: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in _ALLOWED_TAGS:
            self.problems.append(f"forbidden element <{tag}> (fragment whitelist)")
            return
        if tag == "section":
            self.section_depth += 1
            if self.section_depth > 1:
                self.problems.append("nested <section> inside a page")
            if "page" not in (a.get("class") or "").split():
                self.problems.append('<section> missing class="page"')
            else:
                self.page_count += 1
        if tag == "img":
            self.problems.append("forbidden <img> — charts use data-chart tokens (Q48)")
        if "id" in a:
            self.ids.append(a["id"])
            if _RESERVED_ID_RE.match(a["id"]):
                self.problems.append(f"id '{a['id']}' collides with template ids")
        for cls in (a.get("class") or "").split():
            if cls in _RESERVED_CLASSES:
                self.problems.append(
                    f"class '{cls}' is assembler-owned — the author never emits it "
                    f"(Q139)")
        if a.get("href"):
            self.hrefs.append(a["href"])
        if tag == "div" and "data-chart" in a:
            kind = a.get("data-chart")
            if kind not in _CHART_REQUIRED:
                self.problems.append(f"unknown chart kind '{kind}'")
            else:
                try:
                    spec = json.loads(a.get("data-spec") or "")
                except ValueError:
                    self.problems.append(f"chart {kind}: data-spec is not valid JSON")
                else:
                    for key in _CHART_REQUIRED[kind]:
                        if key not in spec:
                            self.problems.append(f"chart {kind}: data-spec missing '{key}'")
                h = a.get("data-height") or ""
                if not (h.isdigit() and int(h) > 0):
                    self.problems.append(f"chart {kind}: data-height must be a positive integer")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)  # <br/>-style void elements

    def handle_endtag(self, tag):
        if tag == "section":
            self.section_depth -= 1


# ── the report gates (T131–T134; Q94/Q115/Q118) ─────────────────────────────
#
# Four deterministic gates on the authored fragment. Each exists because the
# defect it catches was MEASURED in a live report, and each is placed here
# because Q115's argument generalises: the report is a NEW document assembled
# AFTER every existing gate has run, so nothing before this point can see
# in-document inconsistency.

# Q118: the measured defect — every chart in three reports had `alt="kpi_trend"`,
# the chart KIND's name, never a description of the data. In a print-first PDF
# that leaves the figure with no textual content at all: text search cannot find
# it, accessibility tools cannot see it, and a reader who does not "decode the
# shape" has no way to learn what the axes mean.
_CHART_KIND_ALTS = {
    "kpi_trend", "peer_bars", "waterfall", "scatter", "line", "bar", "chart",
    "trend", "sparkline", "area", "column", "pie", "donut", "histogram",
    "filing_figure",  # a raster needs its alt to describe the figure, not the kind
}

# A caption must name UNITS. Q118 pairs this with Q97(2)'s axis requirement: the
# geometric layer and the textual layer together are what make a chart readable,
# and either alone leaves a shape occupying space.
_UNIT_RX = re.compile(
    r"(?i)(%|percent|pp\b|bps?\b|basis points?|USD|US\$|\$|EUR|GBP|JPY|"
    r"metric tons?|tonnes?|shares?|units?|x\b|\bmm\b|\bbn\b|\bbillion\b|"
    r"\bmillion\b|thousand|per cent|×)")

# Q115: a headline figure must trace to the pack, and two pages must not give one
# metric two values. The extraction is deliberately narrow — it reads the
# machine-readable attributes the renderer already emits rather than parsing
# prose, because Q146's rule applies here too: making a determinism gate parse
# prose injects non-determinism into the gate.
_METRIC_RX = re.compile(
    r'data-metric\s*=\s*["\']([^"\']+)["\'][^>]*?'          # data-metric="x"
    r'data-period\s*=\s*["\']([^"\']*)["\'][^>]*?'
    r'data-value\s*=\s*["\']([^"\']+)["\']', re.I)


def _gate_page_shape(content: str) -> list[str]:
    """T132 (Q115): a page that is ONLY a table + caption is not an argument.

    Q142's page contracts put the table SUBORDINATE to the argument — a page
    whose entire content is a grid of numbers states no claim, so a reader
    cannot tell what it is evidence FOR. Measured: report pages that were
    tables with a one-line caption above them."""
    problems: list[str] = []
    for i, page in enumerate(re.findall(r'<section[^>]*class="[^"]*page[^"]*"[^>]*>(.*?)</section>',
                                        content, re.S | re.I), 1):
        # ONLY a page that HAS a table is this gate's subject. The first version
        # flagged any page under 80 chars of non-table text, which also caught a
        # short-but-legitimate prose page — over-reach, caught by
        # test_quality_advisories_non_blocking, whose whole purpose is a
        # deliberately minimal fragment. Q115 says "a page that is only a table
        # + caption"; a page with no table is a different question.
        if not re.search(r"<table\b", page, re.I):
            continue
        stripped = re.sub(r"<table\b.*?</table>", "", page, flags=re.S | re.I)
        stripped = re.sub(r"<[^>]+>", " ", stripped)
        stripped = re.sub(r"\s+", " ", stripped).strip()
        if len(stripped) < 80:
            problems.append(
                f"page {i} is only a table (with caption): {len(stripped)} chars of "
                f"non-table text. A table states no claim — Q142's page contracts "
                f"make it SUBORDINATE to an argument that says what the numbers are "
                f"evidence for (Q115/T132).")
    return problems


def _gate_page_argument(content: str) -> list[str]:
    """T135 (Q95 contracts 1 and 2).

    Q95's measured failure was PAGE-LEVEL, so the fix is too: PA 001's corpus
    pages were not "bad content" — they were **structurally specified as
    enumerations** (`.stat-row` + a 22–28 cell table + one caption). The user's
    ask that key arguments lead to investment decisions had nowhere to land.

    Contract 1 — the heading is a CLAIM, not a label. Measured: the three shipped
    reports already do this ("Launch is 12.3% of revenue at the launch company"),
    so this is a KEEP, not a new requirement — the gate exists to stop the
    practice regressing, which is the only way a satisfied constraint stays
    satisfied.

    Contract 2 — every page carries explanatory prose that lands on investment
    meaning. The measured counter-example: "badge census is not an argument" — a
    page reporting how many facts it contains, rather than what they mean.
    """
    problems: list[str] = []
    # A heading made only of a noun phrase is a label. Two independent signals,
    # because either alone misfires: very short headings, and headings that are a
    # bare ticker/company/section name.
    _LABEL_RX = re.compile(r"^(?:[A-Z]{2,5}|[A-Z][a-z]+(?: [A-Z][a-z]+)?|"
                           r"Evidence|Summary|Overview|Introduction|Background|"
                           r"Appendix|Details|Analysis|Data)$")
    for i, page in enumerate(re.findall(
            r'<section[^>]*class="[^"]*page[^"]*"[^>]*>(.*?)</section>', content, re.S | re.I), 1):
        h = re.search(r"<h[12][^>]*>(.*?)</h[12]>", page, re.S | re.I)
        if h:
            head = re.sub(r"<[^>]+>", "", h.group(1))
            head = re.sub(r"\s+", " ", head).strip().rstrip(".")
            if _LABEL_RX.match(head) or len(head.split()) < 4:
                problems.append(
                    f"page {i}'s heading is a LABEL, not a claim: {head!r}. Q95 "
                    f"contract 1 — a heading must state what the page argues, e.g. "
                    f"'Launch is 12.3% of revenue at the launch company', not "
                    f"'Evidence' or the ticker.")

        # contract 2: PARAGRAPH prose, and it must land somewhere.
        #
        # Counted from `<p>` elements only — NOT every non-table word. The first
        # version stripped tags from the whole page, which counted the HEADING as
        # explanatory prose; a page could then clear the threshold with its title
        # alone, which is the badge-census failure in another costume. Q95 says
        # 解释性正文 — explanatory body text — and a heading is not that.
        paras = re.findall(r"<p\b[^>]*>(.*?)</p>", page, re.S | re.I)
        prose = " ".join(re.sub(r"<[^>]+>", " ", p) for p in paras)
        prose = re.sub(r"\s+", " ", prose).strip()
        words = len(re.findall(r"\S+", prose))
        # THRESHOLD CALIBRATION, stated because Q95 gives no number and I picked
        # one. Two corrections got it here, and both are recorded because the
        # number is a judgement dressed as a measurement:
        #
        #   40 -> rejected a genuine 35-word argument (too high)
        #   25 -> counted the HEADING as prose; once the count is `<p>`-only, 25
        #         rejects ordinary argument paragraphs (too high again)
        #   20 -> sits above nothing in particular and below real prose. It is
        #         deliberately NOT tuned to catch the measured failure, because
        #         CONTRACT 3 already catches it: PA 001's page was 4 tiles + a
        #         28-cell table, which fails the table-only rule outright. Setting
        #         this threshold high enough to catch that page would fail normal
        #         argument pages, and a gate that fails good pages gets disabled.
        if words < 20:
            problems.append(
                f"page {i} carries {words} words of explanatory prose — Q95 "
                f"contract 2 requires the page to say what its numbers mean, and a "
                f"badge census is not an argument (the measured case: 35 words, "
                f"half of them a badge census).")
        else:
            # ── T089 / FR-067: the four-word proxy is replaced where it could not work, and kept
            #    only where nothing else can speak ────────────────────────────────────────────────
            #
            # THE PROXY PASSED THE VERY PAGES IT EXISTED TO CATCH. It asked whether the prose contained
            # one of `implies / means / therefore / argues for`, and "Revenue therefore rose 12% to
            # $1.2B" contains one while being a fact statement. That is the reported symptom — a heap
            # of figures with no reading — and the check could not see it by construction.
            #
            # WHAT REPLACES IT IS THE ONE RATIO THE CORPUS SUPPORTS WITH A UNIVERSAL FLOOR: the share
            # of numeric sentences that also carry a reading. `contracts/report-readability.md` §2 row
            # 5 measured it at 0.27–0.66 across **every** family and every size in the 73-report
            # Morgan Stanley archive, so a 0.25 floor passes all of them, and the same measurement is
            # what forbids setting it higher (the largest family sits at 0.36–0.39, so 0.5 would fail
            # all 30 of its documents). The implementation is not duplicated here — it is the gate
            # T086 already wrote, called with the same prose this function already extracted.
            #
            # WHY THIS IS NOT A PURE REPLACEMENT, which is the one judgement in this edit.
            #
            # The floor is BLOCKING WHERE IT APPLIES and silent where it does not: below
            # `MIN_NUMERIC_SENTENCES` numeric sentences it returns `[]`, which means "unmeasurable",
            # not "clean" — the measured case being a badge census whose numerals are words
            # ("fourteen facts and two badges"), so the ratio has nothing to divide. And the two checks
            # ask DIFFERENT QUESTIONS rather than restating one: the floor asks whether the figures are
            # read, Q95 contract 2 asks whether the prose lands on an implication. A page can fail
            # either while clearing the other:
            #
            #   twelve bare figures + one interpretation   floor FAILS, contract 2 clears  (the
            #                                              case the four-word proxy could not see)
            #   twelve directional sentences, no implication   floor clears, contract 2 FAILS
            #
            # So the token test is KEPT — a union, never a loosening. It runs whenever the floor has
            # not already failed, which is strictly more enforcement than before at both ends. The
            # floor's finding is preferred where both fire, because it carries the ratio and is
            # therefore the one an author can act on.
            #
            # MEASURED, AND ONE LIMIT THAT IS NOT FIXED HERE. Ten sentences of "Revenue therefore rose
            # 12% to $1.2B" pass BOTH checks — `therefore` is an interpretation token, so the ratio is
            # 10/10. FR-067's example sentence is a restatement that no token list can separate from a
            # reading, because the words are the same; separating them needs the scored tier
            # (`FR-065`, `score_report_readability.py`), which is where "the reading is shallow" can be
            # said at all. What this edit fixes is the BREADTH defect — one keyword in one sentence can
            # no longer certify a page of bare figures.
            floor = check_report_readability.check_interpretive_floor(prose)
            if floor:
                problems.extend(f"page {i}: {finding}" for finding in floor)
            elif not _CONCLUSION_RX.search(prose):
                problems.append(
                    f"page {i}'s prose never lands on an investment implication (no "
                    f"'implies / means / therefore / argues for'). Q95 contract 2: the "
                    f"explanatory text must point at what this means for the position, "
                    f"not restate the data.")
    return problems


def _gate_charts(content: str) -> list[str]:
    """T133 (Q118): caption present and human-readable; `alt` not a kind name.

    ⚠️ The `<img>` and `<figure>` loops below are UNREACHABLE for the letter
    report, and always have been: `_ALLOWED_TAGS` admits neither tag, so
    `_validate_content` rejects any authored content carrying them before this
    gate is ever consulted. They are kept rather than deleted so that widening
    the whitelist cannot silently drop the enforcement — but no reader should
    mistake them for running checks. For this template family Q118 is carried by
    the `filing_figure` loop at the end, which is the only figure route the
    whitelist permits.
    """
    problems: list[str] = []
    for m in re.finditer(r"<img\b[^>]*>", content, re.I):
        tag = m.group(0)
        alt = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', tag, re.I)
        alt_v = (alt.group(1) if alt else "").strip()
        if not alt_v:
            problems.append("a chart has no non-empty `alt` (Q118)")
        elif alt_v.lower().replace("-", "_") in _CHART_KIND_ALTS:
            problems.append(
                f"a chart's `alt` is the chart KIND's name ({alt_v!r}), not a "
                f"description of the data — in a print-first PDF that leaves the "
                f"figure with no textual content at all (Q118)")
    # captions: every figure must carry one naming what it draws, units, source
    for fm in re.finditer(r"<figure\b.*?</figure>", content, re.S | re.I):
        fig = fm.group(0)
        cap = re.search(r"<figcaption\b[^>]*>(.*?)</figcaption>", fig, re.S | re.I)
        if not cap:
            problems.append("a chart has no <figcaption> (Q118)")
            continue
        text = re.sub(r"<[^>]+>", " ", cap.group(1))
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 20:
            problems.append(f"a chart caption is too short to name anything: {text!r}")
        if not _UNIT_RX.search(text):
            problems.append(
                f"a chart caption names no UNIT: {text[:70]!r}. Q118 requires the "
                f"caption to name what is drawn, its units, and its source — the "
                f"textual half of what Q97(2) requires geometrically.")
    # filing_figure tokens (Q118 extended, 2026-09-19) — the one figure route the
    # whitelist permits. A raster carries no text, no search and no basis, so its
    # caption IS its provenance: what it is, its units, its citable source, and
    # that it is issuer-produced and unaudited.
    for m in re.finditer(
            r'<div\b[^>]*data-chart="filing_figure"[^>]*>\s*</div>\s*'
            r'(<p\b[^>]*class="[^"]*fig-caption[^"]*"[^>]*>.*?</p>)?',
            content, re.S | re.I):
        cap = m.group(1)
        if not cap:
            problems.append(
                'a filing_figure token has no <p class="fig-caption"> immediately '
                "after it — a raster carries no textual content, so Q118 requires "
                "the caption to name what it is, its units, and its source")
            continue
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", cap)).strip()
        if len(text) < 20:
            problems.append(
                f"a filing_figure caption is too short to name anything: {text!r}")
        if not _UNIT_RX.search(text):
            problems.append(
                f"a filing_figure caption names no UNIT: {text[:70]!r}")
        if not re.search(r'href\s*=\s*["\']https://agentii\.ai/v/\S+', cap, re.I):
            problems.append(
                f"a filing_figure caption carries no agentii.ai/v/ source link: "
                f"{text[:70]!r} — an embedded filing image with no citable source "
                f"is the least auditable artifact a report can carry")
    # The platform-protection cap. Counted on TOKENS, so it binds the report as
    # authored and cannot be evaded by how the assets arrived on disk.
    n_figs = len(re.findall(r'<div\b[^>]*data-chart="filing_figure"', content, re.I))
    if n_figs > MAX_FILING_FIGURES:
        problems.append(
            f"this report embeds {n_figs} filing figures; the cap is "
            f"{MAX_FILING_FIGURES}. Fetching each one is a full-document GET against "
            f"a rate-limited origin, so a report is indistinguishable from a scraper "
            f"above this count — and it degrades the platform for every other reader. "
            f"Quote the few that carry an argument; cite the rest by page link.")
    return problems


def _gate_self_consistency(content: str, metrics: dict) -> list[str]:
    """T134 (Q115): one metric, one value — in-document AND against metrics.json.

    Measured before this existed: a report contradicted itself by 15.3 pp, and
    carried three competing 'best gross margin' superlatives. The cost is
    specific to reports: a reader who meets one metric at two values on pages 6
    and 11 stops believing the rest of the numbers, INCLUDING the correct ones.
    That is not "a page is wrong" — it is "the document is no longer
    trustworthy", which is why it fails assembly rather than warning."""
    problems: list[str] = []
    seen: dict[tuple[str, str], tuple[str, int]] = {}
    for i, m in enumerate(_METRIC_RX.finditer(content), 1):
        metric, period, value = (m.group(1).strip(), m.group(2).strip(),
                                 m.group(3).strip())
        key = (metric, period)
        if key in seen:
            prev, _ = seen[key]
            if _num_of(prev) != _num_of(value):
                problems.append(
                    f"the document contradicts itself on {metric!r} ({period}): "
                    f"{prev} vs {value}. A reader who meets one metric at two "
                    f"values distrusts every other number too (Q115/T134)")
        else:
            seen[key] = (value, i)
    # TRACEABILITY is a separate question, and it is about the HEADLINE figure
    # only. Q115: "头条数字无法溯源到 pack" — the headline cannot be traced. The
    # first version compared EVERY occurrence against `metrics.json`, which holds
    # ONE period-less value per metric, so a document showing revenue for Q1 and
    # Q2 was flagged for the Q1 row — a false positive that would fire on every
    # real multi-period report.
    #
    # So: for each metric named in `key_metrics`, the document's value at its
    # LATEST period must match the pack. Earlier periods are history, not
    # headline.
    mj = metrics.get("key_metrics") if isinstance(metrics, dict) else None
    if isinstance(mj, dict):
        by_metric: dict[str, list[tuple[str, str]]] = {}
        for m in _METRIC_RX.finditer(content):
            by_metric.setdefault(m.group(1).strip(), []).append(
                (m.group(2).strip(), m.group(3).strip()))
        for metric, ref_raw in mj.items():
            rows = by_metric.get(metric)
            if not rows:
                continue
            _period, latest = sorted(rows, key=lambda r: r[0])[-1]
            ref = _num_of(str(ref_raw))
            got = _num_of(latest)
            if ref is not None and got is not None and ref != got:
                problems.append(
                    f"{metric!r} is {latest} in the report but {ref_raw!r} in "
                    f"metrics.json — a headline figure that cannot be traced to the "
                    f"pack fails assembly (Q115)")
    return problems


def _load_metrics(thesis: Path) -> dict:
    """`report/metrics.json` — the pack's own numbers, and T134's second operand.
    Absent or empty is not an error here: `pack` already hard-fails on that
    (Q97(1)), so reaching assemble with no metrics means pack was bypassed."""
    f = thesis / "report" / "metrics.json"
    if not f.is_file():
        return {}
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _num_of(s: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", str(s).replace(",", ""))
    return float(m.group(0)) if m else None


# Q94: the outline elements a report must have decided BEFORE writing pages.
_OUTLINE_ELEMENTS = {
    "argument": re.compile(r"(?im)^\s*#{1,4}\s*.*(argument|论断|论点)"),
    "evidence": re.compile(r"(?im)^\s*#{1,4}\s*.*(evidence|证据)"),
    "pages":    re.compile(r"(?im)^\s*#{1,4}\s*.*(page|页)"),
    "storyline": re.compile(r"(?im)^\s*#{1,4}\s*.*(story|叙事|故事线)"),
}
# An argument that restates a fact is not an argument. Q94: each key argument
# must point at an investment CONCLUSION — "what this means for expectations or
# returns" — not repeat what the data says.
_CONCLUSION_RX = re.compile(
    r"(?i)(implies|means|suggests|therefore|so that|argues for|supports a|"
    r"warrants|justifies|points to|应当|意味着|因此|支持|指向)")


def gate_outline(thesis: Path) -> list[str]:
    """T131 (Q94): authoring is REFUSED without report/outline.md.

    Q94's measured basis: the render-and-optimize loop was proven for LAYOUT and
    had no counterpart for the ARGUMENT — the author step went from a 333 KB pack
    to content.html in one pass, and every iteration after it checked clipping,
    density and orphan headings. So structure was never chosen, only emerged. A
    corpus-wide search for outline/abstract/story-line/key-argument in the
    scenarios vertical returned ZERO hits."""
    f = thesis / "report" / "outline.md"
    if not f.is_file():
        return [f"report/outline.md not found. Q94: the outline is written and "
                f"FINALISED before any page is authored — without it the structure "
                f"of the argument is never chosen, only emerges. Minimum content: "
                f"key arguments (each a claim pointing at an investment conclusion), "
                f"argument -> evidence, argument -> page plan, and the story line."]
    text = f.read_text(encoding="utf-8")
    problems = [f"outline.md has no {name} section (Q94)"
                for name, rx in _OUTLINE_ELEMENTS.items() if not rx.search(text)]
    args = re.findall(r"(?im)^\s*#{1,4}\s*.*(?:argument|论断|论点).*$\n((?:.*\n)*?)(?=#|\Z)",
                      text)
    body = " ".join(args)
    if body.strip() and not _CONCLUSION_RX.search(body):
        problems.append(
            "outline.md's arguments never point at an investment conclusion — "
            "Q94: each key argument must say what this means for expectations or "
            "returns, not restate what the data says")
    return problems


def _validate_content(content: str, pack_txt: str) -> list[str]:
    """Hard gates over the LLM-authored fragment. Empty list = valid."""
    if not content.strip():
        return ["content.html is empty"]
    if _FORBIDDEN_DOC_RE.search(content):
        return ["content.html must be a fragment, not a document "
                "(found <!DOCTYPE>/<html>/<head>/<body>/<style>/<script> tags)"]
    parser = _ContentParser()
    parser.feed(content)
    problems = list(parser.problems)
    if parser.page_count < 1:
        problems.append('no <section class="page"> found')
    if parser.section_depth != 0:
        problems.append("unbalanced <section> tags")
    if not problems:
        # Citation anti-fabrication gate: every viewer link's
        # {ticker}/{citation_id} pair must appear in the source pack.
        allowed = set(re.findall(r"agentii\.ai/v/([A-Z0-9]+)/([a-z0-9_-]+)/", pack_txt))
        for href in parser.hrefs:
            m = _CITE_HREF_RE.match(href)
            if m and (m.group(1), m.group(2)) not in allowed:
                problems.append(f"citation href '{href}' is not backed by any "
                                "source file (fabricated citation_id)")
    return problems


_CHART_TOKEN_RE = re.compile(
    r'<div\b(?=[^>]*\bdata-chart="([^"]+)")(?=[^>]*\bdata-spec=\x27(.*?)\x27)'
    r'(?=[^>]*\bdata-height="(\d+)")[^>]*>\s*</div>')


def render_chart_tokens(content: str, thesis: Path | None = None) -> str:
    """Replace data-chart token divs with base64 <img> (Q48). The img keeps
    an explicit height so the overflow estimator counts it honestly.

    Two families reach here. The five numeric kinds are DRAWN by chart_render
    from the spec's data. `filing_figure` is the one kind that is not drawn: its
    spec names a local asset the thesis fetched for itself, and the bytes are
    inlined verbatim. It is the only route by which a raster can reach a report
    — and it stays a token rather than an <img> in content.html, so the fragment
    whitelist still holds and the figure is still born after validation.
    """

    def _sub(m: re.Match) -> str:
        kind, spec_json, height = m.group(1), m.group(2), m.group(3)
        spec = json.loads(spec_json)
        if kind == "filing_figure":
            if thesis is None:
                raise ValueError(
                    "a filing_figure token needs the thesis dir to resolve its asset")
            uri = chart_render.to_image_uri(thesis / spec["asset"])
            alt = spec.get("alt") or kind
        else:
            uri = chart_render.to_data_uri(chart_render.render_svg(kind, spec))
            alt = kind
        return (f'<img src="{uri}" alt="{alt}" height="{height}" '
                f'style="width:100%;object-fit:contain">')

    return _CHART_TOKEN_RE.sub(_sub, content)


def _renumber_pages(content: str) -> str:
    """Strip any ids/data-report-page on the authored sections, then renumber
    starting at 2 (the cover owns page 1)."""

    class _TagAttrs(html.parser.HTMLParser):
        def handle_starttag(self, tag, attrs):
            self.attrs = dict(attrs)

    toks = re.split(r"(<section\b[^>]*>)", content)
    out: list[str] = [toks[0]]
    n = 0
    for i in range(1, len(toks), 2):
        tag = toks[i]
        parser = _TagAttrs()
        parser.feed(tag)
        if "page" in (parser.attrs.get("class") or "").split():
            n += 1
            tag = re.sub(r'\s+data-report-page="[^"]*"', "", tag)
            tag = re.sub(r'\s+id="[^"]*"', "", tag)
            tag = tag[:-1] + f' data-report-page="{n + 1}" id="page-{n + 1}">'
        out.append(tag)
        if i + 1 < len(toks):
            out.append(toks[i + 1])
    return "".join(out)


def _inject_page_chrome(pages_html: str, total: int, slug: str, thesis_num: str) -> str:
    """Running sheet head/foot + page marks + registration marks on every content
    page (v0.3.0). Assembler-owned — the LLM never authors these reserved classes
    (sheet-head / sheet-foot / reg / page-mark)."""
    def _chrome(m: re.Match) -> str:
        n = int(m.group(2))
        return (m.group(1)
                + f'<div class="sheet-head"><span>AGENTII THESIS REPORT</span>'
                  f'<span>THESIS {_html.escape(thesis_num)}</span></div>'
                + '<i class="reg reg-tl"></i><i class="reg reg-tr"></i>'
                  '<i class="reg reg-bl"></i><i class="reg reg-br"></i>'
                + f'<div class="sheet-foot"><span>{_html.escape(slug)}</span>'
                  '<span class="print-center no-print">'
                  '<button type="button" class="print-btn" '
                  'title="Safari print dialog — Paper: US Letter · Margins: None · '
                  'Scale: 100% · Print backgrounds: ON" '
                  'onclick="window.print()">Print / PDF</button>'
                  '<span class="print-hint">US Letter · Margins: None · '
                  'Scale: 100% · Print backgrounds</span></span>'
                  f'<span class="page-mark">{n:02d} / {total:02d}</span></div>')

    return re.sub(r'(<section\b[^>]*data-report-page="(\d+)"[^>]*>)', _chrome, pages_html)


def _quality_advisories(content: str) -> list[str]:
    """NON-blocking quality guidance (v0.3.0) — the SKILL.md checklist, echoed
    by the machine where it is mechanically detectable. Hard gates stay as-is;
    these warn only."""
    advisories: list[str] = []
    if 'class="stat-row"' not in content:
        advisories.append("no .stat-row KPI tiles anywhere — the executive "
                          "summary page requires a 2–4 tile row")
    elif not re.search(r'<section\b[^>]*class="[^"]*page[^"]*"[^>]*>'
                       r'(?:(?!</section>).)*?class="stat-row"', content, re.DOTALL):
        advisories.append("the first page (executive summary) has no .stat-row tile row")
    if not re.search(r'class="[^"]*badge-(supported|indeterminate|refuted)[^"]*"', content):
        advisories.append("no pillar verdict badges "
                          "(.badge-supported/.badge-indeterminate/.badge-refuted)")
    if 'class="timeline"' not in content:
        advisories.append("capability timeline not styled (.timeline / .tl-item)")
    if 'class="sec-kicker"' not in content:
        advisories.append("no section kickers (.sec-kicker) — every page opens with one")
    if re.search(r"\*\*[^*]+\*\*|````", content):
        advisories.append("raw markdown leakage (** or code fences) in content")
    return advisories


def _workspace_language(thesis: Path) -> str | None:
    """Q126/T138: the language a WORKSPACE declares, from its own `style.md`.

    `contracts/preflight.md` step 2 already reads `style.md` for per-workspace
    overrides (`default_lookback_quarters`, `reporting_currency`, …), so the
    language is one more declaration in a file the pipeline already reads —
    no new mechanism, no new file, no registry (Q4).
    """
    for candidate in (thesis.parent.parent / "style.md", thesis.parent / "style.md"):
        if not candidate.is_file():
            continue
        m = re.search(r"^language\s*:\s*(\S+)\s*$",
                      candidate.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip().strip("'\"")
    return None


def _disclaimer_clauses(body: str) -> list[str]:
    """The clause ids a rendering carries. Stable ids are what make Q139 rule 3
    ENFORCEABLE — without them 'the clause set is the contract' cannot be checked,
    and a translation could silently drop the liability clause and still read as
    compliant."""
    return re.findall(r'data-clause\s*=\s*["\']([^"\']+)["\']', body)


def _disclaimer_body(thesis: Path | None = None) -> str:
    """The canonical HTML disclaimer block, read out of disclaimer.md.

    disclaimer.md is the single source (Q139 rule 1). Reading it rather than
    copying it into the template makes "never restated, never forked" an enforced
    property instead of a declared one. A missing or malformed block is a hard
    error: a presentation output must not ship without its disclaimer."""
    if not DISCLAIMER_MD.is_file():
        raise ValueError(f"disclaimer template missing: {DISCLAIMER_MD} (Q139)")
    # T138 (Q126): language follows the WORKSPACE. The canonical file is English;
    # a workspace declaring another language supplies its own rendering of the
    # SAME clauses, and the clause SET is verified. Resolution order: the
    # workspace's own file, then the kit's canonical one.
    canonical = DISCLAIMER_MD.read_text(encoding="utf-8")
    source, src_path = canonical, DISCLAIMER_MD
    lang = _workspace_language(thesis) if thesis is not None else None
    if lang and lang.lower() not in ("en", "english"):
        for cand in ((thesis.parent.parent / f"disclaimer.{lang}.md"),
                     (thesis.parent.parent / "disclaimer.md")):
            if cand.is_file():
                source, src_path = cand.read_text(encoding="utf-8"), cand
                break
        else:
            raise ValueError(
                f"workspace declares language {lang!r} but supplies no "
                f"disclaimer.{lang}.md (or disclaimer.md) — Q126: the clause set is "
                f"the contract and the wording is the workspace's rendering, so the "
                f"rendering must exist. Shipping the English text into a workspace "
                f"that declared another language is the failure this prevents.")

    blocks = re.findall(r"^```html\n(.*?)^```", source, re.DOTALL | re.MULTILINE)
    if len(blocks) != 1:
        raise ValueError(
            f"{src_path.name} must carry exactly one ```html block "
            f"(found {len(blocks)}) — it is the single source for the HTML "
            f"rendering (Q139 rule 1)")

    body = blocks[0].strip()
    # the clause set must match EXACTLY (rule 3b). Missing a clause fails;
    # adding one is allowed only by adding it to the canonical file first, which
    # is what keeps the canonical set the contract rather than the translation.
    want = _disclaimer_clauses(
        re.findall(r"^```html\n(.*?)^```", canonical, re.DOTALL | re.MULTILINE)[0])
    got = _disclaimer_clauses(body)
    if set(got) != set(want):
        missing, extra = sorted(set(want) - set(got)), sorted(set(got) - set(want))
        raise ValueError(
            f"{src_path.name} does not carry the canonical clause set: "
            f"missing {missing}, extra {extra}. Q139 rule 3b — the CLAUSE SET is "
            f"the contract and the wording is the workspace's, so a rendering that "
            f"drops the liability clause is not a translation, it is a different "
            f"disclaimer.")
    return body


def _disclaimer_section(total: int, thesis: Path, facts: dict,
                        generated_at: str, slug: str, thesis_num: str) -> str:
    """The template-owned trailing disclaimer page, numbered last and chromed.

    Position it in `build_html` *after* the TOC is computed: it is a legal tail,
    not a chapter, so it stays out of the contents list (disclaimer.md, Placement).
    Q139 rule 3: the clause set is the contract, the wording is not — a workspace
    declaring another language swaps this file, not this code."""
    workspace = thesis.parent.parent.name if thesis.parent.name == "theses" \
        else thesis.parent.name
    body = (_disclaimer_body(thesis)
            .replace("[WORKSPACE]", _html.escape(workspace))
            .replace("[AS_OF]", _html.escape(str(facts.get("as_of") or "—")))
            .replace("[GENERATED]", _html.escape(generated_at)))
    unfilled = sorted(set(_UNFILLED_RE.findall(body)))
    if unfilled:
        raise ValueError(
            f"disclaimer has unfilled placeholders {unfilled} — placeholders are "
            f"filled, never shipped (Q139 rule 2, same rule as Q108)")
    return _inject_page_chrome(
        f'<section class="page disclaimer" data-report-page="{total}">'
        f'{body}</section>', total, slug, thesis_num)


def _toc_entries(content: str) -> list[tuple[int, str]]:
    """First h1/h2 heading text of each renumbered page → TOC entries."""
    entries: list[tuple[int, str]] = []
    for m in re.finditer(r'<section\b[^>]*data-report-page="(\d+)"[^>]*>(.*?)</section>',
                         content, re.DOTALL):
        h = re.search(r"<h[12][^>]*>(.*?)</h[12]>", m.group(2), re.DOTALL)
        if h:
            title = re.sub(r"<[^>]+>", "", h.group(1)).strip()
            if title:
                entries.append((int(m.group(1)), title))
    return entries


def build_html(thesis: Path, pages_html: str, shash: str, generated_at: str,
               *, font_tier: int = 0, draft: bool = False,
               overflow_check: str = "unknown") -> str:
    """Template + cover fill + page injection + chrome + pins. Deterministic
    except the generated_at output metadata (never a pin)."""
    facts = _header_facts(thesis)
    esc = _html.escape
    universe = " · ".join(f"{t} {w}".strip() for t, w in facts["universe"]) or "—"
    thesis_num = thesis.name.split("-", 1)[0]
    slug = thesis.name.upper()
    # v0.3.0: running sheet head/foot + page marks on every content page.
    # Q139: total = cover + authored pages + the template-owned disclaimer tail,
    # so the tail is page-numbered and overflow-checked like any other page.
    authored = len(re.findall(r'data-report-page="(\d+)"', pages_html))
    total = 2 + authored
    pages_html = _inject_page_chrome(pages_html, total, slug, thesis_num)

    html = TEMPLATE.read_text(encoding="utf-8")
    if PAGES_COMMENT not in html:
        raise ValueError(f"template {TEMPLATE} is missing the PAGES injection point")
    html = html.replace("<title>Thesis Report</title>",
                        f"<title>{esc(facts['name'])} — agentii Thesis Report</title>", 1)
    html = html.replace('<h1 id="cover-title">Thesis Report</h1>',
                        f'<h1 id="cover-title">{esc(facts["name"])}</h1>', 1)
    html = html.replace('<span id="cover-kicker" class="sec-kicker"></span>',
                        f'<span id="cover-kicker" class="sec-kicker">'
                        f'AGENTII THESIS REPORT · {esc(thesis_num)}</span>', 1)
    html = html.replace("__SLUG__", esc(slug), 1)
    html = html.replace("__TOTAL__", f"{total:02d}", 1)
    html = html.replace('<p id="cover-claim" class="claim"></p>',
                        f'<p id="cover-claim" class="claim">{esc(facts["claim"] or "—")}</p>', 1)
    html = html.replace('<td id="cover-pin"></td>',
                        f'<td id="cover-pin">{esc(facts["pin"] or "—")}</td>', 1)
    html = html.replace('<td id="cover-as-of"></td>',
                        f'<td id="cover-as-of">{esc(facts["as_of"] or "—")}</td>', 1)
    # T091/FR-065: the scored readability tier, on the cover beside the pins, with the regression
    # explanation appended where one was required. Read here rather than passed in, so the cover and
    # the gate read the same file through the same function — see `_readability`.
    rd = _readability(thesis)
    cover_rd = esc(rd["cover"])
    if rd["explanation"]:
        cover_rd += f' <span class="rd-note">{esc(rd["explanation"])}</span>'
    html = html.replace('<td id="cover-readability"></td>',
                        f'<td id="cover-readability">{cover_rd}</td>', 1)
    html = html.replace('<td id="cover-universe"></td>',
                        f'<td id="cover-universe">{esc(universe)}</td>', 1)
    html = html.replace('<td id="cover-generated"></td>',
                        f'<td id="cover-generated">{esc(generated_at)}</td>', 1)
    toc_items = "".join(f'<li><a href="#page-{n}">{esc(t)}</a></li>'
                        for n, t in _toc_entries(pages_html))
    html = html.replace('<div id="cover-toc" class="toc"></div>',
                        f'<div id="cover-toc" class="toc"><h2>Contents</h2><ol>{toc_items}</ol></div>', 1)
    # Appended after the TOC above was computed from the authored pages only: the
    # disclaimer is a legal tail, not a chapter.
    pages_html += _disclaimer_section(total, thesis, facts, generated_at, slug, thesis_num)
    html = html.replace(PAGES_COMMENT, pages_html, 1)

    # Q99/Q105: record WHICH overflow check ran. The ±5% estimator passed five
    # genuinely overflowing pages, so a report must never imply a precision it
    # did not have — "approximate" is the estimator, "engine" is headless Chrome.
    body_attrs = (f'<body data-sources-hash="{shash}" '
                  f'data-overflow-check="{overflow_check}" '
                  f'data-template-version="{TEMPLATE_VERSION}"')
    if font_tier > 0:
        body_attrs += (f' data-font-tier="{font_tier}" '
                       f'style="font-size:{check_page_overflow.FONT_TIERS[font_tier]}pt"')
    body_attrs += ">"
    if draft:
        body_attrs += ('<div class="draft-banner">DRAFT — page_overflow_unresolved '
                       'at all font tiers; markdown fallback: thesis-report.md</div>')
    html = html.replace("<body>", body_attrs, 1)
    return html


def _print_heights(html_text: str, tier: int, over: list[int]) -> None:
    base = check_page_overflow.FONT_TIERS[tier]
    limit = (check_page_overflow.LETTER_HEIGHT_PX * check_page_overflow.TOLERANCE
             * (check_page_overflow.FONT_TIERS[0] / base))
    for page in check_page_overflow.estimate_heights(html_text):
        status = "OVER" if page["index"] + 1 in over else "PASS"
        print(f"page {page['index'] + 1}: {page['height']:.0f}px / {limit:.0f}px — {status}")


def _write_generated(path: Path, text: str, producer: str = "synthesize_report") -> None:
    """Write a GENERATED artifact, replacing any prior copy — and VERIFY the verdict.

    Measured 2026-09-19, thesis 003. Three consecutive `assemble` runs left
    `thesis-report.html` byte-identical to a version **three content edits old**,
    while every one of them printed `OK /…/thesis-report.html`. The render step
    then produced pixels from that stale file, and the author's visual pass was
    reviewing a document nobody had written.

    The cause is not in this file: `write_boundary.write` applies Q127's fail-safe,
    and for a document that declares no `writer:` that fail-safe is APPEND-ONLY.
    An HTML report has no frontmatter to declare one in, so the SECOND write is
    always refused — and this function's caller discarded the return value, so a
    refusal was indistinguishable from a success.

    Two corrections, and both are needed:
      1. the stale copy is UNLINKED first. The assembler is the sole producer of
         these paths (`thesis-report.html`, its markdown fallback) — they are
         regenerated wholesale from `content.html` on every run, so a second write
         is not a second writer. This is the semantic Q127 was protecting, not an
         exemption from it; the guard still applies to every authored document.
      2. the verdict is CHECKED. A refusal now raises instead of printing OK.
    """
    if path.exists():
        path.unlink()
    res = write_boundary.write(path, text, producer=producer)
    if getattr(res, "verdict", "written") == "refused":
        raise ValueError(
            f"write boundary REFUSED {path.name}: "
            + "; ".join(getattr(res, "reasons", []) or ["no reason given"]))


def assemble(thesis: Path, out_path: Path | None = None, *,
             check_only: bool = False) -> tuple[Path | None, str, bool]:
    """Validate the LLM-authored content, assemble, gate, deliver (or degrade).

    Returns (report_path, sources_hash, degraded). Raises ContentMissingError
    when report/content.html is absent and ValueError on contract violations.
    check_only=True prints per-page heights at every tier and writes nothing —
    the LLM's iteration loop for letter-fit."""
    thesis = Path(thesis)
    content_path = thesis / "report" / "content.html"
    if not content_path.is_file():
        raise ContentMissingError(
            "report/content.html not found. The synthesize workflow is "
            "pack → author → assemble:\n"
            "  1. python3 scripts/synthesize_report.py pack --thesis <thesis-dir>\n"
            "  2. author report/content.html from report-input.md "
            "(contract in skills/agentii/synthesize/SKILL.md)\n"
            "  3. python3 scripts/synthesize_report.py assemble --thesis <thesis-dir>")
    # T131 (Q94): the outline gate runs FIRST, before the content is even read.
    # Order matters: Q94 says the outline is finalised BEFORE any page is
    # authored, so refusing here refuses the premise, not just the output.
    outline_problems = gate_outline(thesis)
    if outline_problems:
        raise ValueError("outline gate failed (Q94/T131):\n- "
                         + "\n- ".join(outline_problems))

    content = content_path.read_text(encoding="utf-8")
    pack_txt = pack_text(thesis)
    problems = _validate_content(content, pack_txt)
    # T132/T133/T134 — the in-document gates. They live here because Q115's
    # argument is that the report is a NEW document assembled AFTER every other
    # gate has run; nothing upstream can see a document contradicting itself.
    problems += _gate_page_shape(content)
    problems += _gate_page_argument(content)   # T135 (Q95 contracts 1, 2)
    problems += _gate_charts(content)
    problems += _gate_self_consistency(content, _load_metrics(thesis))
    # T091/FR-065 — the ONE thing in the scored tier that can refuse. The score itself never does: it is
    # not compared to any threshold, and a low score assembles exactly like a high one. What is refused
    # is a REGRESSION WITH NO EXPLANATION, because "MUST be explained in the deliverable" with no
    # consequence is the field-that-triggers-nothing defect FR-040 forbids — and because the first
    # version of FR-065 was that defect, introduced in the act of fixing another one.
    problems += _readability(thesis)["problems"]
    if problems:
        raise ValueError("content.html validation failed:\n- " + "\n- ".join(problems))
    for advisory in _quality_advisories(content):
        print(f"advisory: {advisory}", file=sys.stderr)

    pages_html = _renumber_pages(render_chart_tokens(content, thesis))
    shash = sources_hash(thesis)
    report_path = out_path or (thesis / "thesis-report.html")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    mode = "engine" if check_page_overflow.engine_available() else "approximate"
    for tier in range(len(check_page_overflow.FONT_TIERS)):
        html = build_html(thesis, pages_html, shash, generated_at, font_tier=tier,
                          overflow_check=mode)
        over, used = check_page_overflow.check_with_mode(html, font_tier=tier)
        if used != mode:
            # Chrome died between the probe and the run. Rebuild once with the
            # mode that actually ran, so the artifact cannot claim the engine.
            mode = used
            html = build_html(thesis, pages_html, shash, generated_at,
                              font_tier=tier, overflow_check=mode)
        if check_only:
            _print_heights(html, tier, over)
            if not over:
                return None, shash, False
            continue
        if not over:
            _write_generated(report_path, html)
            return report_path, shash, False

    # Q47 failure semantics: markdown fallback + HTML draft with a banner.
    if not check_only:
        facts = _header_facts(thesis)
        md_path = report_path.with_suffix(".md")
        _write_generated(
            md_path,
            f"# {facts['name']} — Markdown Report "
            f"(HTML overflow gate unresolved)\n\n{pack_txt}")
        html = build_html(thesis, pages_html, shash, generated_at,
                          font_tier=len(check_page_overflow.FONT_TIERS) - 1,
                          draft=True, overflow_check=mode)
        _write_generated(report_path, html)
    return report_path, shash, True


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="synthesize_report.py",
        description="Thesis HTML synthesis (Q49/Q50): pack → (LLM authors "
                    "report/content.html) → assemble")
    sub = p.add_subparsers(dest="cmd", required=True)
    pk = sub.add_parser("pack", help="bundle all source markdown into report-input.md")
    pk.add_argument("--thesis", required=True, help="theses/{nnn}-{slug}/ directory")
    pk.add_argument("--limit-body", type=int, default=None,
                    help="truncate each artifact body at N chars (paragraph boundary)")
    asm = sub.add_parser("assemble", help="validate + assemble + gate → thesis-report.html")
    asm.add_argument("--thesis", required=True)
    asm.add_argument("--out", default=None, help="override output path")
    asm.add_argument("--check-only", action="store_true",
                     help="print per-page heights, write nothing (LLM fit loop)")
    args = p.parse_args(argv)
    thesis = Path(args.thesis)
    try:
        if args.cmd == "pack":
            out, shash = pack(thesis, body_limit=args.limit_body)
            print(f"OK {out} sources_hash={shash}")
            return 0
        path, shash, degraded = assemble(
            thesis, out_path=Path(args.out) if args.out else None,
            check_only=args.check_only)
        if args.check_only:
            print(f"{'DEGRADED' if degraded else 'OK'} (check-only — nothing written) "
                  f"sources_hash={shash}")
        else:
            print(f"{'DEGRADED' if degraded else 'OK'} {path} sources_hash={shash}")
        return 0
    except ContentMissingError as exc:
        print(exc, file=sys.stderr)
        return 2
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
