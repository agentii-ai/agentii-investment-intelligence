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
    """A minimal copy of the package sufficient to run check.py."""
    dst = tmp_path / "pkg"
    # Copy only what check.py touches to keep the fixture fast.
    for sub in ["scripts", "contracts", "plugins", "managed-agent-cookbooks"]:
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
