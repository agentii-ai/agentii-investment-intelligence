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
import check_page_overflow  # noqa: E402
import chart_render  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates" / "thesis-report.html"
TEMPLATE_VERSION = "0.3.0"
PACK_VERSION = "2.0"

# Q50: all source markdown artifacts — artifacts, the cross-stock synthesis and
# the snapshot all feed the report, so all of them pin it (v0.1.0 hashed only
# artifacts/). Outputs (report-input.md, report/content.html, thesis-report.*)
# are deliberately excluded — a regenerated report must not self-stale.
SOURCE_GLOBS = ["artifacts/**/*.md", "_cross/**/*.md", "snapshots/**/*.md"]

PAGES_COMMENT = ("<!-- PAGES — assembler injects the LLM-authored "
                 '<section class="page"> sequence -->')


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


def pack(thesis: Path, body_limit: int | None = None) -> tuple[Path, str]:
    thesis = Path(thesis)
    out = thesis / "report-input.md"
    _atomic_write(out, pack_text(thesis, body_limit))
    metrics_path = thesis / "report" / "metrics.json"
    _atomic_write(metrics_path, json.dumps(extract_metrics(thesis), indent=2,
                                           ensure_ascii=False,
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
}
_FORBIDDEN_DOC_RE = re.compile(r"(?i)<\s*!doctype\b|<\s*/?\s*(html|head|body|style|script)\b")
_RESERVED_ID_RE = re.compile(r"^(cover-|stale-bar$)")
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


def render_chart_tokens(content: str) -> str:
    """Replace data-chart token divs with base64 SVG <img> (Q48). The img keeps
    an explicit height so the overflow estimator counts it honestly."""

    def _sub(m: re.Match) -> str:
        kind, spec_json, height = m.group(1), m.group(2), m.group(3)
        svg = chart_render.render_svg(kind, json.loads(spec_json))
        uri = chart_render.to_data_uri(svg)
        return (f'<img src="{uri}" alt="{kind}" height="{height}" '
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
               *, font_tier: int = 0, draft: bool = False) -> str:
    """Template + cover fill + page injection + chrome + pins. Deterministic
    except the generated_at output metadata (never a pin)."""
    facts = _header_facts(thesis)
    esc = _html.escape
    universe = " · ".join(f"{t} {w}".strip() for t, w in facts["universe"]) or "—"
    thesis_num = thesis.name.split("-", 1)[0]
    slug = thesis.name.upper()
    # v0.3.0: running sheet head/foot + page marks on every content page.
    total = 1 + len(re.findall(r'data-report-page="(\d+)"', pages_html))
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
    html = html.replace('<td id="cover-universe"></td>',
                        f'<td id="cover-universe">{esc(universe)}</td>', 1)
    html = html.replace('<td id="cover-generated"></td>',
                        f'<td id="cover-generated">{esc(generated_at)}</td>', 1)
    toc_items = "".join(f'<li><a href="#page-{n}">{esc(t)}</a></li>'
                        for n, t in _toc_entries(pages_html))
    html = html.replace('<div id="cover-toc" class="toc"></div>',
                        f'<div id="cover-toc" class="toc"><h2>Contents</h2><ol>{toc_items}</ol></div>', 1)
    html = html.replace(PAGES_COMMENT, pages_html, 1)

    body_attrs = (f'<body data-sources-hash="{shash}" '
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
    content = content_path.read_text(encoding="utf-8")
    pack_txt = pack_text(thesis)
    problems = _validate_content(content, pack_txt)
    if problems:
        raise ValueError("content.html validation failed:\n- " + "\n- ".join(problems))
    for advisory in _quality_advisories(content):
        print(f"advisory: {advisory}", file=sys.stderr)

    pages_html = _renumber_pages(render_chart_tokens(content))
    shash = sources_hash(thesis)
    report_path = out_path or (thesis / "thesis-report.html")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for tier in range(len(check_page_overflow.FONT_TIERS)):
        html = build_html(thesis, pages_html, shash, generated_at, font_tier=tier)
        over = check_page_overflow.check(html, font_tier=tier)
        if check_only:
            _print_heights(html, tier, over)
            if not over:
                return None, shash, False
            continue
        if not over:
            _atomic_write(report_path, html)
            return report_path, shash, False

    # Q47 failure semantics: markdown fallback + HTML draft with a banner.
    if not check_only:
        facts = _header_facts(thesis)
        md_path = report_path.with_suffix(".md")
        _atomic_write(md_path, f"# {facts['name']} — Markdown Report "
                               f"(HTML overflow gate unresolved)\n\n{pack_txt}")
        html = build_html(thesis, pages_html, shash, generated_at,
                          font_tier=len(check_page_overflow.FONT_TIERS) - 1, draft=True)
        _atomic_write(report_path, html)
    return report_path, shash, True


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)


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
