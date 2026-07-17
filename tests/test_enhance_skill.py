"""T017 — tests for scripts/enhance-skill.py (write FIRST).

Covers: preset parse/validate (line-numbered errors on bad YAML), applies_to
refusal against the registry, --dry-run writes nothing, and --json output shape.
Deterministic — no LLM/MCP calls (enrichment stages take injected records).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ENHANCE = REPO_ROOT / "scripts" / "enhance-skill.py"


def _load():
    spec = importlib.util.spec_from_file_location("enhance_skill", ENHANCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_script_exists():
    assert ENHANCE.is_file()


def test_load_preset_valid(tmp_path):
    mod = _load()
    p = tmp_path / "wf.yaml"
    p.write_text(
        "name: demo\ndescription: d\nversion: 1.0.0\nstages:\n"
        "  - name: s1\n    type: reference_injection\n    prompt: go\n"
    )
    preset = mod.load_preset(p)
    assert preset["name"] == "demo"
    assert preset["stages"][0]["type"] == "reference_injection"


def test_load_preset_bad_yaml_line_numbered(tmp_path):
    mod = _load()
    p = tmp_path / "bad.yaml"
    p.write_text("name: demo\nstages: [unclosed\n")
    with pytest.raises(mod.PresetError) as exc:
        mod.load_preset(p)
    # error must reference a line number
    assert "line" in str(exc.value).lower()


def test_load_preset_schema_violation(tmp_path):
    mod = _load()
    p = tmp_path / "wf.yaml"
    # missing required 'stages'
    p.write_text("name: demo\ndescription: d\nversion: 1.0.0\n")
    with pytest.raises(mod.PresetError):
        mod.load_preset(p)


def test_applies_to_refusal():
    mod = _load()
    preset = {"name": "x", "applies_to": {"vertical": "macro-strategy"}, "stages": []}
    skill_entry = {"skill_name": "business-model", "vertical": "equity-research-core", "layer_tags": ["L2"]}
    ok, reason = mod.matches_applies_to(preset, skill_entry)
    assert ok is False
    assert "vertical" in reason.lower()


def test_applies_to_layer_and_score():
    mod = _load()
    preset = {"name": "x", "applies_to": {"layer_tags": ["L4"], "min_quality_score": 5}, "stages": []}
    l2 = {"skill_name": "a", "vertical": "v", "layer_tags": ["L2"], "quality_score": 6}
    l4 = {"skill_name": "b", "vertical": "v", "layer_tags": ["L4"], "quality_score": 6}
    assert mod.matches_applies_to(preset, l2)[0] is False   # wrong layer
    assert mod.matches_applies_to(preset, l4)[0] is True


def _mini_skill(tmp_path):
    """Create a minimal on-disk skill + registry for CLI tests."""
    sk_dir = tmp_path / "plugins" / "vertical-plugins" / "equity-research-core" / "skills" / "agentii" / "business-model"
    (sk_dir / "references").mkdir(parents=True)
    (sk_dir / "SKILL.md").write_text("---\nname: business-model\n---\n## Methodology\n")
    reg = tmp_path / "skill-registry.yaml"
    reg.write_text(yaml.safe_dump({
        "version": "1.0.0",
        "skills": [{"skill_name": "business-model", "vertical": "equity-research-core", "layer_tags": ["L2"], "quality_score": 3}],
    }))
    return sk_dir, reg


def test_dry_run_writes_nothing(tmp_path):
    sk_dir, reg = _mini_skill(tmp_path)
    kf = sk_dir / "references" / "knowledge-frameworks.md"
    res = subprocess.run(
        [sys.executable, str(ENHANCE), "--skill", "business-model",
         "--workflow", "strategy-enrichment", "--dry-run", "--json",
         "--registry", str(reg), "--skills-root", str(tmp_path / "plugins")],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert res.returncode == 0, res.stderr
    assert not kf.exists()  # dry-run must not create the file
    payload = json.loads(res.stdout)
    assert payload["dry_run"] is True
    assert "diff" in payload


def test_json_shape(tmp_path):
    _sk_dir, reg = _mini_skill(tmp_path)
    res = subprocess.run(
        [sys.executable, str(ENHANCE), "--skill", "business-model",
         "--workflow", "strategy-enrichment", "--dry-run", "--json",
         "--registry", str(reg), "--skills-root", str(tmp_path / "plugins")],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    payload = json.loads(res.stdout)
    for key in ("skill", "workflows", "dry_run", "status"):
        assert key in payload


# --- US2: chaining, history threading, idempotent re-run (T029) --------------
def _records():
    return {
        "strategy-enrichment": {"strategies": [
            {"citation_id": "str_001", "columns": ["str_001", "Moat", "quality", "wide moat", "AAPL"]},
        ]},
        "case-enrichment": {"cases": [
            {"citation_id": "case_001", "columns": ["case_001", "PFE turnaround", "3y", "pharma", "recovery"]},
        ]},
    }


def test_chaining_threads_history(tmp_path):
    mod = _load()
    _sk_dir, reg = _mini_skill(tmp_path)
    res = mod.enrich(
        "business-model", ["strategy-enrichment", "case-enrichment"],
        registry_path=reg, skills_root=tmp_path / "plugins",
        injected_records=_records(),
    )
    assert res["status"] == "ok"
    # both stages' citations landed in the same working copy
    assert res["citations_inserted"] == 2
    kf = (_sk_dir / "references" / "knowledge-frameworks.md").read_text()
    assert "str_001" in kf and "case_001" in kf


def test_idempotent_rerun_zero_diff(tmp_path):
    mod = _load()
    _sk_dir, reg = _mini_skill(tmp_path)
    kw = dict(registry_path=reg, skills_root=tmp_path / "plugins", injected_records=_records())
    mod.enrich("business-model", ["strategy-enrichment", "case-enrichment"], **kw)
    kf_path = _sk_dir / "references" / "knowledge-frameworks.md"
    first = kf_path.read_text()
    res2 = mod.enrich("business-model", ["strategy-enrichment", "case-enrichment"], **kw)
    assert res2["citations_inserted"] == 0
    assert kf_path.read_text() == first  # zero diff on re-run


def test_applies_to_refusal_halts_chain(tmp_path):
    mod = _load()
    _sk_dir, reg = _mini_skill(tmp_path)
    # setup-enrichment requires L4; the L2 fixture skill must be refused
    res = mod.enrich(
        "business-model", ["strategy-enrichment", "setup-enrichment"],
        registry_path=reg, skills_root=tmp_path / "plugins",
        injected_records=_records(),
    )
    assert res["status"] == "refused"
    # intermediate output preserved (nothing written on refusal)
    assert not (_sk_dir / "references" / "knowledge-frameworks.md").exists()


def test_from_registry_batch_selects_low_scores(tmp_path):
    mod = _load()
    import yaml as _y
    # two skills: one below threshold, one above
    sk_root = tmp_path / "plugins"
    for name, score in [("business-model", 3), ("valuation-methods", 9)]:
        d = sk_root / "vertical-plugins" / "equity-research-core" / "skills" / "agentii" / name
        (d / "references").mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    reg = tmp_path / "skill-registry.yaml"
    reg.write_text(_y.safe_dump({"version": "1.0.0", "skills": [
        {"skill_name": "business-model", "vertical": "equity-research-core", "layer_tags": ["L2"], "quality_score": 3},
        {"skill_name": "valuation-methods", "vertical": "equity-research-core", "layer_tags": ["L2"], "quality_score": 9},
    ]}))
    cands = mod._registry.get_enrichment_candidates(path=reg, vertical="equity-research-core", max_score=7.0)
    names = {c["skill_name"] for c in cands}
    assert names == {"business-model"}


class _FakeSpec037:
    def __init__(self, empty=False, raise_it=False):
        self.empty, self.raise_it = empty, raise_it

    def search_investment_strategies(self, **kw):
        if self.raise_it:
            raise ConnectionError("down")
        if self.empty:
            return []
        return [{"strategy_id": "s1", "title": "Moat", "kind": "quality",
                 "summary": "wide moat", "citation_id": "s1", "ticker": "AAPL", "page": 3}]


def test_enrich_via_spec037_bridge_writes_rows(tmp_path):
    mod = _load()
    sk_dir, reg = _mini_skill(tmp_path)
    res = mod.enrich("business-model", ["strategy-enrichment"],
                     registry_path=reg, skills_root=tmp_path / "plugins",
                     spec037_client=_FakeSpec037())
    assert res["status"] == "ok"
    assert res["citations_inserted"] == 1
    kf = (sk_dir / "references" / "knowledge-frameworks.md").read_text()
    assert "s1" in kf and "agentii.ai/v/AAPL/s1/3" in kf


def test_enrich_coverage_gap_when_spec037_down(tmp_path):
    mod = _load()
    _sk_dir, reg = _mini_skill(tmp_path)
    res = mod.enrich("business-model", ["strategy-enrichment"],
                     registry_path=reg, skills_root=tmp_path / "plugins",
                     spec037_client=_FakeSpec037(raise_it=True))
    assert "coverage_gap" in res
    assert res["citations_inserted"] == 0


def test_enrich_methodology_patch_injects_block(tmp_path):
    mod = _load()
    sk_dir, reg = _mini_skill(tmp_path)
    mod.enrich("business-model", ["case-enrichment"],
               registry_path=reg, skills_root=tmp_path / "plugins",
               injected_records={"case-enrichment": {"cases": [
                   {"citation_id": "c1", "columns": ["c1", "PFE", "3y", "pharma", "x", "https://agentii.ai/v/PFE/c1/1"]}]}})
    md = (sk_dir / "SKILL.md").read_text()
    assert "### Runtime Analogue Discovery" in md


def test_rollback_on_score_regression(tmp_path):
    """T047: a quality_audit-bearing chain that regresses the score must revert (R2)."""
    mod = _load()
    # Build a skill already at a good score (5 refs w/ valid citations, full sections).
    d = tmp_path / "plugins" / "vertical-plugins" / "equity-research-core" / "skills" / "agentii" / "business-model"
    (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text(
        "---\nname: business-model\n---\n## Methodology\n### a\n### b\n### c\n### d\n### e\n"
        "## Output Structure\n1\n2\n3\n4\n5\n## Error Handling\nx\n## Triggers\n- t\n"
    )
    kf = d / "references" / "knowledge-frameworks.md"
    good_rows = "\n".join(
        f"| s{i} | T | quality | one | https://agentii.ai/v/AAPL/s{i}/1 |" for i in range(5))
    kf.write_text("## Referenced Strategies\n\n| strategy_id | t | k | o | c |\n|---|---|---|---|---|\n" + good_rows + "\n")
    before = kf.read_text()

    import yaml as _y
    reg = tmp_path / "skill-registry.yaml"
    reg.write_text(_y.safe_dump({"version": "1.0.0", "skills": [
        {"skill_name": "business-model", "vertical": "equity-research-core", "layer_tags": ["L2"]}]}))

    # comprehensive-enrichment has a quality_audit stage; inject a BROKEN citation row
    # (no /v/ link) which lowers citation_integrity → regression → rollback.
    res = mod.enrich("business-model", ["comprehensive-enrichment"],
                     registry_path=reg, skills_root=tmp_path / "plugins",
                     injected_records={"comprehensive-enrichment": {"strategies": [
                         {"citation_id": "bad1", "columns": ["bad1", "T", "quality", "one", "(no link)"]}]}})
    assert res["status"] == "rolled_back"
    assert kf.read_text() == before  # reverted to original


def test_workflow_show_accepts_user_override_flag(tmp_path):
    """Regression: `workflow show --user-workflow-dir` must be accepted by the subparser
    and must override a bundled preset of the same name (FR-005)."""
    udir = tmp_path / "userwf"
    udir.mkdir()
    (udir / "strategy-enrichment.yaml").write_text(
        "name: strategy-enrichment\ndescription: USER OVERRIDE\nversion: 2.0.0\n"
        "stages:\n  - name: s\n    type: custom\n    prompt: overridden\n"
    )
    res = subprocess.run(
        [sys.executable, str(ENHANCE), "workflow", "show", "strategy-enrichment",
         "--user-workflow-dir", str(udir)],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert res.returncode == 0, res.stderr
    assert "USER OVERRIDE" in res.stdout
