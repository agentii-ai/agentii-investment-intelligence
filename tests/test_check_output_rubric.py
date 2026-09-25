"""test_check_output_rubric.py — the buy-side rubric, registered (spec 062 `FR-034` iii, `T083`).

THE CONTROL IS THE FIRST CASE, and it is the one that makes the rest mean something: an artifact that
clears all four questions must PASS. Without it, a rubric that failed everything would satisfy every
other assertion in this file — and this programme has already shipped one gate whose red case nobody
had run against a green one.

EACH RED CASE CHANGES EXACTLY ONE THING from the control, so a failure names the rule it broke. The
verdicts are asserted individually rather than as a score: "3 of 4" does not say which question
failed, and the count is the least useful thing this rubric produces.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_output_rubric as rub  # noqa: E402

L13 = "https://agentii.ai/v/FLY/sec101/13"
L14 = "https://agentii.ai/v/FLY/sec101/14"
L15 = "https://agentii.ai/v/FLY/sec101/15"

#: 5 prose lines, 2 of them fact-bearing (40% ≤ the 50% bar); 5 tags, 3 inferred (60% ≥ the 10%
#: bar); the summary carries a `[DEDUCTED]`; every link names FLY, the subject in the path.
CONTROL = (
    "## Executive Summary\n"
    f"Revenue was $5.2B [FACT] ({L13}). We expect margin pressure to persist [DEDUCTED] ({L14}).\n"
    "\n"
    "## Analysis\n"
    f"Revenue was $5.2B [FACT] ({L13}).\n"
    f"We expect the trajectory to keep deteriorating [VIEW] ({L14}).\n"
    "The position is defensible, and the risk looks contained [VIEW].\n"
)


def _write(tmp_path, body: str, ticker: str = "FLY") -> pathlib.Path:
    # The subject comes from the PATH: `<theses>/<N>/artifacts/<TICKER>/<file>.md`.
    d = tmp_path / "theses" / "001" / "artifacts" / ticker
    d.mkdir(parents=True, exist_ok=True)
    p = d / "2026-09-20_1430_business-model_default.md"
    p.write_text(body, encoding="utf-8")
    return p


def test_the_control_passes_all_four(tmp_path):
    """THE CONTROL. Every other test here asserts a failure."""
    r = rub.check(_write(tmp_path, CONTROL))
    assert r["passed"] == 4, r


def test_q1_a_summary_of_facts_only_fails(tmp_path):
    """The summary interprets nothing. This is the corpus's most common shape: 25 of 50."""
    body = CONTROL.replace(" We expect margin pressure to persist [DEDUCTED] (" + L14 + ").", "")
    r = rub.check(_write(tmp_path, body))
    assert r["exec_summary_interprets"] is False
    assert r["verdicts"]["Q1-summary-interprets"] is False, r


def test_q2_a_token_inference_fails(tmp_path):
    """One inference among many facts is not analysis. The share is the thing, not the presence."""
    body = "## Executive Summary\nWe conclude the setup is favourable [VIEW].\n\n## Analysis\n" + \
        "".join(f"Revenue line {i} was ${i}.0M [FACT] ({L13}).\n" for i in range(1, 20))
    r = rub.check(_write(tmp_path, body))
    assert r["interpretation_share"] < rub.INTERPRETATION_MIN_SHARE, r
    assert r["verdicts"]["Q2-interpretation-share"] is False, r
    # And the control direction: the same ONE inference with fewer facts clears the bar.
    body2 = "## Executive Summary\nWe conclude the setup is favourable [VIEW] ({L14}).\n\n## Analysis\n" \
        f"Revenue was $5.2M [FACT] ({L13}).\n"
    assert rub.check(_write(tmp_path, body2))["verdicts"]["Q2-interpretation-share"] is True


def test_q3_a_data_dump_fails(tmp_path):
    """Past half the prose, the document is a fact table. The owner's word is 堆砌."""
    body = "## Executive Summary\nWe see the trajectory improving [VIEW] (" + L14 + ").\n\n## Analysis\n" \
        + "".join(f"Revenue line {i} was ${i}.0M [FACT] ({L13}).\n" for i in range(1, 12))
    r = rub.check(_write(tmp_path, body))
    assert r["fact_line_share"] > rub.FACT_LINE_MAX_SHARE, r
    assert r["verdicts"]["Q3-not-a-data-dump"] is False, r


def test_q4_a_foreign_ticker_citation_fails(tmp_path):
    """A perfectly well-formed URL pointing at another issuer — no structural rule can see it.

    Measured on the corpus 2026-09-25: 1 of 50 (`HON/..._supply-chain_default.md` cites PH).
    """
    body = CONTROL.replace(L14, "https://agentii.ai/v/PH/sec88/4")
    r = rub.check(_write(tmp_path, body, ticker="FLY"))
    assert r["foreign_ticker_citations"] == ["PH"], r
    assert r["verdicts"]["Q4-cites-own-subject"] is False, r


@pytest.mark.parametrize("path_ticker,expected", [("fly", None), ("FLY", True)])
def test_q4_is_not_applicable_without_a_subject_in_the_path(tmp_path, path_ticker, expected):
    """No uppercase parent directory means no subject, so Q4 cannot be asked — and `None` is the
    answer, NOT `False`.

    **This test first asserted `False`**, on the reasoning that an unreadable subject should be
    reported rather than silently passed. That was wrong in the same way the whole applicability rule
    was: `False` says "this artifact cites someone else", which the evidence does not support, and a
    rate computed over it would be a rate about the path convention. Reported as `n/a` and excluded
    from the denominator.
    """
    r = rub.check(_write(tmp_path, CONTROL, ticker=path_ticker))
    assert r["verdicts"]["Q4-cites-own-subject"] is expected, r
    assert r["scored"] == (4 if expected is True else 3), r
