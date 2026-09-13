"""Spec 055 eval-harness structure tests (FR-E04/SC-004 deterministic half):
every registered bio-pharm skill is covered by ≥1 golden prompt, every prompt
file carries the ## Prompt + ## Rubric Checks structure, and the manifest
builder agrees."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import golden_prompt_eval  # noqa: E402


def test_every_skill_covered_by_a_golden_prompt():
    manifest = golden_prompt_eval.build_manifest()
    assert manifest["prompt_count"] >= 15, "FR-E04: ≥15 prompts required"
    assert manifest["uncovered"] == [], \
        f"skills without a prompt: {manifest['uncovered']}"


def test_prompt_files_carry_rubric_structure():
    prompt_dir = ROOT / "tests" / "golden_prompts_055"
    files = list(prompt_dir.glob("*.md"))
    assert files, "no golden prompts present"
    for f in files:
        text = f.read_text(encoding="utf-8")
        assert "## Prompt" in text, f"{f.name}: missing ## Prompt"
        assert "## Rubric" in text, f"{f.name}: missing ## Rubric"
        assert "- [ ]" in text, f"{f.name}: no rubric checkboxes"
