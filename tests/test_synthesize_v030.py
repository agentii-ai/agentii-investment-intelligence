"""v0.3.0 — metrics.json extraction, page chrome injection, quality advisories,
and the render_report.py visual-QA loop (Chrome/poppler smoke, skip-if-absent)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_page_overflow  # noqa: E402
import render_report  # noqa: E402
import synthesize_report  # noqa: E402

HAVE_TOOLS = (
    render_report.chrome_bin().is_file()
    and shutil.which("pdfinfo") is not None
    and shutil.which("pdftoppm") is not None)


def _write_artifact(thesis: Path, ticker: str, name: str, extra: str = "",
                    key_metrics: str = "  revenue_fy2026_usd_m: 215938\n") -> None:
    (thesis / "artifacts" / ticker).mkdir(parents=True, exist_ok=True)
    (thesis / "artifacts" / ticker / name).write_text(f"""---
assumption_pin: 1
corpus_version: "x"
as_of: 2026-09-10
constitution_pin: 1.3.0
skill_pin: "x:y"
mode: default
data_class: slow
key_metrics:
{key_metrics}conclusions:
  - "First conclusion."
facts_count: 10
deducted_count: 3
views_count: 2
citation_count: 8
{extra}---

# {ticker} body — cited at https://agentii.ai/v/{ticker}/sec169/37
""")


def test_metrics_deterministic_and_lenient(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    (thesis / "_cross").mkdir(parents=True)
    (thesis / "_cross" / "x_synthesis.md").write_text("""---
pillar_verdicts:
  PIL-1: indeterminate   # untestable
capability_timeline:
  gpt_3_5_moment_estimate: "2027-Q4 to 2028-Q2"
  confidence: medium
---

