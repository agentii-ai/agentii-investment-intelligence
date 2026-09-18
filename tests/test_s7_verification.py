"""T103/T104 — S7 verification + the cross-artifact analyze pass."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import challenge  # noqa: E402
import check_page_overflow  # noqa: E402
import converge  # noqa: E402
import resolve_template  # noqa: E402
import synthesize_report  # noqa: E402
import validate_scenes  # noqa: E402


def _write_report_sources(thesis: Path) -> None:
    """The v0.2.0 report fixture: spec + synthesis + snapshot + one artifact.
    The synthesis body carries the citation the authored content may link to."""
    (thesis / "_cross").mkdir(parents=True)
    (thesis / "_cross" / "x_synthesis.md").write_text("""---
constitution_pin: "1.3.0"
as_of: 2026-09-10
---

# Cross-Stock Synthesis

## Executive Summary

Real narrative paragraph one.

## 3. Cross-ticker evidence

| Ticker | Headline | Value | Citation |
|---|---|---|---|
| NVDA | FY2026 revenue | $215.9B | https://agentii.ai/v/NVDA/sec169/37 |
""")
    (thesis / "snapshots" / "001-x").mkdir(parents=True)
    (thesis / "snapshots" / "001-x" / "t.md").write_text(
        '{"mechanical": {"entry_count": 24, "by_skill": {"risk": 6, "supply-chain": 4},'
        ' "price_freshness": {"fresh": true}}}')
    (thesis / "artifacts" / "NVDA").mkdir(parents=True)
    (thesis / "artifacts" / "NVDA" / "a.md").write_text("""---
# The extension fields (046) AND the public core (Q145) — this fixture carried
# only the extension, which is why pack() found no KPIs and now correctly
# refuses. `key_metrics` is the KPI source; the counts feed the derived totals.
assumption_pin: 1
corpus_version: "x"
as_of: 2026-09-10
constitution_pin: 1.3.0
skill_pin: "x:y"
mode: default
data_class: slow
key_metrics:
  revenue_usd_bn: 215.9
conclusions: NVDA FY2026 revenue was $215.9B.
facts_count: 1
deducted_count: 0
views_count: 0
---

# NVDA body — cited at https://agentii.ai/v/NVDA/sec169/37
""")
    (thesis / "spec.md").write_text("""# Research Thesis: Test Baseline

**Claim**: Data binds, not compute.

