"""T066 — tests for scripts/srt-to-skill.py (write FIRST).

SRT parse, paraphrase-guard (reject long verbatim spans vs source), contract-section
presence in the emitted draft, and the no-repo-write invariant (SRT text never
persisted into the repo). Uses a synthetic transcript — no dependency on the
external course volume.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MOD = REPO_ROOT / "scripts" / "srt-to-skill.py"

SYNTHETIC_SRT = """1
00:00:01,000 --> 00:00:05,000
Leading indicators tell you where the economy is heading before it happens.

2
00:00:05,500 --> 00:00:10,000
The University of Michigan Consumer Sentiment Index surveys household confidence.

3
00:00:10,500 --> 00:00:15,000
Rising sentiment often precedes stronger consumer spending in later quarters.
"""


def _load():
    spec = importlib.util.spec_from_file_location("srt_to_skill", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_parse_srt_returns_text_segments(tmp_path):
    m = _load()
    srt = tmp_path / "sample.srt"
    srt.write_text(SYNTHETIC_SRT)
    segments = m.parse_srt(srt)
    assert len(segments) == 3
    assert "Leading indicators" in segments[0]
    # timestamps + indices stripped
    assert "-->" not in " ".join(segments)


def test_paraphrase_guard_rejects_long_verbatim():
    m = _load()
    source = "Rising sentiment often precedes stronger consumer spending in later quarters."
    verbatim = "Rising sentiment often precedes stronger consumer spending in later quarters."
    assert m.has_verbatim_span(verbatim, [source], max_run=8) is True
    paraphrase = "Improving household confidence tends to lead higher retail demand down the line."
    assert m.has_verbatim_span(paraphrase, [source], max_run=8) is False


def test_draft_has_required_contract_sections(tmp_path):
    m = _load()
    srt = tmp_path / "sample.srt"
    srt.write_text(SYNTHETIC_SRT)
    draft = m.build_draft_skill(
        skill_name="leading-indicators",
        vertical="macro-strategy",
        srt_paths=[srt],
        summary_points=["Leading indicators anticipate turning points.",
                        "Consumer sentiment is one such survey-based signal."],
    )
    for section in ("## Methodology", "## Output Structure", "## Error Handling",
                    "## Triggers", "## Defaults"):
        assert section in draft
    # attribution present, no long verbatim from source
    assert "inspired by" in draft.lower()
    assert m.has_verbatim_span(draft, m.parse_srt(srt), max_run=12) is False


def test_no_repo_write_of_srt(tmp_path):
    m = _load()
    srt = tmp_path / "sample.srt"
    srt.write_text(SYNTHETIC_SRT)
    # dry-run returns text, writes nothing under the repo
    draft = m.build_draft_skill("x", "macro-strategy", [srt], summary_points=["a", "b"])
    # the raw transcript lines must not appear verbatim in the returned draft
    for seg in m.parse_srt(srt):
        assert seg not in draft
