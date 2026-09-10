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


def test_metrics_empty_thesis(tmp_path):
    thesis = tmp_path / "theses" / "002-empty"
    out, shash = synthesize_report.pack(thesis)
    assert out.is_file()
    doc = json.loads((thesis / "report" / "metrics.json").read_text())
    assert doc["tickers"] == {} and doc["synthesis"] == {}
    assert len(shash) == 16


def test_quality_advisories_non_blocking(tmp_path, capsys):
    thesis = tmp_path / "theses" / "001-x"
    _write_artifact(thesis, "NVDA", "a.md")
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    # a valid but quality-poor fragment: no tiles, no badges, no timeline, no kicker
    (thesis / "report" / "content.html").write_text("""
<section class="page">
<h2>Executive Summary</h2>
<p>Plain prose with **raw markdown** and no components.</p>
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
    (thesis / "report" / "content.html").write_text("""
<section class="page">
<h2>Executive Summary</h2>
<div class="stat-row">
<div class="stat"><div class="num">24</div><div class="lbl">Artifacts</div><div class="sub">six names</div></div>
</div>
</section>
<section class="page">
<h2>Timeline</h2>
<div class="timeline"><div class="tl-item"><span class="tl-phase">2027-Q4</span></div></div>
</section>
""")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    html = path.read_text(encoding="utf-8")
    assert html.count('class="sheet-head"') == 3          # cover + 2 content pages
    assert html.count('class="reg reg-tl"') == 3
    assert html.count('class="print-btn no-print"') == 3  # Print / PDF on every page
    assert html.count('onclick="window.print()"') == 3
    assert "02 / 03" in html                              # page marks
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
    (thesis / "report" / "content.html").write_text("""
<section class="page">
<h2>Executive Summary</h2>
<div class="stat-row">
<div class="stat"><div class="num">24</div><div class="lbl">Artifacts</div></div>
</div>
</section>
<section class="page">
<h2>Evidence</h2>
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
    assert manifest["page_count"] == 3        # cover + 2 authored pages
    assert len(list(out_dir.glob("page-*.png"))) == 3
    assert (out_dir / "manifest.json").is_file()
    w = manifest["width"]
    assert abs(w - round(8.5 * 72)) <= 1      # letter width at requested dpi
    assert path.read_bytes() == before        # render is strictly read-only on the report
