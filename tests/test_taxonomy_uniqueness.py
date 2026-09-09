"""T041 (Check 33): contracts/taxonomy.yaml — every value on exactly one axis.

The Q76 placement rule keeps eval corpora comparable; a value on two axes (or on
none) is a silent aggregation break. Mirrors the check.py Check 33 logic so the
test is the executable form of the CI check.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "contracts" / "taxonomy.yaml"


def _load():
    return yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))


def test_axes_are_present_and_versioned():
    tax = _load()
    assert isinstance(tax["version"], int) and tax["version"] >= 1
    for axis in ("error_code", "gap_type", "claim_state", "data_class", "severity"):
        assert isinstance(tax["axes"][axis], list) and tax["axes"][axis]


def test_every_value_lives_on_exactly_one_axis():
    tax = _load()
    seen: dict[str, str] = {}
    for axis, values in tax["axes"].items():
        assert len(values) == len(set(values)), f"duplicate value within axis {axis}"
        for v in values:
            assert v not in seen, f"'{v}' appears on both '{seen.get(v)}' and '{axis}'"
            seen[v] = axis


def test_known_values_are_placed_per_spec():
    tax = _load()
    axes = tax["axes"]
    assert "stale_price" in axes["claim_state"]        # Q76-adjudicated orphan
    assert "INSUFFICIENT_HISTORY" in axes["error_code"]  # Q42 orphan → error_code
    assert "PRICE_ACCESS_PREMATURE" in axes["error_code"]  # plan-declared (Q41)
    assert "dependency_retired" in axes["gap_type"]    # Q70
    assert "retired_by_ic" in axes["claim_state"]      # Q66
    assert "pending_gate" in axes["claim_state"]       # Q80
    assert "severity" in axes                          # Q78's fifth axis


def test_schema_validates_the_yaml():
    import json

    import jsonschema
    schema = json.loads((Path(__file__).resolve().parents[1] / ".." /
                         "specs" / "046-agentii-research-orchestration" / "contracts" /
                         "taxonomy.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(_load(), schema)  # must not raise
