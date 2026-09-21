"""test_ci_script_coverage.py — FR-003: the scripts CI runs are exercised here (T043).

WHAT COVERING THEM FOUND, which is the point of the task. Six `validate-*.py` scripts and
one shell script were run by CI and referenced by no test. Running them:

  * `validate-multi-ticker-syntax.py` **FAILS with 34 violations** — 20 of them the 10
    kit/orchestrator skills × 2 trees, whose `multi_ticker_semantics` is absent, which
    `check.py`'s Check 10 EXEMPTS them from by role filter; and 14 the bio-pharm skills
    whose value is `basket_v1_1`, "forbidden at v1.0 (FR-054b)";
  * `validate-prose-safety.py` **FAILS with 1** — a shell-variable form in
    `technical-analysis/skills/agentii/trade-execution/SKILL.md`;
  * `validate-telemetry-redaction.py` **passes having scanned 0 files** — "OK — 0 emission
    file(s) scanned". A check that examines nothing reports exactly what a satisfied check
    reports, which is the defect this specification exists to name.

So the kit's local gate is green while its CI is red. That is not a coincidence of
sequencing: `check.py` does not invoke these scripts, and nothing said so (T043).

The three live defects are pinned with `xfail(strict=True)` — the repository's own idiom for
a real, known failure. `strict=True` means the moment one is FIXED this file fails and the
marker must be removed, which is FR-005's discipline and T045's subject. The docstrings name
the defect and who owns the decision, so nobody has to rediscover it.

One decision deliberately NOT taken here: the kit-skill disagreement (`check.py:402` exempts
by role; the validator does not) is a **rule question**, not a bug to patch quietly — one of
the two is wrong and which one is the methodology owner's call. It is recorded, not resolved.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
SCRIPTS = KIT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_script_coverage as cov  # noqa: E402


def _run(name: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / name)],
                          capture_output=True, text=True, cwd=str(KIT))


# ── the gate's own rule, asserted over this repository ──────────────────────

def test_no_ci_run_script_is_uncovered():
    """T043 — the rule, over the kit. It was 7 before these tests existed."""
    problems, counts = cov.check()
    assert not problems, (
        "script(s) CI runs that no test reaches:\n  " + "\n  ".join(problems))
    assert len(counts["ci_run"]) >= 10, (
        f"only {len(counts['ci_run'])} CI-run script(s) found — the scan is broken, and a "
        f"gate over an empty population passes without meaning anything")


def test_the_coverage_gate_fires_on_an_uncovered_ci_script(tmp_path):
    """The negative fixture. Without it, a gate that found nothing would look identical."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "brand_new_check.py").write_text("print('hi')\n")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text(
        "jobs:\n  x:\n    steps:\n      - run: python3 scripts/brand_new_check.py\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_something.py").write_text("def test_x():\n    assert True\n")

    problems, counts = cov.check(root=tmp_path)

    assert counts["uncovered"] == ["brand_new_check.py"], counts
    assert any("brand_new_check.py" in p and "FR-003" in p for p in problems), problems


