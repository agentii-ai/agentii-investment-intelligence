"""Check 19's own self-test: the check that guards the trace-contract pair must be able to FAIL.

Why this file exists (2026-09-22, spec 060). Check 19 is the only executable guard on **two** of 060's
requirements — FR-202/FR-202a ("one place, and the pair agrees") and SC-205 — and until this file it had no
test of its own: `tests/` asserted that the sandbox passes `check.py` *wholesale* (`test_check_extensions.py`)
and that every CI script is invoked (`test_ci_script_coverage.py`), and neither of those can tell a check that
works from a check that cannot fail. The kit's own history says why that matters: v1.0 of Check 19 asserted
only that two files **exist**, and both existed while describing a mechanism (`agent_traces`, a Redis-minted
id, a per-call re-mint) the deployed MCP never had — a gate that verified presence while the behaviour
drifted. Each case below mutates one of the properties Check 19 claims to assert and requires the check to
report it, so the check's teeth are a test rather than a reading.

The mutations are the ones an editor would actually make: dropping the store's name, putting the retired
table back, shortening the member tuple, and restoring the two removed behaviours in the delivery contract.

Runs `check.py` in a copied sandbox (`tmp_path`), so the real tree is never mutated — same pattern as
`test_check_extensions.py`, whose fixture this one mirrors (including why the copy list must be "sufficient":
a section that examines zero files fails the gate by design, so a sandbox missing a tracked directory would
fail for the wrong reason).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HEADER = Path("contracts") / "x-agentii-trace-header.md"
DELIVERY = Path("contracts") / "x-agentii-trace-delivery.md"


def _run_check(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "check.py")],
        capture_output=True,
        text=True,
        cwd=str(root),
    )


@pytest.fixture
def sandbox(tmp_path) -> Path:
    """A copy of the package sufficient to run `check.py` — same list as `test_check_extensions.py`."""
    dst = tmp_path / "pkg"
    # `tests` and `.github` are in the list because check.py's script-coverage section (FR-003) reads the
    # CI definition to learn which scripts CI runs and then scans `tests/` to see which a test reaches —
    # a sandbox missing either reports scripts as uncovered and the *baseline* goes red for a reason that
    # has nothing to do with the contracts (measured here, and the same cause was fixed in
    # `test_check_extensions.py`'s fixture the same day).
    for sub in ["scripts", "contracts", "plugins", "managed-agent-cookbooks",
                ".claude-plugin", "data-tools", "tests", ".github"]:
        src = REPO_ROOT / sub
        if src.exists():
            shutil.copytree(src, dst / sub)
    for f in ["skill-registry.yaml"]:
        if (REPO_ROOT / f).exists():
            shutil.copy2(REPO_ROOT / f, dst / f)
    return dst


def _edit(root: Path, rel: Path, mutate) -> None:
    path = root / rel
    before = path.read_text()
    after = mutate(before)
    assert after != before, f"the mutation changed nothing in {rel} — the case would pass vacuously"
    path.write_text(after)


def _assert_check_19_reports(res: subprocess.CompletedProcess, needle: str) -> None:
    out = res.stdout + res.stderr
    assert res.returncode != 0, f"check.py passed with the contract broken:\n{out}"
    assert "agent tracing:" in out, f"the failure did not come from Check 19:\n{out}"
    assert needle in out, f"Check 19 failed for a different reason than expected:\n{out}"


def test_the_unmodified_sandbox_passes_with_no_check_19_error(sandbox):
    """The baseline: the contracts as shipped produce no Check-19 error.

    **Liveness is proven by the mutation cases below, not by a string here.** `_mark` records the surface a
    section examined into `SURFACES` and the default report prints counts, not section names — so
    grepping the output for "Check 19" would assert the report's formatting, not the check's existence.
    What actually proves the check runs is that each mutation of a property it claims to assert makes it
    fail: a dormant check cannot fail five different ways.
    """
    res = _run_check(sandbox)
    out = res.stdout + res.stderr

    assert res.returncode == 0, f"baseline check.py failed:\n{out}"
    assert "agent tracing:" not in out, out


def test_a_contract_that_omits_the_durable_store_fails(sandbox):
    """The store the record actually lands in, named positively (060 D-1)."""
    # Every occurrence, not the first: the contract names the store in more than one place, and
    # Check 19 asks whether it is named *at all*.
    _edit(sandbox, HEADER, lambda t: re.sub(r"usage_logs", "the durable store", t))
    _assert_check_19_reports(_run_check(sandbox), "does not name usage_logs")


def test_naming_the_retired_table_again_fails(sandbox):
    """`agent_traces` never existed; naming it again — even tautologically — re-teaches a reader to query it."""
    _edit(sandbox, HEADER, lambda t: t + "\n\n(The retired `agent_traces` table is not used.)\n")
    _assert_check_19_reports(_run_check(sandbox), "names the retired agent_traces table")


def test_a_shortened_member_tuple_fails(sandbox):
    """Four fields instead of five: the hot tier's shape is what a tree reconstruction parses."""
    _edit(sandbox, HEADER, lambda t: t.replace("agent|parent|instance|endpoint|status", "agent|parent|endpoint|status"))
    _assert_check_19_reports(_run_check(sandbox), "5-field member tuple")


def test_restoring_the_redis_mint_in_the_delivery_contract_fails(sandbox):
    """The per-call mint 060 removed: `INCR agentii:run_id_counter` is the sentence that rebuilt the defect."""
    _edit(sandbox, DELIVERY, lambda t: t + "\n\nThe server mints the id with `INCR agentii:run_id_counter`.\n")
    _assert_check_19_reports(_run_check(sandbox), "Redis INCR mint")


def test_restoring_auto_generation_of_a_missing_id_fails(sandbox):
    """The 'graceful degradation' paragraph, which invented an id for a caller that sent none (060 D-22)."""
    _edit(sandbox, DELIVERY, lambda t: t + "\n\nA missing run_id is auto-generated by the proxy.\n")
    _assert_check_19_reports(_run_check(sandbox), "auto-generating a missing run_id")
