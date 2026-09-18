"""L8: the price-tool surface the skills are promised vs. what the package exposes.

Covers D8 (no price tool in the registration manifest; `get_options_chain` is a
phantom referenced by three skills and defined nowhere) and D9 (every `early`-stage
skill fails the Q45 allowlist gate `g1_gate.check_market_data_allowlist`, which has
never been run against the real registry — only against synthetic inputs).

These tests bridge two repos that have never been checked against each other:
the package's `data-tools/` + `skill-registry.yaml`, and the installed skills'
`SKILL.md` frontmatter. That gap is where D8 and D9 live.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "data-tools"))

import mcp_adapters  # noqa: E402
import g1_gate  # noqa: E402

# The price tools that skills declare in `allowed_tools`.
DECLARED_PRICE_TOOLS = {"get_realtime_quote", "get_price_history", "get_options_chain"}

# Candidate locations for installed skill definitions, newest layout first.
SKILL_ROOTS = [
    Path.home() / ".claude" / "skills" / "agentii",
    Path.home() / ".claude" / "plugins" / "marketplaces" / "agentii-investment-intelligence"
    / "plugins" / "vertical-plugins",
]


def _skill_files() -> list[Path]:
    for root in SKILL_ROOTS:
        if root.is_dir():
            found = sorted(root.rglob("SKILL.md"))
            if found:
                return found
    return []


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError:
        return {}


def _registry() -> dict:
    path = REPO_ROOT / "skill-registry.yaml"
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


# --- D8: the manifest must expose the tools the skills are told to call -------

@pytest.mark.xfail(strict=True, reason=(
    "D8: mcp_adapters.REGISTRATION_MANIFEST exposes get_market_data (-> get_quote) "
    "but none of the tool names skills actually declare. 20 skills declare "
    "get_realtime_quote; get_price_history has no adapter at all despite being the "
    "early-stage tool the Q45 gate mandates."))
def test_manifest_exposes_the_declared_price_tools():
    """A skill whose allowed_tools names a tool the host never registers cannot
    work — it degrades to 'prompt the user for the price'."""
    exposed = set(mcp_adapters.REGISTRATION_MANIFEST)
    missing = DECLARED_PRICE_TOOLS - exposed
    assert not missing, (
        f"tools declared by skills but absent from REGISTRATION_MANIFEST: "
        f"{sorted(missing)}"
    )


@pytest.mark.xfail(strict=True, reason=(
    "D8b: get_options_chain is listed in allowed_tools by three skills "
    "(volatility-trading, options-foundations, income-strategies) with no contract, "
    "no implementation, and no adapter."))
def test_options_chain_is_either_implemented_or_undeclared():
    """Phantom tools are worse than absent tools: the skill believes it can fetch
    an options chain and plans around data that will never arrive."""
    files = _skill_files()
    if not files:
        pytest.skip("no installed skill definitions found")

    declaring = [
        f.parent.name for f in files
        if "get_options_chain" in (_frontmatter(f).get("allowed_tools") or [])
    ]
    if not declaring:
        pytest.skip("no skill declares get_options_chain")

    exposed = set(mcp_adapters.REGISTRATION_MANIFEST)
    has_contract = any(REPO_ROOT.glob("contracts/get-options-chain*"))
    assert declaring and (exposed & {"get_options_chain"} or has_contract), (
        f"{declaring} declare get_options_chain, but there is no adapter and no "
        f"contract for it"
    )


# --- D9: the Q45 allowlist gate against the REAL registry --------------------

def test_q45_gate_itself_behaves(tmp_path):
    """Guard on the gate's own contract, independent of registry contents."""
    assert g1_gate.check_market_data_allowlist("early", ["get_price_history"]) == []
    assert g1_gate.check_market_data_allowlist("late", ["get_realtime_quote"]) == []
    assert g1_gate.check_market_data_allowlist("early", ["get_realtime_quote"])
    assert g1_gate.check_market_data_allowlist(
        "late", ["get_realtime_quote", "get_price_history"])


@pytest.mark.xfail(strict=False, reason=(
    "D9: every early-stage skill in skill-registry.yaml lacks get_price_history in "
    "its allowed_tools, so all of them fail check_market_data_allowlist. The gate is "
    "unit-tested only against synthetic inputs; it has never run against the real "
    "registry. Environmental: skips when no installed skills are present."))
def test_every_early_stage_skill_passes_the_q45_gate():
    """The gate exists to prevent exactly this state, and it is currently violated
    by every early-stage skill in the shipped registry."""
    registry = _registry()
    if not registry:
        pytest.skip("no skill-registry.yaml")

    early = set()
    for skill in registry.get("skills", []):
        for mode in skill.get("modes") or []:
            if mode.get("market_data_stage") == "early":
                early.add(skill.get("skill_name"))
    if not early:
        pytest.skip("no early-stage skills in the registry")

    files = _skill_files()
    if not files:
        pytest.skip("no installed skill definitions found")
    by_name = {f.parent.name: f for f in files}

    violations = {}
    for name in sorted(early):
        path = by_name.get(name)
        if path is None:
            continue
        allowed = _frontmatter(path).get("allowed_tools") or []
        problems = g1_gate.check_market_data_allowlist("early", list(allowed))
        if problems:
            violations[name] = problems[0]

    assert not violations, (
        f"{len(violations)} early-stage skills fail the Q45 allowlist gate: "
        f"{sorted(violations)}"
    )
