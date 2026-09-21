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
import shutil
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
    m = re.search(r"(\d+) file examination\(s\) in (\d+) section\(s\)", gate_output)
    assert m, f"the gate no longer reports its total surface:\n{gate_output[-2000:]}"
    assert int(m.group(1)) > 1000, (
        f"the gate examined only {m.group(1)} — it reported 708 before T001 made every "
        f"section count its surface, so a number near that means the fix regressed"
    )
    assert int(m.group(2)) >= 30, (
        f"the surface table has only {m.group(2)} section(s). The 2026-09-21 audit found "
        f"nine executing blocks in check.py that registered no row at all — they were "
        f"invisible, and their counts were attributed to whichever section DID register "
        f"one. A table that shrinks means that has happened again (FR-006, SC-009)"
    )


def test_no_section_reports_an_uncovered_zero_surface(gate_output):
    """T001/T002 / FR-006 — zero is either covered by a pending declaration or fatal."""
    assert "NO SURFACE REPORTED" not in gate_output, (
        "a section stopped reporting its surface; FR-006 requires it to fail instead:\n"
        + "\n".join(l for l in gate_output.splitlines() if "NO SURFACE" in l)
    )


def _unmarked_blocks(src: str) -> list[str]:
    """Executing top-level blocks in `check.py`'s source that register no surface.

    A block is the span between two `# --- ` / `# === ` headers. It is EXEMPT if it is
    comment-only (the reclaimed-number notes are this shape) or if it is the report
    block — the surface table is the instrument, not a section.
    """
    lines = src.splitlines()
    header = re.compile(r"^# (?:---|===)\s*(\S.*)$")
    mark = re.compile(r"^\s*_mark\(")

    heads = [(i, header.match(l).group(1)) for i, l in enumerate(lines) if header.match(l)]
    out: list[str] = []
    for n, (i, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        if "report" in title.lower():
            continue
        body = lines[i + 1:end]
        if not any(l.strip() and not l.lstrip().startswith("#") for l in body):
            continue
        if not any(mark.match(l) for l in body):
            out.append(f"line {i + 1}: {title}")
    return out


def test_every_executing_block_in_check_py_registers_a_surface():
    """FR-006 / SC-009 — the control. Without this, an unmarked block is invisible.

    The 2026-09-21 audit found NINE executing blocks that registered no row: Check 29's
    own loop, the twelve Phase-28 context gates, Checks 30, 30b, 31, 32, 33, 34, 35, T114
    and Check 52. Attribution here is by `checked` delta, so each of their counts was
    attributed to the nearest PRECEDING mark: the row labelled "Check 29: Output
    Structure gate" was provably 1 (Check 30, the registry file) + 12 (Check 30b, the
    `data-tools/*.py` files), while Check 29's own traversal — the same `SKILL_FILES`
    collection whose other row reads 149 — contributed nothing. `NO SURFACE REPORTED`
    cannot see any of that, because a block that never marks never produces the phrase.

    So the rule and the instrument have to be able to disagree, which is what this test
    is: it compares the block population against the marks, structurally.
    """
    src = (KIT / "scripts" / "check.py").read_text(encoding="utf-8")
    heads = len(re.findall(r"(?m)^# (?:---|===)\s*\S", src))
    assert heads > 20, f"check.py's section headers no longer parse ({heads} found)"

    unmarked = _unmarked_blocks(src)
    assert not unmarked, (
        "executing block(s) in check.py with no surface mark. Their examined count is "
        "attributed to the section above them, and a section that examines nothing here "
        "cannot fail — which is FR-006's defect inside the mechanism that enforces "
        "FR-006:\n  " + "\n  ".join(unmarked) + "\n"
        "Fix: add `_mark('<name>')` and count what the block reads. If it is dormant by "
        "construction, pass `conditional='<path>'` (honoured only while that path is "
        "absent); if it is blocked on unfinished work, declare it in "
        "contracts/pending.yaml (FR-054)."
    )


def _uncounted_walks(src: str) -> list[str]:
    """Marked blocks that walk a file collection without counting what they walked.

    The OTHER half of the 2026-09-21 finding, and the half `_unmarked_blocks` cannot
    see: Check 29 HAD a `_mark` and never incremented `checked` inside
    `for sk in SKILL_FILES`, so its row reported the next two blocks' files (1 + 12) and
    read as a perfectly normal row. A marked section with a plausible number is
    indistinguishable from a marked section with a correct one — which is why the
    check that catches it has to be about the shape, not the output.

    Narrow on purpose: only the two module-level file collections and explicit
    `glob(`/`rglob(` calls. A broader "iterates anything" rule would flag Check 33's
    taxonomy axes and be wrong often enough to get switched off.
    """
    lines = src.splitlines()
    header = re.compile(r"^# (?:---|===)\s*(\S.*)$")
    walk = re.compile(r"for\s+\w+\s+in\s+(?:sorted\()?(?:SKILL_FILES|COMMAND_FILES)\b"
                      r"|\.(?:rglob|glob)\(")
    count = re.compile(r"^\s*checked\s*\+=")

    heads = [(i, header.match(l).group(1)) for i, l in enumerate(lines) if header.match(l)]
    out: list[str] = []
    for n, (i, title) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        if "report" in title.lower():
            continue
        body = lines[i + 1:end]
        if not any(walk.search(l) for l in body):
            continue
        if not any(count.match(l) for l in body):
            out.append(f"line {i + 1}: {title}")
    return out


def test_every_block_that_walks_a_collection_counts_it():
    """FR-006 — a section that walks files must report how many it walked."""
    src = (KIT / "scripts" / "check.py").read_text(encoding="utf-8")
    uncounted = _uncounted_walks(src)
    assert not uncounted, (
        "section(s) walk a file collection and count none of it. The row still shows a "
        "number — the neighbouring block's — so nothing about the output looks wrong:\n  "
        + "\n  ".join(uncounted) + "\n"
        "Fix: `checked += 1` per file walked, or a single `checked += len(<collection>)` "
        "if the section re-walks the same collection (the Phase 28 block's convention)."
    )


def test_the_uncounted_walk_detector_actually_fires():
    """The control's control, again — and it must reproduce the REAL Check 29.

    The pre-058 revision is the strongest available fixture: its Check 29 iterates
    `SKILL_FILES` and counts nothing, and that is the exact block whose row the audit
    found reporting 1 + 12 files belonging to Checks 30 and 30b.
    """
    synthetic = (
        "# --- Check 1: walks and counts ---\n"
        "_mark('Check 1')\n"
        "for sk in SKILL_FILES:\n"
        "    checked += 1\n"
        "\n"
        "# --- Check 2: walks, counts nothing (Check 29's real defect) ---\n"
        "_mark('Check 2')\n"
        "for sk in SKILL_FILES:\n"
        "    err('read, and never counted')\n"
        "\n"
        "# --- report ---\n"
        "print('the instrument itself')\n"
    )
    found = _uncounted_walks(synthetic)
    assert len(found) == 1, found
    assert found[0].startswith("line 6: Check 2:"), found

    old = subprocess.run(["git", "show", "1a2d679^:scripts/check.py"],
                         capture_output=True, text=True, cwd=str(KIT))
    if old.returncode == 0 and old.stdout:
        real = _uncounted_walks(old.stdout)
        assert any("Check 29" in r for r in real), (
            "the detector does not reproduce Check 29 in the pre-058 revision — the block "
            f"whose row reported Checks 30/30b's files. Found: {real}"
        )


def test_the_unmarked_block_detector_actually_fires():
    """The control's control. `test_every_executing_block…` passes on today's file, and
    a detector that returned `[]` unconditionally would pass it identically — the same
    hollow-test defect FR-004 names. This feeds it the shape it exists to catch, and the
    pre-fix shape it was written against."""
    synthetic = (
        "# --- Check 1: fine ---\n"
        "_mark('Check 1')\n"
        "for x in THINGS:\n"
        "    checked += 1\n"
        "\n"
        "# --- Check 2: never marked (the 2026-09-21 defect) ---\n"
        "for x in THINGS:\n"
        "    err('this runs and reports no surface')\n"
        "\n"
        "# --- report ---\n"
        "print('the instrument itself')\n"
    )
    found = _unmarked_blocks(synthetic)
    assert len(found) == 1, found
    assert found[0].startswith("line 6: Check 2:"), found
    assert "Check 1" not in found[0], (
        f"the detector flagged the MARKED block as well — it is not discriminating: {found}"
    )

    # And a real pre-fix revision, if this checkout is a git clone with that history: the
    # commit BEFORE spec 058's phase-1 work. It must find the defect there too — on a
    # whole real file, not a three-line fixture.
    old = subprocess.run(["git", "show", "1a2d679^:scripts/check.py"],
                         capture_output=True, text=True, cwd=str(KIT))
    if old.returncode == 0 and old.stdout:
        assert len(_unmarked_blocks(old.stdout)) >= 8, (
            "the detector found fewer than 8 unmarked blocks in the pre-058 check.py. "
            "The 2026-09-21 audit found nine in the version it examined, so a number "
            "this low means the detector is not seeing the defect it exists for"
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


def test_the_gate_field_check_fires_on_an_undeclared_read(tmp_path):
    """T015 / FR-037 — the contract check must fail, not just pass.

    `entity_claims` was read by five gates and absent from 128 artifacts, and nothing
    reported it, because nothing compared the reads against a declaration. This asserts
    the comparison exists AND bites: a field a gate reads but the contract does not
    declare must fail the check, naming both.

    It also pins the detector's blind spots, because each was a real bug in it: it must
    resolve loop constants (`for pin in FIVE_PINS`), generator expressions
    (`any(... for p in CONST)`), and inline tuple literals (`for f in ("a","b")`) — the
    three forms under which a real read stayed invisible while the check reported OK.
    """
    pkg = tmp_path / "pkg"
    for sub in ["scripts", "contracts"]:
        shutil.copytree(KIT / sub, pkg / sub)
    gate = pkg / "scripts" / "g1_gate.py"
    gate.write_text(gate.read_text().replace(
        '    if not fm.get("mode"):',
        '    _t = fm.get("totally_undeclared_field")\n    if not fm.get("mode"):', 1))

    res = subprocess.run([sys.executable, str(pkg / "scripts" / "check_gate_fields.py")],
                         capture_output=True, text=True, cwd=str(pkg))
    out = res.stdout + res.stderr
    assert res.returncode != 0, f"an undeclared read did not fail the check:\n{out}"
    assert "totally_undeclared_field" in out, f"the check did not name the field:\n{out}"
    assert "g1_gate.py" in out, f"the check did not name the script:\n{out}"


def test_the_gate_population_is_derived_not_asserted_by_its_own_config(tmp_path):
    """FR-037 / the 2026-09-21 audit — a NEW gate cannot slip in undeclared.

    `contracts/artifact-frontmatter.yaml`'s `gates:` list is hand-maintained, so before
    this the check could only verify the scripts it was told about — the same shape as the
    surface table's missing rows: a rule whose population is asserted by its own config.
    The population is mechanical (a script that calls the shared parser reads artifact
    frontmatter), so it is now derived and diffed.

    The fixture is the real defect: a new script that reads a field, undeclared.
    """
    pkg = tmp_path / "pkg"
    for sub in ["scripts", "contracts"]:
        shutil.copytree(KIT / sub, pkg / sub)
    (pkg / "scripts" / "new_gate.py").write_text(
        "import g1_gate\n\n\n"
        "def check(path):\n"
        "    with open(path) as fh:\n"
        "        fm = g1_gate.parse_frontmatter(fh.read())\n"
        "    return fm.get('mode')\n"
    )

    res = subprocess.run([sys.executable, str(pkg / "scripts" / "check_gate_fields.py")],
                         capture_output=True, text=True, cwd=str(pkg))
    out = res.stdout + res.stderr
    assert res.returncode != 0, f"an undeclared new gate passed:\n{out}"
    assert "new_gate.py" in out, f"the check did not name the undeclared gate:\n{out}"
    assert "gates:" in out, f"the check did not say where to declare it:\n{out}"


def test_a_declared_dynamic_read_does_not_read_like_a_failure(tmp_path):
    """I6 / FR-037 — the two states must be distinguishable by their WORDS.

    A read whose field names the workspace supplies is ACCOUNTED FOR by `dynamic_reads`.
    The first version printed it under the heading "declared" while re-using the
    `unresolved` string verbatim — "no resolvable binding: not a known constant, no inline
    tuple, no `for field in <CONST>` in this file" — so the output claimed a read was
    unaccounted-for in the same sentence that filed it as accounted. `unresolved: 0` is
    only meaningful if a reader can tell the two apart without reading the source.
    """
    res = subprocess.run([sys.executable, str(KIT / "scripts" / "check_gate_fields.py")],
                         capture_output=True, text=True, cwd=str(KIT))
    out = res.stdout + res.stderr
    notes = [l for l in out.splitlines() if "declared-dynamic read:" in l]
    assert notes, f"no declared-dynamic read is reported at all:\n{out}"
    for line in notes:
        assert "ACCOUNTED FOR" in line, (
            f"a declared-dynamic read does not say it is accounted for:\n{line}")
        assert "no resolvable binding" not in line, (
            f"a declared-dynamic read is described in the words reserved for an "
            f"UNRESOLVED one — the states are indistinguishable again:\n{line}")


def test_the_gate_field_check_resolves_every_read_or_says_it_cannot(tmp_path):
    """The live contract must leave nothing unresolved.

    `unresolved: 0` has to mean "every read was accounted for", never "none were found".
    The contract carries a `dynamic_reads` list precisely so workspace-supplied field
    names are DECLARED rather than silently skipped.
    """
    res = subprocess.run([sys.executable, str(KIT / "scripts" / "check_gate_fields.py")],
                         capture_output=True, text=True, cwd=str(KIT))
    out = res.stdout + res.stderr
    assert "0 unresolved" in out, (
        f"a frontmatter read is neither declared nor a declared dynamic path:\n{out}"
    )
