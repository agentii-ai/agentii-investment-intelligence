"""T016 — tests for check.py spec-039 extensions (write FIRST).

Check 30 (Registry Sync): bijection between on-disk skills (dirs with SKILL.md)
and skill-registry.yaml entries — a fake on-disk skill with no registry entry
fails; an orphan registry entry with no dir fails.

License-boundary sub-check: importing a copyleft (AGPL/GPL) package into
data-tools/ trips the denylist.

These run check.py in a copied sandbox so the real tree is never mutated.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_check(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "check.py")],
        capture_output=True,
        text=True,
        cwd=str(root),
    )


@pytest.fixture
def sandbox(tmp_path):
    """A minimal copy of the package sufficient to run check.py.

    `.claude-plugin` is part of "sufficient": section 7 ("marketplace source paths
    resolve") reads `.claude-plugin/marketplace.json`, and since spec 058 T002 a
    section that examines zero files fails the gate (FR-006). Omitting it made the
    sandbox a package with no marketplace manifest — a state the real kit is never
    in — so the fixture was incomplete, not the gate too strict.

    `data-tools` is part of "sufficient" for the same reason, added 2026-09-21 when
    the 2026-09-21 audit found Check 30b and Check 35 among the blocks that never
    registered a surface. Both are now counted sections, so in a sandbox without
    `data-tools/` they would report zero and fail — correctly, because `data-tools/`
    is TRACKED: its absence is a defect, unlike `packaging/targets/` (gitignored build
    output) and `theses/INDEX.md` (an uncommitted workspace), which are the two
    sections that declare themselves conditional instead.
    """
    dst = tmp_path / "pkg"
    # Copy only what check.py touches to keep the fixture fast.
    for sub in ["scripts", "contracts", "plugins", "managed-agent-cookbooks",
                ".claude-plugin", "data-tools"]:
        src = REPO_ROOT / sub
        if src.exists():
            shutil.copytree(src, dst / sub)
    # registry + schema live at root
    for f in ["skill-registry.yaml"]:
        if (REPO_ROOT / f).exists():
            shutil.copy2(REPO_ROOT / f, dst / f)
    return dst


def test_baseline_green(sandbox):
    """The unmodified sandbox must pass check.py (incl. Check 30)."""
    res = _run_check(sandbox)
    assert res.returncode == 0, f"baseline check.py failed:\n{res.stdout}\n{res.stderr}"


def test_a_conditional_section_reports_instead_of_passing_silently(sandbox):
    """FR-006's third state — dormant by construction must be SAYABLE.

    Two sections have no input in any clean checkout: Check 34 (a committed
    `theses/INDEX.md`) and T114 (gitignored `packaging/targets/`). Before 2026-09-21
    they reported no surface at all, which is indistinguishable from a pass. They now
    carry a standing notice, so a reader of ANY gate run learns which checks did not
    run — the same treatment `upstream_stale` gets under FR-040.
    """
    res = _run_check(sandbox)
    out = res.stdout + res.stderr
    assert res.returncode == 0, f"a conditional section failed the gate:\n{out}"
    assert "conditional:" in out, (
        "no conditional state was reported. The sandbox has no packaging/targets/ and no "
        f"theses/INDEX.md, so at least one section is dormant — silently:\n{out}"
    )
    assert "activates when that path appears" in out, out


def test_a_conditional_declaration_cannot_silence_a_present_input(sandbox):
    """The state's own guard: it is honoured ONLY while the path is absent.

    An empty `packaging/targets/` is the real-world shape of "someone made the directory
    and nothing built" — the build check examines 0 files and, before this rule, reported
    `0 expected, 0 stale-or-missing`, which reads as everything current. A marker that
    could silence that would be worse than no marker.
    """
    (sandbox / "packaging" / "targets").mkdir(parents=True)
    res = _run_check(sandbox)
    out = res.stdout + res.stderr
    assert res.returncode == 1, (
        f"an empty packaging/targets/ passed the build check and no error was raised:\n{out}"
    )
    assert "declared conditional" in out and "EXISTS" in out, (
        f"the failure did not name the conditional declaration as the cause:\n{out}"
    )


def test_check30_orphan_registry_entry_fails(sandbox):
    """A registry entry with no on-disk skill dir must fail Check 30."""
    reg = sandbox / "skill-registry.yaml"
    import yaml

    doc = yaml.safe_load(reg.read_text())
    doc["skills"].append(
        {
            "skill_name": "ghost-skill-xyz",
            "vertical": "equity-research-core",
            "layer_tags": ["L2"],
        }
    )
    reg.write_text(yaml.safe_dump(doc, sort_keys=False))
    res = _run_check(sandbox)
    assert res.returncode == 1
    assert "ghost-skill-xyz" in (res.stdout + res.stderr)


def test_check30_unregistered_ondisk_skill_fails(sandbox):
    """An on-disk skill with no registry entry must fail Check 30."""
    reg = sandbox / "skill-registry.yaml"
    import yaml

    doc = yaml.safe_load(reg.read_text())
    doc["skills"] = [s for s in doc["skills"] if s["skill_name"] != "business-model"]
    reg.write_text(yaml.safe_dump(doc, sort_keys=False))
    res = _run_check(sandbox)
    assert res.returncode == 1
    assert "business-model" in (res.stdout + res.stderr)


def test_license_boundary_denylist_trips(sandbox):
    """A data-tools/*.py that imports a copyleft package must fail the license check."""
    dt = sandbox / "data-tools"
    dt.mkdir(exist_ok=True)
    (dt / "bad_source.py").write_text("import openbb  # AGPL — must not be imported into MIT core\n")
    res = _run_check(sandbox)
    assert res.returncode == 1
    out = res.stdout + res.stderr
    assert "openbb" in out and ("license" in out.lower() or "copyleft" in out.lower())


def test_license_boundary_allows_permissive_import(sandbox):
    """A permissive import (yfinance) in data-tools/ must NOT trip the denylist."""
    dt = sandbox / "data-tools"
    dt.mkdir(exist_ok=True)
    (dt / "ok_source.py").write_text("import yfinance  # Apache-2.0 — fine\n")
    res = _run_check(sandbox)
    assert res.returncode == 0, f"permissive import wrongly failed:\n{res.stdout}\n{res.stderr}"
