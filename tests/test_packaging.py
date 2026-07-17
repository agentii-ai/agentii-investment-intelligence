"""T080 — tests for packaging export (write FIRST).

Export reproducibility (diff-clean re-run) + per-target structural validation on a
representative skill. Deterministic: exports from on-disk canonical SKILL.md, no
external Skill Seekers dependency required for the native exporter.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MOD = REPO_ROOT / "packaging" / "export.py"


def _load():
    spec = importlib.util.spec_from_file_location("export", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _sample_skill(tmp_path):
    d = tmp_path / "skills" / "agentii" / "demo"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        "---\nname: demo\ndescription: demo skill\nmulti_ticker_semantics: single_target\n"
        "allowed_tools:\n  - search_knowledge_entries\nretrieval_scope: structured_only\n---\n"
        "## Methodology\n### Step 1\ndo the thing\n## Output Structure\n1\n2\n3\n4\n5\n"
        "## Error Handling\nhandle\n"
    )
    return d


def test_module_exists():
    assert MOD.is_file()


def test_targets_list():
    m = _load()
    assert set(m.TARGETS) >= {"claude-code", "codex", "cowork", "generic-cli"}


def test_export_creates_per_target(tmp_path):
    m = _load()
    sk = _sample_skill(tmp_path)
    out = tmp_path / "targets"
    m.export_skill(sk, out, targets=["codex", "generic-cli"])
    assert (out / "codex" / "demo" / "plugin.json").is_file()
    assert (out / "codex" / "demo" / "SKILL.md").is_file()
    assert (out / "generic-cli" / "demo" / "SKILL.md").is_file()


def test_export_reproducible(tmp_path):
    m = _load()
    sk = _sample_skill(tmp_path)
    out = tmp_path / "targets"
    m.export_skill(sk, out, targets=["codex"])
    first = (out / "codex" / "demo" / "plugin.json").read_text()
    m.export_skill(sk, out, targets=["codex"])  # re-run
    second = (out / "codex" / "demo" / "plugin.json").read_text()
    assert first == second  # diff-clean


def test_codex_plugin_json_valid(tmp_path):
    import json
    m = _load()
    sk = _sample_skill(tmp_path)
    out = tmp_path / "targets"
    m.export_skill(sk, out, targets=["codex"])
    pj = json.loads((out / "codex" / "demo" / "plugin.json").read_text())
    assert pj["name"] == "demo"
    assert "description" in pj


def test_placeholders_preserved(tmp_path):
    m = _load()
    d = tmp_path / "skills" / "agentii" / "macro"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        "---\nname: macro\ndescription: d\nmulti_ticker_semantics: single_target\n"
        "retrieval_scope: structured_only\n---\n## Methodology\nUses ~~macro_data placeholder.\n"
        "## Output Structure\n1\n2\n3\n4\n5\n## Error Handling\nx\n"
    )
    out = tmp_path / "targets"
    m.export_skill(d, out, targets=["generic-cli"])
    text = (out / "generic-cli" / "macro" / "SKILL.md").read_text()
    assert "~~macro_data" in text  # connector-agnostic placeholder preserved
