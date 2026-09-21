"""test_migrate_artifacts.py — FR-042's migration, verified against a fixture workspace.

spec 058 T023, and the three things it must prove:

  * **dry run is the default and a needed rewrite is an exit code** — a migration that
    reports success while a workspace still needs migrating is the defect class this whole
    specification exists to remove, so the first assertion is that a dry run does NOT write
    (byte comparison, not a return value);
  * **it is idempotent** — the second run finds nothing and changes nothing;
  * **it never invents a value** — a field it cannot derive is reported as needing a human
    and left absent, because `facts_count: 0` written by a migration is indistinguishable
    from a counted zero, and that indistinguishability is the thing being removed.

`FR-042` also says the migration must never touch the B/ workspaces. That is asserted at the
end against the real workspace, read-only, and skipped where it is not mounted.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
SCRIPT = KIT / "scripts" / "migrate_artifacts.py"
WORKSPACE = Path("/Users/frank/B/agentii-space-tech-SPCX")

ART = """---
ticker: FLY
as_of: 2026-09-20
constitution_pin: v1.2.0
---

# FLY — competitive

Two [FACT] badges here: one [FACT] and two [FACT].

See ([📄 FLY 10-K p.12](https://agentii.ai/v/FLY/sec101/12)).
"""


def _ws(tmp_path: Path, name: str = "005-demo/artifacts/FLY/2026-09-20_competitive_methodology.md",
        text: str = ART) -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_a_dry_run_reports_and_writes_nothing(tmp_path):
    """The default must not write. Asserted by BYTES, because a script that wrote and then
    printed a dry-run summary would pass a return-value check."""
    art = _ws(tmp_path)
    before = _sha(art)
    res = _run(str(tmp_path))
    out = res.stdout + res.stderr
    assert res.returncode == 1, f"a workspace needing migration exited 0:\n{out}"
    assert _sha(art) == before, "THE DRY RUN WROTE TO THE FILE"
    assert "DRY RUN" in out and "--apply" in out, out
    assert "+ date: '2026-09-20'" in out, f"the plan does not show the derived value:\n{out}"
    assert "the `YYYY-MM-DD` prefix of the filename" in out, (
        f"the plan does not name the derivation, so a reader cannot audit what was "
        f"invented (nothing) versus derived:\n{out}")


def test_apply_adds_only_the_derivable_fields(tmp_path):
    """The existing keys survive unchanged and the new ones are added — nothing else.

    Asserted as "the original mapping is a SUBSET of the result", which is the invariant
    that matters and is robust to YAML's own typing (`as_of: 2026-09-20` parses as a
    `date`, not a `str` — the first version of this test compared it to a string and was
    wrong about the artifact, not about the migration).
    """
    art = _ws(tmp_path)
    before = yaml.safe_load(art.read_text().split("---", 2)[1])
    res = _run(str(tmp_path), "--apply")
    assert res.returncode == 1, (
        "the run should still exit 1: `conclusions` and `key_metrics` need a human")
    fm = yaml.safe_load(art.read_text().split("---", 2)[1])
    for k, v in before.items():
        assert fm.get(k) == v, f"the migration changed an existing key {k!r}: {v!r} -> {fm.get(k)!r}"
    assert fm["date"] == "2026-09-20", fm
    assert fm["affix"] == "methodology", fm
    assert fm["citation_count"] == 1, fm
    assert fm["facts_count"] == 3, f"the [FACT] count is wrong: {fm}"
    assert "conclusions" not in fm and "key_metrics" not in fm, (
        f"a field a migration cannot derive was written anyway: {fm}")


def test_it_is_idempotent(tmp_path):
    """FR-042's own standard. A second apply must be a no-op, byte for byte — for the
    fields it owns; the human fields keep it exiting 1, which is a different statement."""
    art = _ws(tmp_path)
    _run(str(tmp_path), "--apply")
    once = _sha(art)
    res = _run(str(tmp_path), "--apply")
    assert _sha(art) == once, "the second run changed the file"
    assert "APPLIED 0 rewrite(s)" in (res.stdout + res.stderr), (
        f"the second run claimed work:\n{res.stdout}{res.stderr}")
    # And a dry run over the same tree proposes nothing.
    res2 = _run(str(tmp_path), "--fields", "date,affix,citation_count,facts_count")
    assert res2.returncode == 0, (
        f"a fully-migrated artifact still needed a rewrite:\n{res2.stdout}{res2.stderr}")


def test_an_underivable_field_is_reported_never_written(tmp_path):
    art = _ws(tmp_path)
    res = _run(str(tmp_path), "--apply", "--fields", "conclusions")
    out = res.stdout + res.stderr
    assert res.returncode == 1, f"an underivable field did not fail:\n{out}"
    assert "MANUAL" in out and "cannot write one" in out, out
    assert yaml.safe_load(art.read_text().split("---", 2)[1]).get("conclusions") is None, (
        "the migration invented a value for a field it cannot derive")


def test_non_artifact_files_are_not_touched(tmp_path):
    """The population rule, shared with the citation gate: `plan.md` is the workspace's own
    document, not a skill's output, and a migration that rewrote it would be editing
    somebody's plan."""
    plan = tmp_path / "005-demo" / "plan.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text("---\ntitle: the plan\n---\n\nNo artifact fields here.\n")
    art = _ws(tmp_path)
    res = _run(str(tmp_path), "--apply")
    out = res.stdout + res.stderr
    assert "plan.md" not in out, f"the migration touched a non-artifact:\n{out}"
    assert yaml.safe_load(plan.read_text().split("---", 2)[1]) == {"title": "the plan"}


def test_an_unknown_field_is_refused_by_name(tmp_path):
    _ws(tmp_path)
    res = _run(str(tmp_path), "--fields", "fact_count")     # typo for facts_count
    out = res.stdout + res.stderr
    assert res.returncode == 2, out
    assert "unknown field" in out and "fact_count" in out, out


def test_an_empty_tree_is_not_a_clean_migration(tmp_path):
    """Zero surface must not read as success — the same rule as everywhere else here."""
    (tmp_path / "empty").mkdir()
    res = _run(str(tmp_path / "empty"))
    out = res.stdout + res.stderr
    assert res.returncode == 1, out
    assert "no artifact examined" in out, out


@pytest.mark.skipif(not (WORKSPACE / "theses").is_dir(),
                    reason="the read-only SPACX workspace is not mounted")
def test_it_never_mutates_the_b_workspaces():
    """FR-042's hard constraint, and the one that matters most: a dry run over the REAL
    workspace must leave every artifact's bytes and mtime untouched. The scan is read-only
    by construction (nothing writes without `--apply`) — this is the assertion that keeps
    it that way if someone later reorders `main`."""
    import os
    root = WORKSPACE / "theses"
    arts = [p for p in sorted(root.rglob("*.md")) if "artifacts" in p.parts][:40]
    assert arts, "the fixture found no artifacts — the path rule is wrong"
    before = {p: (_sha(p), os.stat(p).st_mtime_ns) for p in arts}
    res = _run(str(root))
    assert res.returncode in (0, 1), f"unexpected exit: {res.stdout}{res.stderr}"
    for p, (sha, mtime) in before.items():
        assert _sha(p) == sha, f"the dry run mutated {p}"
        assert os.stat(p).st_mtime_ns == mtime, f"the dry run touched the mtime of {p}"