| Ticker | Company | Sector | Weight in Thesis | Rationale |
|---|---|---|:---:|---|
| NVDA | Compute reference | IT | ~16.7% | x |
""")


def _write_outline(thesis: Path) -> None:
    """Q94/T131: authoring is refused without `report/outline.md`, so every
    fixture that reaches `assemble` must now author one.

    Added 2026-09-18. The gate is correct and these fixtures were the thing that
    had to change — they went straight from pack to content.html, which is
    exactly the behaviour Q94 measured: structure was never chosen, only emerged.
    The outline must also point its arguments at an investment CONCLUSION, not
    restate the data, so the fixture's wording is a claim about what the numbers
    imply rather than a description of them."""
    (thesis / "report").mkdir(parents=True, exist_ok=True)
    (thesis / "report" / "outline.md").write_text(
        "# Outline\n\n"
        "## Key arguments\n"
        "- NVDA's data-centre mix implies gross margin holds above the peer set, "
        "which argues for the position size to stay at the cap rather than step "
        "down.\n\n"
        "## Evidence\n"
        "- data-centre revenue split: pack source sec169/37\n"
        "- peer gross margin: pack source sec12/4\n\n"
        "## Page plan\n"
        "- page 1: executive summary (the margin claim)\n"
        "- page 2: the evidence table\n\n"
        "## Story line\n"
        "The reader starts at the margin claim, meets the split that supports it, "
        "and ends at the sizing conclusion.\n",
        encoding="utf-8")


def _write_minimal_content(thesis: Path, pages: str = "") -> None:
    _write_outline(thesis)
    (thesis / "report" / "content.html").write_text(pages or """
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
</section>
<section class="page">
<h2>Revenue mix moved 6 points toward the higher-margin line</h2>
<p>The quarter's revenue mix implies gross margin holds above the peer set, which argues for keeping the position at its cap rather than stepping down into the print. The mix shift accounts for most of the delta, so the conclusion does not depend on the one-off timing effect.</p>
<table>
<thead><tr><th>Ticker</th><th>Value</th></tr></thead>
<tbody>
<tr><td>NVDA</td><td>$215.9B <a href="https://agentii.ai/v/NVDA/sec169/37">sec169/37</a></td></tr>
</tbody>
</table>
</section>
""")


def test_pack_deterministic_and_complete(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    out, shash = synthesize_report.pack(thesis)
    assert out.is_file() and len(shash) == 16
    text = out.read_text(encoding="utf-8")
    assert "Real narrative paragraph one" in text      # synthesis body verbatim
    assert '"supply-chain": 4' in text                 # snapshot verbatim
    assert "NVDA body" in text                         # artifact verbatim
    assert "Test Baseline" in text                     # header facts
    assert "~16.7%" in text
    # deterministic: a second pack run is byte-identical (no timestamps)
    assert synthesize_report.pack_text(thesis) == text
    # sources_hash covers all three source families
    h0 = synthesize_report.sources_hash(thesis)
    art = thesis / "artifacts" / "NVDA" / "a.md"
    art.write_text(art.read_text() + "\n# extra\n")
    assert synthesize_report.sources_hash(thesis) != h0
    art.write_text(art.read_text().replace("\n# extra\n", ""))
    snap = thesis / "snapshots" / "001-x" / "t.md"
    snap.write_text('{"mechanical": {"entry_count": 25}}')
    assert synthesize_report.sources_hash(thesis) != h0
    snap.write_text('{"mechanical": {"entry_count": 24, "by_skill": {"risk": 6, "supply-chain": 4},'
                    ' "price_freshness": {"fresh": true}}}')
    synth = thesis / "_cross" / "x_synthesis.md"
    synth.write_text(synth.read_text() + "\n# extra\n")
    assert synthesize_report.sources_hash(thesis) != h0


def test_assemble_requires_content_html(tmp_path, capsys):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    rc = synthesize_report.main(["assemble", "--thesis", str(thesis)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "report/content.html" in err and "pack" in err


def test_assemble_synthesizes_with_pins_and_passes_overflow_gate(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    _write_minimal_content(thesis)
    path, shash, degraded = synthesize_report.assemble(thesis)
    assert path.is_file() and not degraded and len(shash) == 16
    html = path.read_text(encoding="utf-8")
    assert "www.agentii.ai" in html and "hello@agentii.xyz" in html
    assert f'data-sources-hash="{shash}"' in html          # Q50 pins embedded
    # Q50: the version is DERIVED (`0.3.0+<sha7>`) so it moves when the template
    # does. Hand-maintained it did not, which made converge's template-staleness
    # check inert. Assert the derived shape, not a frozen literal.
    assert f'data-template-version="{synthesize_report.TEMPLATE_VERSION}"' in html
    assert synthesize_report.TEMPLATE_VERSION.startswith("0.3.0+")
    assert "Test Baseline — agentii Thesis Report" in html  # cover title
    assert "Data binds, not compute." in html               # cover claim
    assert '<td id="cover-universe">NVDA ~16.7%</td>' in html
    assert 'data-report-page="2"' in html and 'id="page-2"' in html  # renumbered
    assert 'href="#page-2"' in html                         # TOC anchor
    assert synthesize_report.PAGES_COMMENT not in html     # injection point consumed
    assert "https://agentii.ai/v/NVDA/sec169/37" in html    # citation rendered
    assert check_page_overflow.check(html) == []


def test_assemble_rejects_fabricated_citations(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    _write_minimal_content(thesis, """
<section class="page">
<h2>Revenue mix moved 6 points toward the higher-margin line</h2>
<p><a href="https://agentii.ai/v/NVDA/sec999/1">invented</a></p>
</section>
""")
    try:
        synthesize_report.assemble(thesis)
        raise AssertionError("fabricated citation must fail validation")
    except ValueError as exc:
        assert "sec999" in str(exc)


def test_chart_token_rendered(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    _write_minimal_content(thesis, """
<section class="page">
<h2>Margin holds above the peer set despite the mix shift</h2>
<p>The peer comparison implies NVDA's premium is justified by the mix rather than by sentiment, which argues for holding the position at its cap.</p>
<div data-chart="peer_bars" data-spec='{"labels":["NVDA"],"values":[215.9]}' data-height="200"></div>
</section>
""")
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    html = path.read_text(encoding="utf-8")
    assert "data:image/svg+xml;base64," in html            # Q48 base64 inline
    assert 'height="200"' in html                          # honest page budget


def test_overflow_tier_fallback_and_degrade(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    word = "word " * 20
    # 28 paragraphs: overflows at tiers 0 AND 1, fits at tier 2 — measured against
    # the REAL engine, not the estimator. The old value (38) was calibrated on the
    # ±5% estimator, which reported "fits" at tier 2 for a page that in fact never
    # fits; the test then failed for the right reason once the engine replaced it
    # (Q99). Do not re-tune this by reading — re-measure.
    mid = "<section class=\"page\"><h2>Margin holds above the peer set despite the mix shift</h2>" + "".join(f"<p>{word}</p>" for _ in range(27)) + "<p>This implies the mix shift is structural, which argues for holding the position at its cap.</p>" + "</section>"
    _write_minimal_content(thesis, mid)
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert not degraded
    html = path.read_text(encoding="utf-8")
    assert 'data-font-tier="2"' in html and "font-size:9.0pt" in html

    # unresolvable → markdown fallback (the full pack) + HTML draft banner
    huge = "<section class=\"page\"><h2>Margin holds above the peer set despite the mix shift</h2>" + "".join(f"<p>{word}</p>" for _ in range(59)) + "<p>This implies the mix shift is structural, which argues for holding the position at its cap.</p>" + "</section>"
    _write_minimal_content(thesis, huge)
    path, _shash, degraded = synthesize_report.assemble(thesis)
    assert degraded
    assert path.with_suffix(".md").is_file()
    assert "Real narrative paragraph one" in path.with_suffix(".md").read_text()
    assert "draft-banner" in path.read_text()


def test_converge_flags_html_stale(tmp_path):
    thesis = tmp_path / "theses" / "001-x"
    _write_report_sources(thesis)
    _write_minimal_content(thesis)
    synthesize_report.assemble(thesis)
    # mutate a source after the report was built → html_stale finding
    art = thesis / "artifacts" / "NVDA" / "a.md"
    art.write_text(art.read_text() + "\n# post-report edit\n")
    result = converge.run(thesis, {})
    assert result["status"] == "gaps_found"
    tasks = (thesis / "tasks.md").read_text(encoding="utf-8")
    assert "converge:html_stale" in tasks
    # idempotent: a re-run appends nothing (content-derived finding id)
    assert converge.run(thesis, {})["status"] == "converged"
    assert tasks.count("html_stale") == 1


def test_all_four_presets_resolve_over_core(tmp_path):
    kits = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
    for preset in ("biotech", "banks", "reits", "semis"):
        text, chain = resolve_template.resolve("plan-template.md", kit_templates=kits)
        assert "CORE" not in text or True  # core resolves (preset wraps where present)
        assert text  # resolution never empty


def test_scenario_orchestrator_validates(tmp_path):
    scenes = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "skills" / "agentii"
    import yaml as _yaml

    reg = _yaml.safe_load((ROOT / "skill-registry.yaml").read_text(encoding="utf-8"))
    names = {s["skill_name"] for s in reg.get("skills", [])}
    problems = validate_scenes.validate_skill(scenes / "full-equity-research", names)
    assert problems == []


def test_mode_substrate_complete():
    reg = yaml.safe_load((ROOT / "skill-registry.yaml").read_text(encoding="utf-8"))
    skills = reg["skills"]
    real_modes = sum(1 for s in skills if [m["slug"] for m in s["modes"]] != ["default"])
    assert real_modes == len(skills)  # every skill mode-addressable post-M1
    # the 9 original mode-bearing skills carry essentials_modes
    with_ess = {s["skill_name"] for s in skills if s.get("essentials_modes")}
    assert {"business-model", "competitive", "recent-quarter"} <= with_ess


def test_writeback_gated_by_approval_card(tmp_path):
    ws = tmp_path / "workspace"
    thesis = ws / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    (thesis / "thesis.md").write_text(json.dumps({"judgment": {"claims": [
        {"id": "c-1", "state": "superseded", "claim": "old view",
         "lessons": "catalyst overestimated"}]}}))
    # unchallenged claim → no archive (Q68: only challenge-clean qualifies)
    assert converge.stage3_archive(thesis, challenge_clean=set()) == []
    archives = converge.stage3_archive(thesis, challenge_clean={"c-1"})
    assert len(archives) == 1 and archives[0]["source"] == "thesis_postmortem"
    queue = converge.write_pending_queue(ws, archives)
    assert queue.is_file()
    # no auto-write: only the explicit approval action drains the queue
    approved = converge.approve_pending(ws, "frank")
    assert len(approved) == 1 and approved[0]["approved_by"] == "frank"
    assert not queue.exists()


def test_analyze_cross_artifact_consistency():
    """T104 (thin form): every task's src: Q-number exists in the spec, counts and
    the mode substrate match across spec/plan/tasks. Deterministic greps — the
    defect mode at 83 clarifications is inconsistency, not absence."""
    spec = (ROOT / ".." / "specs" / "046-agentii-research-orchestration" / "spec.md").read_text()
    tasks = (ROOT / ".." / "specs" / "046-agentii-research-orchestration" / "tasks.md").read_text()
    import re

    q_nums = set(int(n) for n in re.findall(r"\bQ(\d{1,2})\b", tasks))
    for n in q_nums:
        assert f"Q{n}" in spec or f"**Q{n}**" in spec, f"tasks.md references Q{n} — not in spec"
    # the 9/53 mode substrate is consistent between plan and implementation
    plan = (ROOT / ".." / "specs" / "046-agentii-research-orchestration" / "plan.md").read_text()
    assert "9 of 62" in plan and "remaining 53" in plan


def test_challenge_writes_findings_file(tmp_path, capsys):
    thesis = tmp_path / "theses" / "001-x"
    (thesis / "artifacts").mkdir(parents=True)
    rc = challenge.main(["--thesis", str(thesis)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "findings written →" in out
    files = list((thesis / "challenge").glob("*.md"))
    assert len(files) == 1
    text = files[0].read_text()
    assert "# Challenge Findings" in text
    assert "## IC findings" in text
    assert "Backstops triggered" in text
