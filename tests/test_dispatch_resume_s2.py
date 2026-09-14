"""S2 dispatch tests (T031/T032): artifact-driven resume — the filesystem IS the
checkpoint (Q56). `[x]` in tasks.md is display-only, never read as truth.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import dispatch  # noqa: E402
import g1_gate  # noqa: E402
import journal  # noqa: E402

CURRENT_PINS = {"assumption_pin": 1, "corpus_version": "2026-08",
                "as_of": "2026-09-08", "constitution_pin": "0.1.0",
                "skill_pin": "recent-quarter:abc"}

GOOD_ART = """---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "recent-quarter:abc"
mode: default
data_class: slow
---

# body
"""


def _thesis(tmp_path):
    t = tmp_path / "theses" / "001-mvp"
    (t / "artifacts" / "NVDA").mkdir(parents=True)
    return t


def test_resume_absent_runs(tmp_path):
    thesis = _thesis(tmp_path)
    verdict = dispatch.resume_verdict(thesis, "NVDA", "recent-quarter", "default",
                                      current_pins=CURRENT_PINS)
    assert verdict == "run"


def test_resume_valid_skips(tmp_path):
    thesis = _thesis(tmp_path)
    (thesis / "artifacts" / "NVDA" / "2026-09-08_recent-quarter_default.md").write_text(GOOD_ART)
    assert dispatch.resume_verdict(thesis, "NVDA", "recent-quarter", "default",
                                   current_pins=CURRENT_PINS) == "skip"


def test_resume_corrupted_requires_resume_flag(tmp_path):
    thesis = _thesis(tmp_path)
    (thesis / "artifacts" / "NVDA" / "2026-09-08_recent-quarter_default.md").write_text(
        "not a real frontmatter artifact — truncated write")
    assert dispatch.resume_verdict(thesis, "NVDA", "recent-quarter", "default",
                                   current_pins=CURRENT_PINS) == "resume"


def test_resume_stale_leaves_for_converge(tmp_path):
    thesis = _thesis(tmp_path)
    stale = GOOD_ART.replace("as_of: 2026-09-08", "as_of: 2026-08-01")
    (thesis / "artifacts" / "NVDA" / "2026-09-08_recent-quarter_default.md").write_text(stale)
    assert dispatch.resume_verdict(thesis, "NVDA", "recent-quarter", "default",
                                   current_pins=CURRENT_PINS) == "stale"
    # T032: the dispatcher's verdict logic never inspects tasks.md — [x] is not
    # among the inputs. (Proven by construction: no tasks.md exists in this thesis.)


def test_x_mark_is_never_an_input(tmp_path):
    # Even with a tasks.md whose [x] claims completion, an absent artifact is "run"
    # and a stale artifact is "stale" — the ledger cannot steer the dispatcher.
    thesis = _thesis(tmp_path)
    (thesis / "tasks.md").write_text(
        "- [x] T001 [S1] NVDA × recent-quarter × default (src: Q30)\n")
    assert dispatch.resume_verdict(thesis, "NVDA", "recent-quarter", "default",
                                   current_pins=CURRENT_PINS) == "run"


def test_dispatch_journals_explicit_path(tmp_path):
    """D75 #5: every dispatch is journaled — explicit path included (the S1 scope
    left explicit dispatches silent; the reducer then saw an empty journal)."""
    import subprocess

    import tempfile

    with tempfile.TemporaryDirectory() as d:
        thesis = Path(d) / "theses" / "001-mvp"
        thesis.mkdir(parents=True)
        shard = Path(d) / "run1.ndjson"
        res = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "dispatch.py"),
             "--thesis-dir", str(thesis), "--task", "NVDA recent-quarter default",
             "--journal", str(shard)],
            capture_output=True, text=True)
        assert res.returncode == 0, res.stderr
        entries = journal.read_shard(shard)
        assert len(entries) == 1
        assert entries[0]["thesis_resolution"] == "explicit"
        assert entries[0]["skill_id"] == "recent-quarter"


def test_dispatch_requires_journal(tmp_path):
    with pytest.raises(SystemExit) as exc:
        dispatch.main(["--thesis-dir", "/tmp/any", "--task", "NVDA recent-quarter default"])
    assert "--journal required" in str(exc.value)


def test_g1_rejects_prose_entity_claims(tmp_path):
    """D75 #6: prose entity_claims strings defeat the entity index — G1 fails them
    as SCHEMA_MISMATCH (the field is the control plane's input, Q20)."""
    art = ROOT / "tests" / "fixtures" if False else Path(tempfile := __import__("tempfile").mkdtemp()) / "a.md"
    art.write_text("""---
assumption_pin: 1
corpus_version: "x"
as_of: 2026-09-10
constitution_pin: 1.3.0
skill_pin: "x:y"
mode: default
data_class: slow
entity_claims:
  - "NVDA revenue was $215.9B in FY2026 (prose claim)"
---

# b
""")
    problems = g1_gate.check_artifact_full(art)
    assert any("SCHEMA_MISMATCH" in p for p in problems)
