"""S3 tests (T040/T042): price-stage refusal + allowlist consistency; dispatcher
remainder — compile-time preflight, retry policy by failure class, Q60 reuse
validation, Q13/Q54 routing declarations."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import dispatch  # noqa: E402
import g1_gate  # noqa: E402
import refusal  # noqa: E402


# --- T040: price-stage refusal -------------------------------------------------

def test_late_stage_price_history_refused():
    env = refusal.require_price_access("late", "get_price_history")
    assert env["status"] == "error"
    assert env["error"].startswith("PRICE_ACCESS_PREMATURE")


def test_late_stage_realtime_quote_allowed():
    assert refusal.require_price_access("late", "get_realtime_quote") is None


def test_early_stage_history_allowed():
    assert refusal.require_price_access("early", "get_price_history") is None


def test_allowlist_consistency_q45():
    # early MUST include get_price_history; late MUST include get_realtime_quote
    # and NOT get_price_history — illegal states are deterministic (Q45).
    assert g1_gate.check_market_data_allowlist("early", ["get_price_history"]) == []
    assert g1_gate.check_market_data_allowlist("early", ["get_realtime_quote"])
    assert g1_gate.check_market_data_allowlist("late", ["get_realtime_quote"]) == []
    assert g1_gate.check_market_data_allowlist("late",
                                               ["get_realtime_quote", "get_price_history"])
    assert g1_gate.check_market_data_allowlist("none", []) == []


# --- T042: dispatcher remainder -------------------------------------------------

def test_compile_time_preflight_fast_fails_naming_the_node():
    registry = {"business-model": {"requires": ["xbrl_coverage: fresh"]},
                "dcf": {"requires": ["business-model"]}}
    plan = [{"skill": "business-model", "requires": ["xbrl_coverage: fresh"]},
            {"skill": "dcf", "requires": ["business-model", "ghost-skill"]}]
    problems = dispatch.preflight(plan, registry)
    assert problems and any("dcf" in p and "ghost-skill" in p for p in problems)


def test_preflight_passes_when_all_requires_resolve():
    registry = {"business-model": {"requires": []}, "dcf": {"requires": ["business-model"]}}
    plan = [{"skill": "business-model"}, {"skill": "dcf", "requires": ["business-model"]}]
    assert dispatch.preflight(plan, registry) == []


def test_retry_policy_by_failure_class():
    # deterministic failures fast-fail (retry cannot change the result);
    # VALIDATOR_FAIL retries N≈2 WITH the failure report injected.
    retries, inject = dispatch.retry_policy("DATA_STALE")
    assert (retries, inject) == (0, False)
    retries, inject = dispatch.retry_policy("VALIDATOR_FAIL")
    assert (retries, inject) == (2, True)


def test_q60_reuse_validation(tmp_path):
    art = tmp_path / "art.md"
    art.write_text("""---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "x:y"
mode: default
data_class: slow
---

# body
""")
    current = {"assumption_pin": 1}
    # valid frontmatter + as_of inside the freshness window → reuse (skip)
    verdict = dispatch.reuse_verdict(art, freshness_window_days=7,
                                     current_pins=current, now="2026-09-10")
    assert verdict == "reuse"
    # as_of outside the window → force re-run
    verdict = dispatch.reuse_verdict(art, freshness_window_days=7,
                                     current_pins=current, now="2026-10-01")
    assert verdict == "force_rerun"
    # corrupted frontmatter → force re-run
    art.write_text("garbage without frontmatter")
    assert dispatch.reuse_verdict(art, 7, current, "2026-09-10") == "force_rerun"
