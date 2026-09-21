"""test_phase1_invariants.py — spec 058 T012: what Phase 1 established, held.

Phase 1 fixed six states that had no guard. Each is asserted here, because every one
of them regressed silently before: a section stopped reporting its surface, a check
number came back into the inventory, a custom marker went unregistered, an install got
committed again, an empty directory shipped. None of those produced a failing gate.

The tasks that made these true are T001–T003, T008–T010, T013. This file is what makes
them stay true — the difference between a repair and a control.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
BUILT = {"plugins", "packaging", "node_modules", ".venv", ".git", ".turbo"}

# pytest's own markers: registered by pytest, not by us (FR-011 is about CUSTOM ones).
BUILTIN_MARKERS = {"parametrize", "skip", "skipif", "xfail", "usefixtures", "filterwarnings"}


@pytest.fixture(scope="module")
def gate_output() -> str:
    """One gate run, shared — check.py takes ~10s and several tests read its output."""
    res = subprocess.run(
        [sys.executable, str(KIT / "scripts" / "check.py"), "--surfaces"],
        capture_output=True, text=True, cwd=str(KIT),
    )
    return res.stdout + res.stderr


def test_the_gate_is_green_and_checks_a_non_trivial_surface(gate_output):
    """T013 / FR-008 / SC-010 — and the coverage figure, not just the exit code.

    The second assertion is the one that matters: before T001 the gate reported
    `708 file(s)`, because it only counted the sections that bothered to. A green gate
    over a misreported surface is this specification's defect with a checkmark on it.
    """
    assert "0 issues" in gate_output, gate_output[-2000:]
    m = re.search(r"(\d+) file\(s\) checked", gate_output)
    assert m, f"the gate no longer reports its total surface:\n{gate_output[-2000:]}"
    assert int(m.group(1)) > 1000, (
        f"the gate examined only {m.group(1)} files — it reported 708 before T001 made "
        f"every section count its surface, so a number near that means the fix regressed"
    )


def test_no_section_reports_an_uncovered_zero_surface(gate_output):
    """T001/T002 / FR-006 — zero is either covered by a pending declaration or fatal."""
    assert "NO SURFACE REPORTED" not in gate_output, (
        "a section stopped reporting its surface; FR-006 requires it to fail instead:\n"
        + "\n".join(l for l in gate_output.splitlines() if "NO SURFACE" in l)
    )


def test_no_retired_check_number_is_counted_as_a_check(gate_output):
    """T003 / FR-007 — 14 was retired and 15–17 reserved; all four are reclaimed.

    FR-007's exact words: a number that examines nothing MUST NOT be counted as a
    check. Naming them in the inventory is counting them.
    """
    counted = [l for l in gate_output.splitlines()
               if re.match(r"^\s+\d+\s+Check (14|15|16|17)\b", l)]
    assert not counted, f"retired/reserved numbers are back in the inventory:\n{counted}"


def test_every_custom_pytest_marker_is_registered():
    """T008 / FR-011 — `smoke` was used in two files and declared in none."""
    declared = set()
    ini = (KIT / "pytest.ini").read_text()
    for m in re.finditer(r"^\s{4}([a-z_][a-z0-9_]*):", ini, re.M):
        declared.add(m.group(1))
    used: set[str] = set()
    for f in (KIT / "tests").rglob("test_*.py"):
        used |= set(re.findall(r"pytest\.mark\.([a-z_][a-z0-9_]*)", f.read_text()))
    unregistered = used - declared - BUILTIN_MARKERS
    assert not unregistered, (
        f"custom marker(s) used but not registered in pytest.ini: {sorted(unregistered)} "
        f"— pytest emits PytestUnknownMarkWarning and the marker selects nothing (FR-011)"
    )


def test_no_local_install_is_committed():
    """T009 / FR-009 — the kit's `.claude/` held 48 SKILL.md against 80 canonical.

    Removed from version control; `.claude/skills/` and `.claude/commands/` are now
    gitignored so a local install cannot be committed again. Both halves are asserted,
    because removing the files without the ignore rule invites the same commit back.
    """
    tracked = subprocess.run(
        ["git", "ls-files", ".claude/"], capture_output=True, text=True, cwd=str(KIT),
    ).stdout.split()
    assert not tracked, (
        f"a local install is committed again ({len(tracked)} file(s)): {tracked[:5]} "
        f"— FR-009: it must match the canonical counts or stay out of version control"
    )
    ignored = subprocess.run(
        ["git", "check-ignore", ".claude/skills/x", ".claude/commands/y"],
        capture_output=True, text=True, cwd=str(KIT),
    ).stdout.split()
    assert len(ignored) == 2, (
        "the install paths are no longer gitignored, so the removal is not durable: "
        f"check-ignore returned {ignored}"
    )


def test_no_empty_directory_in_the_shipped_tree():
    """T010 / FR-010 — `cli-surfaces/` contained 0 files and shipped anyway.

    Scoped to the plugin tree (the shipped surface) and to directories git would carry;
    build output under `packaging/` is gitignored and legitimately sparse mid-build.
    """
    empty = []
    for d in (KIT / "plugins").rglob("*"):
        if not d.is_dir():
            continue
        if any(d.iterdir()):
            continue
        empty.append(str(d.relative_to(KIT)))
    assert not empty, (
        f"empty directory/directories in the shipped tree: {empty} "
        f"— FR-010: a directory with no files is a declaration of structure with no "
        f"content behind it"
    )
