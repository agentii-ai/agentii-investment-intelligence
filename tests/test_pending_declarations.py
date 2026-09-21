"""test_pending_declarations.py — spec 058 T011/T012: the deferral mechanism's teeth.

`contracts/pending.yaml` lets a check whose input does not exist yet say so — with a
named owner and a date — instead of either failing (wrong: the check is correct, its
subject is absent) or reporting a clean surface (wrong: a vacuous section must never
read as productive). It reconciles FR-006 with SC-010.

**Every test here drives the FAILURE path.** A mechanism that only ever passes is the
defect this whole specification exists to remove, and this one shipped with a live
example of it: the first version of the loader called `err()` before `err()` was
defined, so on an expired entry check.py crashed with `NameError` rather than reporting
the expiry. The happy path ran fine and hid it. That crash is why these tests exist —
each of the four invalid states below was, at some point, silently unreachable.

The sandbox copies only `scripts/` and `contracts/`, which is enough: check.py reports
many other errors without `plugins/`, and each test asserts on its OWN message rather
than on the exit code.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PENDING = REPO_ROOT / "contracts" / "pending.yaml"


def _sandbox(tmp_path: Path) -> Path:
    """`scripts/` + `contracts/`, plus the trees check.py walks as EMPTY dirs.

    Empty is deliberate: it keeps the fixture fast (no 80-skill copy) and it gives
    section 8 a zero surface, which is the state under test. Without the empty dirs
    check.py raises before reaching the reporting block.
    """
    dst = tmp_path / "pkg"
    for sub in ["scripts", "contracts"]:
        shutil.copytree(REPO_ROOT / sub, dst / sub)
    for sub in ["plugins", "managed-agent-cookbooks"]:
        (dst / sub).mkdir(exist_ok=True)
    (dst / "skill-registry.yaml").write_text("skills: []\n")
    return dst


def _run(root: Path) -> str:
    res = subprocess.run(
        [sys.executable, str(root / "scripts" / "check.py")],
        capture_output=True, text=True, cwd=str(root),
    )
    return res.stdout + res.stderr


def _edit(root: Path, old: str, new: str) -> None:
    p = root / "contracts" / "pending.yaml"
    text = p.read_text()
    assert old in text, f"fixture drift: {old!r} is not in pending.yaml"
    p.write_text(text.replace(old, new, 1))


def test_a_missing_pending_file_is_not_an_error(tmp_path):
    """A kit with no pending.yaml has nothing deferred — that is a valid state."""
    root = _sandbox(tmp_path)
    (root / "contracts" / "pending.yaml").unlink()
    out = _run(root)
    assert "pending:" not in out, f"absent pending.yaml must not be reported:\n{out}"


def test_an_expired_declaration_fails(tmp_path):
    """FR-054: reaching expiry MUST fail, not warn.

    This is the mechanism's whole point — without it a deferral is permanent, and a
    temporary scaffold becomes the architecture.
    """
    root = _sandbox(tmp_path)
    _edit(root, "expires: 2026-12-31", "expires: 2026-01-01")
    out = _run(root)
    assert "EXPIRED 2026-01-01" in out, f"an expired declaration did not fail:\n{out}"


def test_a_declaration_without_an_owner_fails(tmp_path):
    """FR-054: owner and expiry are both required — a deferral nobody owns is not one."""
    root = _sandbox(tmp_path)
    # Replace the WHOLE line: a prefix-only edit leaves the trailing parenthetical and
    # produces invalid YAML, which fails for the wrong reason (an unparseable file) and
    # would make this test pass while proving nothing about the owner check.
    _edit(root, "owner: spec 046 US7 (managed-agent cookbook authoring)", "owner: ''")
    out = _run(root)
    assert "missing owner" in out, f"an ownerless declaration did not fail:\n{out}"


def test_an_unparseable_expiry_fails(tmp_path):
    root = _sandbox(tmp_path)
    _edit(root, "expires: 2026-12-31", "expires: next quarter")
    out = _run(root)
    assert "is not an ISO date" in out, f"a non-ISO expiry did not fail:\n{out}"


def test_a_subject_nothing_consults_fails(tmp_path):
    """A declaration no check reads cannot expire usefully — FR-040's defect.

    The same shape as `upstream_stale`: a field that records a condition and triggers
    nothing is a comment, not a control.
    """
    root = _sandbox(tmp_path)
    _edit(root, "subject: check:8", "subject: check:999")
    out = _run(root)
    assert "nothing consults" in out, f"an unconsumed subject did not fail:\n{out}"


def test_a_zero_surface_section_fails_when_not_declared_pending(tmp_path):
    """T002/FR-006: a section that examined nothing must fail and name itself.

    Removing the deferral leaves section 8 with a zero surface and no cover, which is
    exactly the state FR-006 says must not read as clean.
    """
    root = _sandbox(tmp_path)
    (root / "contracts" / "pending.yaml").unlink()
    out = _run(root)
    assert "examined 0 files" in out, f"an undeclared zero surface did not fail:\n{out}"


def test_the_live_declaration_covers_its_section(tmp_path):
    """The real pending.yaml must keep section 8 covered and the gate reachable.

    A guard against the failure mode where the mechanism is built, the entry is
    written, and nothing actually consults it — which would leave the entry to expire
    into an unexplained red gate.
    """
    out = _run(REPO_ROOT)
    assert "pending: " not in out, f"the live declaration is malformed:\n{out[:2000]}"
    assert PENDING.is_file(), "contracts/pending.yaml is missing"
