#!/usr/bin/env python3
"""golden_prompt_eval.py — the spec-055 eval harness manifest builder (FR-E04, SC-004).

Deterministic half of the golden-prompt harness: enumerates
tests/golden_prompts_055/*.md, validates each file's structure (## Prompt +
## Rubric Checks with checkboxes), maps prompts to the skills they cover, and
emits a judge-ready manifest. The judge run itself (Opus-5 rubric scoring) is
a runtime operation — this manifest is its deterministic input.

Exit 0 when every registered bio-pharm skill is covered by ≥1 prompt.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "tests" / "golden_prompts_055"
SKILL_DIR = ROOT / "plugins" / "vertical-plugins" / "bio-pharm" / "skills" / "agentii"

_SKILL_HINTS = {
    "market-share-tracking": ["launch_board", "loe_erosion"],
    "ct-status-diff": ["diff_weekly"],
    "med-market-sizing": ["funnel_completeness"],
    "med-event-takeaways": ["ada_note"],
    "fda-catalyst-medicines": ["catalyst_medicines"],
    "fda-catalyst-devices": ["catalyst_devices"],
    "fda-catalyst-vaccines": ["catalyst_vaccines"],
    "pipeline-medicines": ["mechanism_map", "pos_change"],
    "pipeline-devices": ["pipeline_devices"],
    "pipeline-vaccines": ["pipeline_vaccines"],
    "sector-overview-med": ["ripple_map"],
    "trial-readout-analysis": ["readout_lattice"],
    "peer-bench-med": ["peer_analog"],
    "earnings-preview-med": ["earnings_whats_changed"],
    "recent-quarter-med": ["recent_quarter_whats_changed"],
}


def build_manifest() -> dict:
    prompts = []
    for f in sorted(PROMPT_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if "## Prompt" not in text or "## Rubric" not in text:
            raise ValueError(f"{f.name}: missing ## Prompt or ## Rubric")
        rubric = re.findall(r"^- \[ \]", text, re.MULTILINE)
        if not rubric:
            raise ValueError(f"{f.name}: no rubric checks")
        prompts.append({"file": f.name, "rubric_checks": len(rubric)})
    skills = sorted(p.name for p in SKILL_DIR.iterdir() if p.is_dir())
    coverage = {
        s: [p["file"] for p in prompts
            if any(hint in p["file"] for hint in _SKILL_HINTS.get(s, []))]
        for s in skills
    }
    return {
        "prompt_count": len(prompts),
        "skill_count": len(skills),
        "prompts": prompts,
        "coverage": coverage,
        "uncovered": [s for s, ps in coverage.items() if not ps],
    }


def main() -> int:
    try:
        manifest = build_manifest()
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2))
    if manifest["uncovered"]:
        print(f"FAIL: skills without a prompt: {manifest['uncovered']}", file=sys.stderr)
        return 1
    print(f"OK: {manifest['prompt_count']} prompts cover "
          f"{manifest['skill_count']} skills (FR-E04 coverage ✓; judge run deferred)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
