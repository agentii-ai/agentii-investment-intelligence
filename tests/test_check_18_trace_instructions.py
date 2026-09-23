"""Check 18's own self-test: the guard on the tracing **instructions** must be able to FAIL.

Why this file exists (2026-09-23, spec 060's eleventh pass). Check 18 is the only executable guard on the
instruction every skill hands an agent about tracing (FR-106g(c)), and its first version asserted that a
`## Preflight` block *mentions* `X-Agentii-Trace` **or** `_run_id` — a keyword test. Under it, the retired
mechanism passed: five sources still taught "The MCP server will inject run_id, depth, and user_id
automatically" (the v1.0 story spec 060 D-22 removed, and FR-131/FR-204 forbid: depth is derived and
identity comes from the key), and one shipped skill wrapped its pointer across two lines in a way no
line-based migration could see. Neither was caught, because the check certified a sentence rather than its
truth — the failure mode this spec exists to remove, in the gate that guards the instructions.

Each case below mutates one property the hardened check claims to assert and requires a report:

  * the carry present in every `## Preflight` (the run id is minted once and the *caller* sends it onward);
  * the retired story absent from every Preflight **and** from the canonical sources an agent reads —
    the shipped agent prompt, the authoring template, the cookbook subagent prompt, the MCP trace note;
  * the generators that write the pointer agreeing with the template verbatim.

Runs `check.py` in a copied sandbox (`tmp_path`), so the real tree is never mutated — same fixture as
`test_check_19_trace_contracts.py`, including why the copy list must be sufficient (a section examining
zero files fails by design, so a sandbox missing a tracked directory would fail for the wrong reason).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = Path("plugins/vertical-plugins/models-and-pitches/skills/agentii/dcf/SKILL.md")
AGENT_PROMPT = Path("plugins/agent-plugins/agentii-equity-agent/agents/agentii-equity-agent.md")
TEMPLATE = Path("contracts/skill-methodology-template.md")
COOKBOOK = Path("managed-agent-cookbooks/agentii-equity-agent/subagents/system-prompts/retrieval.md")
GENERATOR = Path("scripts/scaffold_vertical.py")

CARRY = ("carry the `_run_id` from your first tool result"
         " and name yourself (and your parent, if you were spawned).")
RETIRED = "The MCP server will inject run_id, depth, and user_id automatically."


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


def _assert_check_18_reports(res: subprocess.CompletedProcess, needle: str) -> None:
    out = res.stdout + res.stderr
    assert res.returncode != 0, f"check.py passed with the instruction broken:\n{out}"
    assert "agent tracing:" in out, f"the failure did not come from Check 18:\n{out}"
    assert needle in out, f"Check 18 failed for a different reason than expected:\n{out}"


def test_the_unmodified_sandbox_passes_with_no_check_18_error(sandbox):
    """The baseline: the corpus as shipped produces no Check-18 error.

    Liveness is proven by the mutation cases below, not by a string here (a dormant check cannot fail
    four different ways): the report prints per-section counts, so grepping it for "Check 18" would
    assert the report's formatting rather than the check's existence.
    """
    res = _run_check(sandbox)
    out = res.stdout + res.stderr
    assert res.returncode == 0, f"baseline check.py failed:\n{out}"
    assert "agent tracing:" not in out, out


def test_a_preflight_that_names_the_header_without_the_carry_fails(sandbox):
    """The defect the pointer text had: it named the header and not the carry (spec 060 D-22)."""
    _edit(sandbox, SKILL, lambda t: t.replace(CARRY, ""))
    _assert_check_18_reports(_run_check(sandbox), "does not state the _run_id carry")


def test_a_preflight_teaching_the_retired_injection_fails(sandbox):
    """The v1.0 story the check used to wave through: a keyword test certifies a sentence, not its truth."""
    _edit(sandbox, SKILL, lambda t: t.replace(CARRY, RETIRED))
    res = _run_check(sandbox)
    # Both halves fire — the carry is gone *and* a false claim is present; either alone is a failure and
    # the retired-mechanism report is the one this case is about.
    _assert_check_18_reports(res, "teaches the retired mechanism")


def test_the_canonical_agent_prompt_teaching_the_retired_injection_fails(sandbox):
    """The shipped prompt `contracts/preflight.md` names as canonical — the text an agent actually reads."""
    _edit(sandbox, AGENT_PROMPT,
          lambda t: t.replace("The server does not re-attach it to calls that arrive without one",
                              "The MCP server will inject run_id automatically"))
    _assert_check_18_reports(_run_check(sandbox), "the canonical agent prompt")


def test_the_cookbook_subagent_prompt_teaching_the_retired_injection_fails(sandbox):
    """The kit's only subagent instruction — where the parent= requirement reaches a spawned agent."""
    _edit(sandbox, COOKBOOK, lambda t: t + f"\n\n{RETIRED}\n")
    _assert_check_18_reports(_run_check(sandbox), "the cookbook subagent prompt")


def test_a_template_without_the_canonical_pointer_fails(sandbox):
    """The template is the sentence's home: without it the generators have nothing to agree with.

    Deleting the fenced pointer line (rather than editing it) is the mutation that reaches *this*
    property — the earlier draft of this case shortened the line instead, and the check failed through
    the generator assertion because the template's own prose still mentions `_run_id`, which is why the
    expected message here is the missing-pointer one.
    """
    _edit(sandbox, TEMPLATE, lambda t: t.replace(f"```\n{pointer_sentence(t)}\n```\n", ""))
    _assert_check_18_reports(_run_check(sandbox), "declares no canonical tracing pointer")


def pointer_sentence(text: str) -> str:
    """The template's canonical pointer line, as a reader of the file would copy it."""
    m = re.search(r"Include the `X-Agentii-Trace` header on every tool call[^\n]*", text)
    assert m, "the template carries no canonical tracing pointer to mutate"
    return m.group(0).strip()


def test_a_generator_that_writes_a_different_pointer_fails(sandbox):
    """One sentence, four writers: a generator that drifts silently rewrites the corpus back."""
    _edit(sandbox, GENERATOR, lambda t: re.sub(r" — carry the `_run_id`[^\n]*", "", t))
    _assert_check_18_reports(_run_check(sandbox), "differs from the template's")
