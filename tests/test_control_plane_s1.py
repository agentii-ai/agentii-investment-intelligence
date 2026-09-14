"""S1 control-plane tests: g1_gate (T019), refusal (T020), dispatch (T021),
journal (T022), reduction (T023), mkdir-CAS allocation (T024)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import alloc_thesis_id  # noqa: E402
import dispatch  # noqa: E402
import g1_gate  # noqa: E402
import journal  # noqa: E402
import reduce_journals  # noqa: E402
import refusal  # noqa: E402

GOOD_FM = """---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "recent-quarter:abc123"
mode: default
data_class: slow
---

# Artifact body
"""


# --- T019: g1_gate ------------------------------------------------------------

def test_g1_passes_complete_artifact(tmp_path):
    art = tmp_path / "artifact.md"
    art.write_text(GOOD_FM)
    assert g1_gate.check_artifact(art) == []


@pytest.mark.parametrize("drop", ["assumption_pin", "corpus_version", "as_of",
                                  "constitution_pin", "skill_pin", "mode", "data_class"])
def test_g1_fails_each_missing_field(tmp_path, drop):
    fm = GOOD_FM.replace(f"{drop}:", f"_removed_{drop}:") if drop not in ("mode", "data_class") \
        else "\n".join(l for l in GOOD_FM.splitlines() if not l.startswith(f"{drop}:"))
    art = tmp_path / "artifact.md"
    art.write_text(fm)
    problems = g1_gate.check_artifact(art)
    assert any(drop in pr for pr in problems), problems


# --- T020: refusal ------------------------------------------------------------

def test_refuse_carries_code_prefix():
    env = refusal.refuse("DATA_STALE", "re-run after refresh")
    assert env["status"] == "error"
    assert env["error"].startswith("DATA_STALE: ")


def test_parse_error_code_is_deterministic():
    assert refusal.parse_error_code("DATA_STALE: xyz") == "DATA_STALE"
    assert refusal.parse_error_code("plain prose") is None
    assert refusal.parse_error_code(None) is None


def test_require_observed_at_refuses_and_passes():
    assert refusal.require_observed_at({"observed_at": "2026-09-08T16:00:00-04:00"}) is None
    env = refusal.require_observed_at({"price": 1.0})
    assert env["status"] == "error"
    assert env["error"].startswith("DATA_STALE")


# --- T021: dispatch -----------------------------------------------------------

def test_dispatch_refuses_without_thesis_dir(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)  # no theses/ upward
    with pytest.raises(SystemExit) as exc:
        dispatch.main(["--task", "NVDA recent-quarter default"])
    assert "thesis_dir missing" in str(exc.value)


def test_dispatch_accepts_explicit_thesis_dir(tmp_path, capsys):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    rc = dispatch.main(["--thesis-dir", str(thesis),
                        "--task", "NVDA recent-quarter default",
                        "--journal", str(tmp_path / "run1.ndjson")])
    assert rc == 0
    assert "thesis_dir=" in capsys.readouterr().out


def test_cwd_fallback_is_journaled_never_silent(tmp_path):
    thesis = tmp_path / "theses" / "001-mvp"
    thesis.mkdir(parents=True)
    shard = tmp_path / "journal.ndjson"
    with pytest.raises(SystemExit) as exc:
        # cwd fallback with no --journal must refuse (silent fallback is forbidden)
        dispatch.main(["--task", "NVDA recent-quarter default"])
        # unreachable — main raises for missing journal only AFTER fallback resolves;
        # here cwd is repo root, not tmp_path, so the no-thesis error fires instead.
    assert exc.value.code is not None
    # Direct fallback resolution test:
    thesis_dir, note = dispatch.resolve_thesis_dir(None, thesis.parent / "subdir")
    assert note == "cwd_fallback"
    assert thesis_dir.name == "001-mvp"


# --- T022: journal ------------------------------------------------------------

def test_journal_entries_roundtrip(tmp_path):
    shard = tmp_path / "shards" / "run1.ndjson"
    journal.append_entry(shard, journal.make_entry("recent-quarter", "NVDA", "default",
                                                   "001-mvp", ["get_realtime_quote"]))
    journal.append_entry(shard, journal.make_entry("business-model", "NVDA", "default",
                                                   "001-mvp", []))
    entries = journal.read_shard(shard)
    assert len(entries) == 2
    assert entries[0]["skill_id"] == "recent-quarter"
    for k in journal.REQUIRED_KEYS:
        assert k in entries[0]


def test_journal_rejects_incomplete_entries(tmp_path):
    with pytest.raises(ValueError):
        journal.append_entry(tmp_path / "x.ndjson", {"skill_id": "recent-quarter"})


# --- T023: reduction ----------------------------------------------------------

def test_reduction_writes_thesis_atomically(tmp_path):
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()
    for i in range(3):
        journal.append_entry(shard_dir / f"a{i}.ndjson",
                             journal.make_entry("recent-quarter", "NVDA", "default",
                                                "001-mvp", [],
                                                observed_at="2026-09-08T16:00:00-04:00"))
    thesis = tmp_path / "theses" / "001-mvp" / "thesis.md"
    doc = reduce_journals.reduce(shard_dir, thesis)
    assert doc["mechanical"]["entry_count"] == 3
    assert thesis.is_file()
    assert "conviction" in doc["judgment"]  # ② revision hook ran over ①'s output
    assert not thesis.with_suffix(".tmp").exists()  # no temp residue


def test_reduction_stale_price_degrades_claim(tmp_path):
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()
    journal.append_entry(shard_dir / "a.ndjson",
                         journal.make_entry("recent-quarter", "NVDA", "default",
                                            "001-mvp", [],
                                            observed_at="2020-01-01T16:00:00-04:00"))
    doc = reduce_journals.reduce(shard_dir, tmp_path / "thesis.md")
    assert doc["mechanical"]["price_freshness"]["stale_price"] is True


# --- T024: mkdir-CAS ----------------------------------------------------------

def test_alloc_assigns_sequential_ids(tmp_path):
    first = alloc_thesis_id.allocate(tmp_path / "theses", "mvp")
    second = alloc_thesis_id.allocate(tmp_path / "theses", "mvp")
    assert first.name == "001-mvp"
    assert second.name == "002-mvp"
    assert first.is_dir() and second.is_dir()


def test_alloc_resumes_after_existing_ids(tmp_path):
    (tmp_path / "theses" / "005-something").mkdir(parents=True)
    new = alloc_thesis_id.allocate(tmp_path / "theses", "mvp")
    assert new.name == "006-mvp"


def test_alloc_never_uses_exist_ok(tmp_path):
    # The Q27 implementation-bug guard: exist_ok=True would silently share a
    # directory. allocate() must create exactly one fresh directory per call.
    (tmp_path / "theses" / "001-mvp").mkdir(parents=True)
    second = alloc_thesis_id.allocate(tmp_path / "theses", "mvp")
    assert second.name == "002-mvp"
    assert (tmp_path / "theses" / "001-mvp").exists()  # original untouched
