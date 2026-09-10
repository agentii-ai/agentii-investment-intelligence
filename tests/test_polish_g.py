"""Global-polish tests (G1–G4): converge ID continuation, network-guard skip,
g2 CLI subprocess wiring, challenge CLI contradiction surface."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import challenge  # noqa: E402
import converge  # noqa: E402
import g2_validator  # noqa: E402

CURRENT_PINS = {"assumption_pin": 1}


# --- G1: converge IDs continue the file's own sequence ------------------------

def test_convergence_ids_continue_task_sequence(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    (thesis / "artifacts" / "NVDA").mkdir(parents=True)
    (thesis / "artifacts" / "NVDA" / "a_recent-quarter_default.md").write_text(
        "---\nassumption_pin: 0\ncorpus_version: \"x\"\nas_of: 2026-01-01\n"
        "constitution_pin: x\nskill_pin: \"x:y\"\nmode: default\ndata_class: slow\n---\n# b\n")
    rows = "\n".join(f"- [ ] T{i:03d} [S1] TKR{i} × skill × default (src: Q30)"
                     for i in range(1, 6))
    (thesis / "tasks.md").write_text("# Research Tasks\n## Phase 1\n" + rows + "\n")
    result = converge.run(thesis, current_pins=CURRENT_PINS)
    assert result["status"] == "gaps_found"
    text = (thesis / "tasks.md").read_text()
    tail = text.split("## Phase 1: Convergence", 1)[1]  # IDs in the new section only
    ids = [int(m) for m in __import__("re").findall(r"^- \[ \] T(\d{3}) ", tail,
                                                    __import__("re").MULTILINE)]
    # missing rows re-use their source task's ID (T001–T005, by design); the NEW
    # stale finding continues the sequence at T006 — never a detached 900-range.
    assert 6 in ids
    assert not any(i >= 900 for i in ids)


# --- G3: g2 CLI runs the documented subprocess wiring -------------------------

def test_g2_cli_runs_validator_subprocess(tmp_path, capsys):
    fake = tmp_path / "validator.sh"
    fake.write_text('#!/bin/sh\necho \'{"artifact": "a.md", "falsifiable": true, "supports": false, "contradictions": []}\'\n')
    fake.chmod(0o755)
    rc = g2_validator.main(["--artifact", "a.md", "--validator-cmd", str(fake)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["falsifiable"] is True  # parsed + schema-validated


def test_g2_cli_fails_on_invalid_verdict(tmp_path, capsys):
    fake = tmp_path / "bad.sh"
    fake.write_text('#!/bin/sh\necho \'{"artifact": "a.md"}\'\n')
    fake.chmod(0o755)
    assert g2_validator.main(["--artifact", "a.md", "--validator-cmd", str(fake)]) == 1


# --- G4: challenge CLI exposes the entity-index contradiction surface ----------

def test_challenge_cli_reports_contradiction(tmp_path, capsys):
    thesis = tmp_path / "theses" / "001-mvp"
    (thesis / "artifacts").mkdir(parents=True)
    for name, value in (("a1.md", 73.0), ("a2.md", 61.0)):
        (thesis / "artifacts" / name).write_text(
            f"---\nassumption_pin: 1\ncorpus_version: \"x\"\nas_of: 2026-09-08\n"
            f"constitution_pin: x\nskill_pin: \"x:y\"\nmode: default\ndata_class: slow\n"
            f"entity_claims:\n  - entity: NVDA\n    metric: gross_margin\n    value: {value}\n"
            f"    unit: pct\n    period: 2026Q2\n    source: x\n"
            f"    retrieved_at: 2026-09-08T09:12:00-04:00\n---\n# b\n")
    rc = challenge.main(["--thesis", str(thesis)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "contradictions: 1" in out
    assert "NVDA.gross_margin" in out
    assert "id=" in out  # content-derived stable IDs