def test_a_docstring_mention_is_not_coverage(tmp_path):
    """The trap this gate fell into itself: `validate-citations.py`'s only "reference" was a
    sentence in another test's docstring. A mention is not a run, and a gate that counts
    mentions reports coverage it does not have."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "mentioned.py").write_text("print('hi')\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_m.py").write_text(
        '"""A docstring that mentions scripts/mentioned.py in prose."""\n\n\n'
        "def test_x():\n    assert True\n")
    # An explicit tests_dir, because the default-argument version of this function bound
    # the REAL tests/ at import time — and this very file mentions the fixture's name in a
    # code string, so the real tree counted as the reference. That is the self-reference
    # hazard in miniature, and it is why the root is a parameter now.
    assert cov.referenced_in_tests("mentioned.py", tmp_path / "tests") is False, (
        "a docstring mention was counted as a test reference")
    assert cov.referenced_in_tests("mentioned.py", KIT / "tests") is True, (
        "the real tests/ does not reference the fixture name — this test can no longer "
        "tell the two cases apart")


# ── one test per CI-run script that had none ────────────────────────────────

def test_validate_citations_reports_its_surface_and_passes():
    res = _run("validate-citations.py")
    out = res.stdout + res.stderr
    assert res.returncode == 0, out
    m = re.search(r"(\d+) file\(s\) scanned", out)
    assert m and int(m.group(1)) > 100, (
        f"the scan reports no non-trivial surface, so 'clean' and 'examined nothing' are "
        f"indistinguishable here:\n{out}")


def test_validate_mode_syntax_reports_its_surface_and_passes():
    res = _run("validate-mode-syntax.py")
    out = res.stdout + res.stderr
    assert res.returncode == 0, out
    m = re.search(r"(\d+) skill\(s\) scanned", out)
    assert m and int(m.group(1)) >= 70, f"unexpected surface:\n{out}"


def test_validate_partner_plugin_passes():
    """Its contract is an exit code and a sentence; it reports NO surface count, which is
    worth knowing rather than asserting away — a check whose output cannot distinguish
    'clean' from 'examined nothing' is the shape T043 exists to surface."""
    res = _run("validate-partner-plugin.py")
    out = res.stdout + res.stderr
    assert res.returncode == 0, out
    assert "passed" in out, out


@pytest.mark.xfail(strict=True, reason=(
    "VACUOUS, not clean: validate-telemetry-redaction.py exits 0 having scanned ZERO "
    "emission files. A check that examined nothing reports exactly what a satisfied check "
    "reports, which is this specification's defect class — and unlike the two failures "
    "above, nothing here is wrong with a file: the SURFACE is empty and undeclared. Either "
    "the emission-file convention lands (spec 060 T024-T026, in flight) so there is "
    "something to scan, or the script declares its empty surface instead of reporting OK. "
    "Remove this marker when the scan reports a non-zero surface."))
def test_validate_telemetry_redaction_scans_a_real_surface():
    res = _run("validate-telemetry-redaction.py")
    out = res.stdout + res.stderr
    scanned = re.search(r"(\d+) emission file\(s\) scanned", out)
    assert res.returncode == 0, out
    assert scanned and int(scanned.group(1)) > 0, (
        f"the scan still examines nothing, so its OK is arithmetically forced:\n{out}")


@pytest.mark.xfail(strict=True, reason=(
    "LIVE CI FAILURE: 34 multi-ticker violations, in two groups. (1) 20 = the 10 "
    "kit/orchestrator skills x 2 trees have no `multi_ticker_semantics`; check.py's Check "
    "10 exempts them by ROLE FILTER (check.py:402) while this validator does not — the two "
    "disagree about one rule, and which is right is the methodology owner's decision, not a "
    "patch. (2) 14 = the 7 bio-pharm skills x 2 trees carry `basket_v1_1`, 'forbidden at "
    "v1.0 (FR-054b)' — spec 055's content. Remove this marker when both are resolved."))
def test_validate_multi_ticker_syntax_passes():
    res = _run("validate-multi-ticker-syntax.py")
    assert res.returncode == 0, (res.stdout + res.stderr)[-2000:]


@pytest.mark.xfail(strict=True, reason=(
    "LIVE CI FAILURE: one prose-safety violation — a shell-variable form `$X` in "
    "plugins/vertical-plugins/technical-analysis/skills/agentii/trade-execution/SKILL.md. "
    "Remove this marker when the line is fixed."))
def test_validate_prose_safety_passes():
    res = _run("validate-prose-safety.py")
    assert res.returncode == 0, (res.stdout + res.stderr)[-2000:]


def test_test_cookbooks_skips_explicitly_never_silently():
    """The seventh uncovered CI-run script, and the only shell one. Its contract is already
    the right shape: every cookbook is either validated or NAMED as skipped — and the skips
    are the declared-pending state (`contracts/pending.yaml` P1, section 8).

    Asserted as "every cookbook line is an explicit outcome", because a script that silently
    skipped an unpopulated cookbook would return 0 and read as fully validated."""
    res = subprocess.run(["bash", str(SCRIPTS / "test-cookbooks.sh")],
                         capture_output=True, text=True, cwd=str(KIT))
    out = res.stdout + res.stderr
    assert res.returncode == 0, out
    cookbooks = [d.name for d in (KIT / "managed-agent-cookbooks").iterdir() if d.is_dir()]
    if cookbooks:
        silent = [c for c in cookbooks if c not in out]
        assert not silent, (
            f"cookbook(s) produced no outcome line at all — neither validated nor named as "
            f"skipped, which is a silent pass:\n{silent}\n{out}")
    assert "skip" in out or "OK" in out or "PASS" in out, (
        f"the script reported nothing recognisable:\n{out}")
