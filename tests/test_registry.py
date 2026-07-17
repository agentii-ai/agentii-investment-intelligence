"""T012 — tests for scripts/_registry.py (write FIRST, must fail before T011).

Covers: schema validation, atomic write (temp + os.replace), round-trip,
and the query helpers (get_skill, list_by_vertical, list_by_layer,
get_enrichment_candidates). Deterministic, no network.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA = REPO_ROOT / "contracts" / "skill-registry.schema.json"


def _load_registry_module():
    spec = importlib.util.spec_from_file_location(
        "_registry", REPO_ROOT / "scripts" / "_registry.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def sample_registry():
    return {
        "version": "1.0.0",
        "generated_by": "test",
        "skills": [
            {
                "skill_name": "business-model",
                "vertical": "equity-research-core",
                "layer_tags": ["L2"],
                "category_tags": ["K1"],
                "retrieval_scope": "unstructured_document_search",
                "has_knowledge_frameworks": False,
                "quality_score": None,
                "quality_score_prev": None,
                "last_enriched": None,
                "enrichment_workflows_applied": [],
                "spec_037_references": 0,
            },
            {
                "skill_name": "rate-cycle",
                "vertical": "macro-strategy",
                "layer_tags": ["L1", "L3"],
                "category_tags": [],
                "retrieval_scope": "structured_only",
                "has_knowledge_frameworks": True,
                "quality_score": 8.0,
                "quality_score_prev": 6.0,
                "last_enriched": "2026-07-17T00:00:00Z",
                "enrichment_workflows_applied": [{"name": "strategy-enrichment", "timestamp": "2026-07-17T00:00:00Z"}],
                "spec_037_references": 3,
            },
        ],
    }


def test_module_exists():
    assert (REPO_ROOT / "scripts" / "_registry.py").is_file()


def test_schema_validation_accepts_valid(sample_registry):
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    jsonschema.validate(sample_registry, schema)  # must not raise


def test_schema_validation_rejects_bad_layer(sample_registry):
    import jsonschema

    schema = json.loads(SCHEMA.read_text())
    sample_registry["skills"][0]["layer_tags"] = ["L9"]  # invalid enum
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(sample_registry, schema)


def test_atomic_write_and_roundtrip(tmp_path, sample_registry):
    mod = _load_registry_module()
    target = tmp_path / "skill-registry.yaml"
    mod.save_registry(sample_registry, path=target)
    assert target.is_file()
    loaded = mod.load_registry(path=target)
    assert loaded["skills"][0]["skill_name"] == "business-model"
    assert len(loaded["skills"]) == 2


def test_atomic_write_no_partial_on_crash(tmp_path, sample_registry, monkeypatch):
    """A failure mid-serialize must not corrupt an existing registry file."""
    mod = _load_registry_module()
    target = tmp_path / "skill-registry.yaml"
    mod.save_registry(sample_registry, path=target)
    original = target.read_text()

    # Force os.replace to fail; the original file must remain intact.
    import os as _os

    def boom(*a, **k):
        raise OSError("simulated crash during replace")

    monkeypatch.setattr(mod.os, "replace", boom)
    with pytest.raises(OSError):
        mod.save_registry(sample_registry, path=target)
    assert target.read_text() == original


def test_get_skill(tmp_path, sample_registry):
    mod = _load_registry_module()
    target = tmp_path / "skill-registry.yaml"
    mod.save_registry(sample_registry, path=target)
    entry = mod.get_skill("rate-cycle", path=target)
    assert entry["vertical"] == "macro-strategy"
    assert mod.get_skill("does-not-exist", path=target) is None


def test_list_by_vertical(tmp_path, sample_registry):
    mod = _load_registry_module()
    target = tmp_path / "skill-registry.yaml"
    mod.save_registry(sample_registry, path=target)
    names = [s["skill_name"] for s in mod.list_by_vertical("macro-strategy", path=target)]
    assert names == ["rate-cycle"]


def test_list_by_layer(tmp_path, sample_registry):
    mod = _load_registry_module()
    target = tmp_path / "skill-registry.yaml"
    mod.save_registry(sample_registry, path=target)
    names = [s["skill_name"] for s in mod.list_by_layer("L3", path=target)]
    assert names == ["rate-cycle"]


def test_get_enrichment_candidates_by_score(tmp_path, sample_registry):
    mod = _load_registry_module()
    target = tmp_path / "skill-registry.yaml"
    mod.save_registry(sample_registry, path=target)
    # candidates below threshold 7 -> business-model (None score treated as 0)
    cands = mod.get_enrichment_candidates(path=target, max_score=7.0)
    names = {s["skill_name"] for s in cands}
    assert "business-model" in names
    assert "rate-cycle" not in names