# Synthesis
""")
    _write_artifact(thesis, "TSLA", "a.md",
                    key_metrics="  FY2025_total_revenues_usd_bn: 94.827\n"
                                '  capex_2026_guidance_usd_b: ">20"\n')
    _write_artifact(thesis, "TSLA", "b.md",
                    key_metrics="  fy2025_total_revenues_usd_bn: 95.0\n"
                                '  range_metric_usd: "900-3700"\n')
    # one file missing the citations key entirely
    _write_artifact(thesis, "SPCX", "c.md",
                    key_metrics='  share_metric_pct: "21/17/16"\n'
                                "  ai_share_h1_capex_pct: 82.7\n")

    out, shash = synthesize_report.pack(thesis)
    metrics_path = thesis / "report" / "metrics.json"
    assert metrics_path.is_file()
    text = metrics_path.read_text(encoding="utf-8")
    assert synthesize_report.pack(thesis)[0] == out
    assert metrics_path.read_text(encoding="utf-8") == text  # byte-deterministic

    doc = json.loads(text)
    assert doc["pack_version"] == "2.0"
    tsla = doc["tickers"]["TSLA"]
    assert "fy2025_total_revenues_usd_bn" in tsla["key_metrics"]      # lowercased
    assert tsla["key_metrics"]["fy2025_total_revenues_usd_bn"] == 94.827  # first file wins
    assert tsla["key_metrics"]["capex_2026_guidance_usd_b"] == ">20"       # string verbatim
    assert tsla["key_metrics"]["range_metric_usd"] == "900-3700"
    assert tsla["metric_sources"]["fy2025_total_revenues_usd_bn"] == \
        [p for p in tsla["metric_sources"]["fy2025_total_revenues_usd_bn"]
         if p.startswith("artifacts/TSLA/")]
    assert len(tsla["metric_sources"]["fy2025_total_revenues_usd_bn"]) == 2  # both files listed
    spcx = doc["tickers"]["SPCX"]
    assert spcx["key_metrics"]["share_metric_pct"] == "21/17/16"
    assert spcx["counts"]["facts_count"] == 10 and spcx["counts"]["citation_count"] == 8
    assert doc["synthesis"]["pillar_verdicts"]["PIL-1"] == "indeterminate"
    assert doc["synthesis"]["capability_timeline"]["confidence"] == "medium"
    assert len(shash) == 16


def test_template_comments_never_nest():
    """A nested comment marker inside the template's header comment ends it
    early and leaks prose into the body (pushed the cover past the letter page
    height in Chrome — PDF got 4 pages for 3 sections). Comments must never
    nest; the PAGES injection point is the only standalone marker."""
    import re

    tpl = (ROOT / "plugins" / "vertical-plugins" / "scenarios"
           / "templates" / "thesis-report.html").read_text(encoding="utf-8")
    events = sorted([(m.start(), +1) for m in re.finditer(r"<!--", tpl)]
                    + [(m.start(), -1) for m in re.finditer(r"-->", tpl)])
    depth = 0
    for _pos, delta in events:
        depth += delta
        assert 0 <= depth <= 1, f"comment nesting at {_pos} (depth {depth})"


def test_metrics_empty_thesis_is_REFUSED(tmp_path):
    """Q97(1). This test used to be `test_metrics_empty_thesis` and assert that a
    thesis with no artifacts produced an empty metrics.json AND a success exit.
    That IS the defect: pack reported OK over a bundle with no series, so the
    report rendered with no KPI tiles and nothing said why. Measured live on
    agentii-space-tech-SPCX/theses/001-technology-baseline (44 artifacts, 0 KPIs).
    """
    thesis = tmp_path / "theses" / "002-empty"
    with pytest.raises(synthesize_report.MetricsMissingError) as exc:
        synthesize_report.pack(thesis)
    msg = str(exc.value)
    assert "no series" in msg
    assert "FR-090" in msg and "key_metrics" in msg
    # refused BEFORE any write — no half-produced bundle left behind
    assert not (thesis / "report" / "metrics.json").exists()


def test_quality_advisories_non_blocking(tmp_path, capsys):
    thesis = tmp_path / "theses" / "001-x"
    _write_artifact(thesis, "NVDA", "a.md")
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    _write_outline(thesis)
    # a valid but quality-poor fragment: no tiles, no badges, no timeline, no kicker
    (thesis / "report" / "content.html").write_text("""
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
</section>
""")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    err = capsys.readouterr().err
    assert "advisory:" in err and ".stat-row" in err


def test_inject_page_chrome(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_artifact(thesis, "NVDA", "a.md")
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    _write_outline(thesis)
    (thesis / "report" / "content.html").write_text("""
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
<div class="stat-row">
<div class="stat"><div class="num">24</div><div class="lbl">Artifacts</div><div class="sub">six names</div></div>
</div>
</section>
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap. This implies the mix shift is structural rather than timing, which argues for holding the position at its cap rather than stepping down into the print.</p>
<div class="timeline"><div class="tl-item"><span class="tl-phase">2027-Q4</span></div></div>
</section>
""")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    html = path.read_text(encoding="utf-8")
    # cover + 2 content pages + the Q139 disclaimer tail = 4
    assert html.count('class="sheet-head"') == 4
    # 4 pages, not 3: cover + 2 authored + the Q139 disclaimer tail page.
    assert html.count('class="reg reg-tl"') == 4
    assert html.count('class="print-center no-print"') == 4  # centered print cluster
    assert html.count('class="print-btn"') == 4           # Print / PDF on every page
    assert html.count('onclick="window.print()"') == 4
    assert html.count('class="print-hint"') == 4          # dialog guidance on every page
    # total is 4 now (the Q139 disclaimer is numbered last); page 2 of 4.
    assert "02 / 04" in html                              # page marks
    assert "04 / 04" in html                              # the disclaimer is the last page
    assert "__TOTAL__" not in html and "__SLUG__" not in html
    assert "AGENTII THESIS REPORT · 001" in html          # cover kicker
    assert check_page_overflow.check(html) == []


def test_render_tool_missing(monkeypatch, tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    (thesis / "thesis-report.html").write_text(
        '<section class="page" data-report-page="1"></section>')
    monkeypatch.setattr(render_report, "chrome_bin", lambda: Path("/nonexistent/chrome"))
    monkeypatch.setattr(shutil, "which", lambda _x: None)
    with pytest.raises(render_report.RenderError) as exc:
        render_report.render(thesis)
    assert exc.value.code == 3 and "poppler" in str(exc.value)


def test_render_count_mismatch(tmp_path):
    # report missing → exit 1; broken numbering → exit 2 (no tools required)
    thesis = tmp_path / "theses" / "001-x"
    with pytest.raises(render_report.RenderError) as exc:
        render_report.render(thesis)
    assert exc.value.code == 1
    thesis.mkdir(parents=True)
    (thesis / "thesis-report.html").write_text(
        '<section class="page" data-report-page="1"></section>'
        '<section class="page" data-report-page="3"></section>')
    with pytest.raises(render_report.RenderError) as exc:
        render_report.render(thesis)
    assert exc.value.code == 2


@pytest.mark.skipif(not HAVE_TOOLS, reason="Chrome/poppler absent")
def test_render_smoke(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_artifact(thesis, "NVDA", "a.md")
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    _write_outline(thesis)
    (thesis / "report" / "content.html").write_text("""
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
<div class="stat-row">
<div class="stat"><div class="num">24</div><div class="lbl">Artifacts</div></div>
</div>
</section>
<section class="page">
<h2>Revenue mix moved 6 points toward the higher-margin line</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
<table>
<thead><tr><th>Ticker</th><th>Value</th></tr></thead>
<tbody><tr><td>NVDA</td><td>$215.9B <a href="https://agentii.ai/v/NVDA/sec169/37">sec169/37</a></td></tr></tbody>
</table>
</section>
""")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    before = path.read_bytes()
    out_dir = tmp_path / "pages"
    manifest = render_report.render(thesis, out=out_dir, dpi=72, verify=True)
    assert manifest["page_count"] == 4        # cover + 2 authored + disclaimer (Q139)
    assert len(list(out_dir.glob("page-*.png"))) == 4
    assert (out_dir / "manifest.json").is_file()
    w = manifest["width"]
    assert abs(w - round(8.5 * 72)) <= 1      # letter width at requested dpi
    assert path.read_bytes() == before        # render is strictly read-only on the report


def _write_outline(thesis: Path) -> None:
    """Q94/T131: `assemble` refuses without `report/outline.md`.

    Added 2026-09-18 — the gate is correct and these fixtures were what had to
    change. They went pack -> content.html directly, which is the behaviour Q94
    measured: the render-and-optimize loop was proven for LAYOUT and had no
    counterpart for the ARGUMENT, so structure was never chosen, only emerged.
    The fixture's arguments point at a conclusion rather than restating data,
    because Q94 requires that too."""
    (thesis / "report" / "outline.md").write_text(
        "# Outline\n\n"
        "## Key arguments\n"
        "- The revenue mix implies margin holds, which argues for holding size at "
        "the cap rather than stepping down.\n\n"
        "## Evidence\n"
        "- pack source sec169/37\n\n"
        "## Page plan\n"
        "- page 1: executive summary\n\n"
        "## Story line\n"
        "The reader moves from the margin claim to its evidence and ends at sizing.\n",
        encoding="utf-8")



# ── S10: the report gates (T131–T134; Q94/Q115/Q118) ────────────────────────
# Each is proved to FIRE, because a gate that cannot fail is this spec's
# recurring defect and a test that only asserts the happy path cannot tell the
# difference between a working gate and an inert one.

def _with_content(thesis, pages):
    (thesis / "report" / "content.html").write_text(pages, encoding="utf-8")


def test_outline_gate_refuses_authoring_without_an_outline(tmp_path):
    """T131/Q94. Measured basis: the render-and-optimize loop was proven for
    LAYOUT and had no counterpart for the ARGUMENT, so structure was never
    chosen, only emerged."""
    thesis = tmp_path / "theses" / "001-x"
    _write_artifact(thesis, "NVDA", "a.md")
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    _with_content(thesis, '<section class="page"><h2>E</h2><p>' + "x" * 200 + " This implies the mix shift is structural rather than timing, which argues for holding the position at its cap rather than stepping down into the print.</p></section>")
    try:
        synthesize_report.assemble(thesis)
        raise AssertionError("assemble should have refused without an outline")
    except ValueError as e:
        assert "outline" in str(e).lower(), e


def test_outline_gate_requires_all_four_elements_and_a_conclusion(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    (thesis / "report" / "outline.md").write_text(
        "# Outline\n\n## Key arguments\n- Revenue was $215.9B.\n",
        encoding="utf-8")
    problems = synthesize_report.gate_outline(thesis)
    assert any("evidence" in p for p in problems), problems
    assert any("page" in p for p in problems), problems
    assert any("story" in p for p in problems), problems
    # …and an argument that only restates data is not an argument
    assert any("conclusion" in p for p in problems), problems


def test_page_shape_gate_fires_on_a_table_only_page():
    """T132/Q115: a table states no claim."""
    pages = ('<section class="page"><h2>Revenue mix moved 6 points toward the higher-margin line</h2><table>'
             '<thead><tr><th>T</th></tr></thead><tbody><tr><td>1</td></tr></tbody>'
             '</table></section>')
    problems = synthesize_report._gate_page_shape(pages)
    assert problems and "only a table" in problems[0]


def test_page_shape_gate_ignores_a_page_with_no_table():
    """The rule is 'only a table + caption' — a short page with no table is a
    different question, and the first version of this gate over-reached."""
    pages = '<section class="page"><h2>E</h2><p>Short. This implies the mix shift is structural rather than timing, which argues for holding the position at its cap rather than stepping down into the print.</p></section>'
    assert synthesize_report._gate_page_shape(pages) == []


def test_chart_gate_rejects_a_kind_name_as_alt():
    """T133/Q118, the measured defect: every chart in three reports carried
    `alt="kpi_trend"` — the KIND's name — leaving the figure with no textual
    content in a print-first PDF."""
    pages = ('<figure><img src="data:image/svg+xml;base64,AA" alt="kpi_trend">'
             '<figcaption>Mass to orbit by quarter, metric tons, from 10-Q p37.</figcaption>'
             '</figure>')
    problems = synthesize_report._gate_charts(pages)
    assert any("KIND" in p for p in problems), problems


def test_chart_gate_requires_units_in_the_caption():
    pages = ('<figure><img src="data:image/svg+xml;base64,AA" alt="Mass to orbit over time">'
             '<figcaption>Mass delivered each quarter.</figcaption></figure>')
    problems = synthesize_report._gate_charts(pages)
    assert any("UNIT" in p for p in problems), problems


def test_chart_gate_passes_a_caption_that_names_what_units_and_source():
    """The standard already existed in the corpus — SPCX's caption disclosed its
    derivation. Nothing was invented."""
    pages = ('<figure><img src="data:image/svg+xml;base64,AA" '
             'alt="Mass to orbit per quarter in metric tons">'
             '<figcaption>Mass to orbit by quarter, metric tons. Q2 as filed; '
             'Q1 derived as the half-year total less Q2 — 1,102 − 652 = 450.</figcaption>'
             '</figure>')
    assert synthesize_report._gate_charts(pages) == []


def test_self_consistency_gate_fires_on_two_values_for_one_metric():
    """T134/Q115: measured — a report contradicted itself by 15.3 pp. The cost is
    specific to reports: a reader who meets one metric at two values stops
    believing the rest, including the correct ones."""
    content = (
        '<div data-metric="gross_margin" data-period="Q2-2026" data-value="0.62"></div>'
        '<div data-metric="gross_margin" data-period="Q2-2026" data-value="0.47"></div>')
    problems = synthesize_report._gate_self_consistency(content, {})
    assert problems and "contradicts itself" in problems[0]


def test_self_consistency_gate_fires_when_a_headline_untraceable_to_the_pack():
    content = '<div data-metric="revenue" data-period="Q2-2026" data-value="215.9"></div>'
    problems = synthesize_report._gate_self_consistency(
        content, {"key_metrics": {"revenue": "$240.1B"}})
    assert problems and "metrics.json" in problems[0]


def test_self_consistency_gate_passes_when_the_document_agrees_with_itself():
    content = (
        '<div data-metric="revenue" data-period="Q2-2026" data-value="215.9"></div>'
        '<div data-metric="revenue" data-period="Q1-2026" data-value="198.4"></div>')
    assert synthesize_report._gate_self_consistency(
        content, {"key_metrics": {"revenue": "$215.9B"}}) == []


# ── T138: language follows the workspace (Q126) ─────────────────────────────

_ZH = '''```html
<section class="disclaimer">
  <h3>免责声明</h3>
  <p data-clause="not-advice">本文档是研究分析，不构成投资建议。</p>
  <p data-clause="sources-fallible">本文基于文内引用的来源，可能有误。</p>
  <p data-clause="hypotheses-not-conclusions">本文含假设而非既定结论。</p>
  <p data-clause="own-due-independence-typo">责任由读者自负。</p>
</section>
```'''


def test_a_workspace_language_requires_its_own_rendering(tmp_path):
    """Q126: the clause set is the contract, the wording is the workspace's. But
    the rendering must EXIST — shipping the English text into a workspace that
    declared another language is the failure this prevents."""
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    (tmp_path / "style.md").write_text("language: zh\n", encoding="utf-8")
    try:
        synthesize_report._disclaimer_body(thesis)
        raise AssertionError("should have refused: declared zh, supplied nothing")
    except ValueError as e:
        assert "disclaimer.zh.md" in str(e), e


def test_the_clause_set_is_checked_against_the_canonical_one(tmp_path):
    """Rule 3b. Without stable clause ids, 'the clause set is the contract' cannot
    be enforced — a translation could drop the liability clause and still read as
    compliant."""
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    (tmp_path / "style.md").write_text("language: zh\n", encoding="utf-8")
    # drops own-due-diligence, invents own-due-independence-typo
    (tmp_path / "disclaimer.zh.md").write_text(_ZH, encoding="utf-8")
    try:
        synthesize_report._disclaimer_body(thesis)
        raise AssertionError("should have refused: clause set differs")
    except ValueError as e:
        msg = str(e)
        assert "own-due-diligence" in msg and "own-due-independence-typo" in msg, msg


def test_a_complete_translation_is_accepted(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    (tmp_path / "style.md").write_text("language: zh\n", encoding="utf-8")
    (tmp_path / "disclaimer.zh.md").write_text(
        _ZH.replace('data-clause="own-due-independence-typo"',
                    'data-clause="own-due-diligence"'), encoding="utf-8")
    body = synthesize_report._disclaimer_body(thesis)
    assert "免责声明" in body
    assert set(synthesize_report._disclaimer_clauses(body)) == {
        "not-advice", "sources-fallible", "hypotheses-not-conclusions",
        "own-due-diligence"}


def test_no_declared_language_uses_the_canonical_english(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    thesis.mkdir(parents=True)
    body = synthesize_report._disclaimer_body(thesis)
    assert "not investment advice" in body


# ── T135: Q95's page-level argument contracts 1 and 2 ───────────────────────

def test_a_label_heading_fails():
    """Q95 contract 1. The measured reports already write claim headings, so this
    is a KEEP — the gate exists to stop the practice regressing, which is the only
    way a satisfied constraint stays satisfied."""
    for label in ("Evidence", "NVDA", "Summary", "Timeline"):
        pages = (f'<section class="page"><h2>{label}</h2>'
                 + '<p>This implies the mix shift is structural, which argues for '
                   'holding the position at its cap rather than stepping down.</p>'
                 + '</section>')
        problems = synthesize_report._gate_page_argument(pages)
        assert any("LABEL" in p for p in problems), (label, problems)


def test_a_claim_heading_passes():
    pages = ('<section class="page">'
             '<h2>Launch is 12.3% of revenue at the launch company</h2>'
             '<p>This implies the mix shift is structural rather than a timing effect, '
             'which argues for holding the position at its cap rather than '
             'stepping down into the print. The margin delta is explained by '
             'mix alone, so the conclusion does not hinge on the one-off.</p>'
             '</section>')
    assert synthesize_report._gate_page_argument(pages) == []


def test_a_page_whose_prose_never_lands_on_an_implication_fails():
    """Q95 contract 2's measured counter-example: 'a badge census is not an
    argument' — the page reported how many facts it contained, not what they mean.

    The prose is deliberately longer than the word-count threshold, so this test
    reaches the IMPLICATION check rather than tripping the count first. When the
    threshold moved under it, this test silently started asserting the wrong
    thing — it still failed, for a different reason."""
    pages = ('<section class="page">'
             '<h2>Revenue mix moved 6 points toward the higher-margin line</h2>'
             + '<p>' + "The page contains fourteen facts and two badges. " * 4 + '</p>'
             + '</section>')
    problems = synthesize_report._gate_page_argument(pages)
    assert any("investment implication" in p for p in problems), problems


def test_a_page_with_too_little_prose_fails():
    pages = ('<section class="page"><h2>Margin holds above the peer set</h2>'
             '<p>Revenue rose, which means margin held.</p></section>')
    problems = synthesize_report._gate_page_argument(pages)
    assert any("explanatory prose" in p for p in problems), problems


def test_a_page_of_bare_figures_is_caught_where_the_four_word_proxy_could_not_see_it():
    """FR-067 / T089: ONE keyword used to certify a PAGE of bare figures.

    The strengthening, and the fixture is shaped to isolate it. Twelve figures with no reading, plus a
    single sentence carrying `implies`. The keyword proxy was satisfied by that one sentence and
    reported nothing, while the page was — in the reported symptom's words — a heap of data. The corpus
    floor measures BREADTH, so it sees the eleven bare sentences a presence test cannot.
    """
    prose = " ".join(["Revenue rose 12% to $1.2B in the quarter."] * 12
                     + ["This implies the mix shift is structural."])
    pages = f'<section class="page"><h2>Revenue mix moved 6 points</h2><p>{prose}</p></section>'
    problems = synthesize_report._gate_page_argument(pages)
    assert any("interpretive-floor" in p for p in problems), problems


def test_the_implication_requirement_still_stands_where_the_floor_is_clear():
    """A UNION, NOT A REPLACEMENT — the regression this pins.

    Twelve directional sentences clear the floor (direction counts as interpretation, per the corpus:
    `contracts/report-readability.md` §2 row 5) and still never say what any of it means for the
    position, which is Q95 contract 2's requirement. This page was blocked before T089. Replacing the
    token test rather than adding to it would have let it through, so the two checks are kept as two:
    the floor asks whether the figures are read, contract 2 asks whether the prose lands.
    """
    prose = " ".join(["Revenue grew 12% to $1.2B as margin expanded."] * 12)
    pages = f'<section class="page"><h2>Revenue mix moved 6 points</h2><p>{prose}</p></section>'
    problems = synthesize_report._gate_page_argument(pages)
    assert any("investment implication" in p for p in problems), problems


def test_the_limit_of_this_change_is_pinned_rather_than_hidden():
    """What T089 does NOT fix, asserted so the change is not read as more than it is.

    Ten sentences of "Revenue therefore rose 12% to $1.2B" pass BOTH checks: `therefore` is an
    interpretation token, so the ratio is 10/10. That sentence is FR-067's own example of a restatement
    a keyword test cannot separate from a reading — the words are identical — so separating them needs
    `FR-065`'s scored tier, where "the reading is shallow" is sayable at all. What T089 repairs is the
    breadth defect, not the depth one.

    Pinned as a passing expectation on purpose: if a later change makes this page block, that is an
    improvement, and the right response is to update this test and its docstring — not to discover the
    difference as a surprise.
    """
    prose = " ".join(["Revenue therefore rose 12% to $1.2B in the quarter."] * 10)
    pages = f'<section class="page"><h2>Revenue mix moved 6 points</h2><p>{prose}</p></section>'
    assert synthesize_report._gate_page_argument(pages) == []


# ── T090/T091 (FR-065): the scored readability tier's record and its one refusal ──────────────

def _readability_dir(tmp_path, payload):
    (tmp_path / "report").mkdir(parents=True, exist_ok=True)
    if payload is not None:
        (tmp_path / "report" / "readability.json").write_text(
            payload if isinstance(payload, str) else json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_an_unscored_report_records_that_rather_than_guessing(tmp_path):
    """Absent is a STATE, not an error. A thesis whose report predates this tier still assembles."""
    rd = synthesize_report._readability(_readability_dir(tmp_path, None))
    assert rd["score"] is None and rd["problems"] == []
    assert "not scored" in rd["cover"]


def test_a_recorded_score_lands_on_the_cover(tmp_path):
    rd = synthesize_report._readability(_readability_dir(tmp_path, {"score": 21, "previous": 18}))
    assert (rd["score"], rd["problems"]) == (21, [])
    assert rd["cover"] == "21/25"


def test_a_score_outside_the_rubric_range_is_refused(tmp_path):
    """Five criteria on 1–5, so 26 is not a harsh score — it is not a score."""
    for bad in (0, 26, -1, "high", 4.5):
        rd = synthesize_report._readability(_readability_dir(tmp_path, {"score": bad}))
        assert rd["problems"] and "1–25" in rd["problems"][0], bad


def test_a_dropped_score_must_be_explained(tmp_path):
    """FR-065's consequence, and the ONLY thing in this tier that can refuse anything.

    The score itself is never compared to a threshold — a low score assembles exactly like a high one,
    because the trigger is a regression rather than an absolute. What is refused is a regression with
    no explanation, which would leave the score recorded without consequence.
    """
    rd = synthesize_report._readability(_readability_dir(tmp_path, {"score": 12, "previous": 20}))
    assert rd["problems"], "a drop with no explanation must be refused"
    assert "MUST be explained" in rd["problems"][0]
    assert "never refused for being low" in rd["problems"][0]


def test_a_low_score_with_no_previous_release_is_not_a_regression(tmp_path):
    """The first report sets its own baseline, so there is nothing to regress from."""
    assert synthesize_report._readability(
        _readability_dir(tmp_path, {"score": 5})).get("problems") == []
    assert synthesize_report._readability(
        _readability_dir(tmp_path, {"score": 5, "previous": None})).get("problems") == []


def test_an_explained_drop_is_accepted_and_the_explanation_is_carried(tmp_path):
    rd = synthesize_report._readability(_readability_dir(tmp_path, {
        "score": 14, "previous": 19,
        "explanation": "The launch-timing slide was cut for length, which cost the scenario criterion.",
    }))
    assert rd["problems"] == []
    assert "launch-timing" in rd["explanation"]


def test_malformed_readability_json_is_reported_not_ignored(tmp_path):
    """A record that cannot be read must not read as "not scored" — that is the silent-empty defect."""
    for bad in ("{not json", "[1,2,3]", '"a string"'):
        rd = synthesize_report._readability(_readability_dir(tmp_path, bad))
        assert rd["problems"], bad


def test_the_template_carries_the_cover_anchor_the_assembler_fills(tmp_path):
    """The guard against a SILENT no-op.

    `build_html` fills the row with `html.replace(anchor, …)`, which does nothing at all if the anchor
    is absent — no error, no warning, and every report quietly loses its readability score. So the
    anchor is asserted rather than assumed.
    """
    template = synthesize_report.TEMPLATE.read_text(encoding="utf-8")
    assert '<td id="cover-readability"></td>' in template


_CONTENT_OK = """
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
</section>
"""


def _thesis_for_readability(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_artifact(thesis, "NVDA", "a.md")
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    _write_outline(thesis)
    (thesis / "report" / "content.html").write_text(_CONTENT_OK)
    return thesis


def test_assemble_refuses_an_unexplained_readability_regression(tmp_path):
    """The consequence FR-065 requires, asserted at the ASSEMBLY, not only in the reader.

    This is the one thing the scored tier can refuse, and it is deliberately not a threshold: nothing
    here is compared to a quality bar. What is refused is a DROP with no explanation, because the
    requirement is that a regression is explained in the deliverable — and a rule with no consequence
    is the field-that-triggers-nothing defect FR-040 names, the very defect FR-065's first draft had.
    """
    thesis = _thesis_for_readability(tmp_path)
    (thesis / "report" / "readability.json").write_text(
        json.dumps({"score": 11, "previous": 20}), encoding="utf-8")
    with pytest.raises(ValueError) as exc:
        synthesize_report.assemble(thesis)
    assert "MUST be explained" in str(exc.value)


def test_assemble_accepts_the_same_drop_once_explained_and_puts_it_on_the_cover(tmp_path):
    """And the other half: the fix is an explanation, not a better score."""
    thesis = _thesis_for_readability(tmp_path)
    (thesis / "report" / "readability.json").write_text(json.dumps({
        "score": 11, "previous": 20,
        "explanation": "Two scenario pages were cut for length.",
    }), encoding="utf-8")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    html = path.read_text(encoding="utf-8")
    assert "11/25" in html and "cut for length" in html


def test_assemble_does_not_refuse_a_low_score(tmp_path):
    """A LOW score is not a failure — FR-065 is explicit that there is no absolute threshold.

    The pair to the regression test: 3/25 on a first report assembles cleanly, because the first report
    sets its own baseline and no score was chosen in advance. A gate that refused a low score would be
    the threshold-with-a-warning that `check_disclaimer.py` was before Check 48.
    """
    thesis = _thesis_for_readability(tmp_path)
    (thesis / "report" / "readability.json").write_text(json.dumps({"score": 3}), encoding="utf-8")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded and "3/25" in path.read_text(encoding="utf-8")
