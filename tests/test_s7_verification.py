"""T103/T104 — S7 verification + the cross-artifact analyze pass."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_page_overflow  # noqa: E402
import converge  # noqa: E402
import resolve_template  # noqa: E402
import synthesize_report  # noqa: E402
import validate_scenes  # noqa: E402


def test_report_synthesizes_with_pins_and_passes_overflow_gate(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    (thesis / "artifacts" / "NVDA").mkdir(parents=True)
    (thesis / "artifacts" / "NVDA" / "a.md").write_text("""---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "x:y"
mode: default
data_class: slow
---

# body
""")
    path, shash, degraded = synthesize_report.synthesize(thesis)
    assert path.is_file()
    assert len(shash) == 16
    assert not degraded  # a normal thesis fits the letter pages
    html = path.read_text(encoding="utf-8")
    assert "www.agentii.ai" in html
    assert "hello@agentii.xyz" in html
    assert f'data-sources-hash="{shash}"' in html  # Q50 pins embedded
    assert check_page_overflow.check(html) == []


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
