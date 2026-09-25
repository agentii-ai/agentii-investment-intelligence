"""test_run_surface_ablation.py — the offline half of `T080`'s ablation runner (spec 062).

**What is NOT tested here, and saying so is the point**: the runner's whole output comes from two live
completions per question, so a test of its result needs a model credential and a network. What CAN be
tested is the half where a bug is silent and would corrupt the comparison — **the with-arm's context
block**.

That half matters more than it looks. The two arms differ by exactly one string, and if the "without"
arm ever received the context the ablation would measure noise against noise and report a tie — which,
under the pre-declared tie rule, is `INCONCLUSIVE` and would retire nothing while looking like a
result. So the assertion that **the context block is non-empty, carries the frozen records, and is not
secreted into the without-arm prompt** is the one that keeps the comparison real.

**And the nondeterminism is recorded rather than tested away**: `temperature=0` does NOT make DeepSeek
reproducible. Measured 2026-09-25 — the same question scored 4/4-vs-3/4 on the smoke run and 3/4-vs-3/4
on the full run. A test asserting a fixed score would be testing the provider's sampler, not this code.
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_surface_ablation as abl  # noqa: E402

CTX = {
    "cases": [
        {"case_id": "a", "title": "Case A", "provenance": "synthesized",
         "analogue_tags": {"company_situation": ["turnaround"]}, "tickers_referenced": ["AAPL"],
         "case_summary": "A summary.", "result_headline": "A result.", "when_to_recall": "Recall A."},
        {"case_id": "b", "title": "Case B", "provenance": "extracted",
         "analogue_tags": {"company_situation": ["turnaround"]}, "tickers_referenced": ["MCD"],
         "case_summary": None, "result_headline": None, "when_to_recall": None},
    ],
    "strategies_returned_by_the_same_call": [{"strategy_id": "s", "title": "Strategy S", "note": "N"}],
}


def test_the_context_block_carries_the_frozen_records():
    block = abl._context_block(CTX)
    assert "Case A" in block and "Case B" in block and "Strategy S" in block
    assert "A summary." in block and "Recall A." in block


def test_the_null_fields_are_preserved_not_repaired():
    """The supply finding IS the asymmetry — a `None` in the rendered context is the measurement.

    A helper that quietly dropped nulls would make every case look populated, and the with-arm would be
    answering a question the real surface does not pose.
    """
    payload = json.loads(abl._context_block(CTX).split("```json")[1].split("```")[0])
    extracted = next(c for c in payload["cases"] if c["case_id"] == "b")
    assert extracted["case_summary"] is None and extracted["when_to_recall"] is None, extracted
    synthesized = next(c for c in payload["cases"] if c["case_id"] == "a")
    assert synthesized["when_to_recall"] == "Recall A."


def test_the_declared_output_shape_is_what_the_rubric_can_score():
    """The prompt asks for the nine skills' declared shape, and the rubric reads that shape.

    If the shape and the rubric drift apart the ablation scores every arm identically — for a reason
    that has nothing to do with the surface.
    """
    for needed in ("## Executive Summary", "[FACT]", "[DEDUCTED]", "[VIEW]",
                   "as_of", "constitution_pin", "assumption_pin", "corpus_version", "skill_pin"):
        assert needed in abl.SHAPE, f"the requested shape lost `{needed}`, which the rubric requires"


def test_the_two_arms_can_only_differ_by_the_context_block():
    """The without-arm's extra text is the empty string — the arms are the same question plus one block."""
    assert abl._context_block(CTX).strip(), "an empty context block makes the two arms identical"
    assert "" != abl._context_block(CTX)
