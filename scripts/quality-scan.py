#!/usr/bin/env python3
"""quality-scan.py — 5-dimension skill quality score (spec 039 Part I, US3, FR-013..FR-017).

Each dimension scores 0-2; total is 0-10. Deterministic — computed from on-disk
SKILL.md + references/ only (no LLM/MCP), so it runs in CI.

Dimensions:
  1. Completeness       — required sections present (## Output Structure, ## Error Handling,
                          ## Methodology, ## Triggers)
  2. Knowledge Density  — references/knowledge-frameworks.md exists with cited rows
  3. Citation Integrity — every knowledge-frameworks row carries a valid /v/ citation link
  4. Methodology Depth  — ## Methodology has >= 5 subsections/steps
  5. Output Structure   — ## Output Structure has >= 5 non-empty lines

Writes scores back to skill-registry.yaml (archives prior). --threshold gates CI
(warn-only by default until Part I enrichment lands, then flip blocking). --fix applies
safe remediations (missing ## Error Handling -> template; empty knowledge-frameworks -> template).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _registry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = REPO_ROOT / "contracts"
CITATION_RE = re.compile(r"https://agentii\.ai/v/[^/\s|]+/[A-Za-z0-9_-]+/\d+")
_ERR_TEMPLATE = CONTRACTS / "error-handling-template.md"

# suggested workflow per failing dimension (FR-015 report)
SUGGESTED = {
    "knowledge_density": "strategy-enrichment",
    "citation_integrity": "strategy-enrichment",
    "methodology_depth": "case-enrichment",
    "completeness": "quality-audit",
    "output_structure": "quality-audit",
}


def _kf_rows(kf_text: str) -> list[str]:
    rows = []
    for line in kf_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        first = s.strip("|").split("|")[0].strip()
        if not first or set(first) <= set("-: ") or first in {"strategy_id", "case_id", "setup_id"}:
            continue
        rows.append(s)
    return rows


def score_skill(skill_dir: Path) -> dict[str, Any]:
    skill_dir = Path(skill_dir)
    sk = skill_dir / "SKILL.md"
    text = sk.read_text(encoding="utf-8") if sk.is_file() else ""
    kf = skill_dir / "references" / "knowledge-frameworks.md"
    kf_text = kf.read_text(encoding="utf-8") if kf.is_file() else ""

    dims: dict[str, int] = {}

    # 1. Completeness — 0.5 per required section (rounded to 0-2)
    required = ["## Output Structure", "## Error Handling", "## Methodology", "## Triggers"]
    present = sum(1 for r in required if r in text)
    dims["completeness"] = round(2 * present / len(required))

    # 2. Knowledge Density — rows present
    rows = _kf_rows(kf_text)
    dims["knowledge_density"] = 2 if len(rows) >= 3 else (1 if rows else 0)

    # 3. Citation Integrity — all rows carry a valid /v/ link
    if rows:
        good = sum(1 for r in rows if CITATION_RE.search(r))
        dims["citation_integrity"] = 2 if good == len(rows) else (1 if good else 0)
    else:
        dims["citation_integrity"] = 0

    # 4. Methodology Depth — >= 5 subsections/steps
    meth = re.search(r"## Methodology\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    steps = len(re.findall(r"^###\s+\S+", meth.group(1), re.MULTILINE)) if meth else 0
    dims["methodology_depth"] = 2 if steps >= 5 else (1 if steps >= 2 else 0)

    # 5. Output Structure — >= 5 non-empty lines
    os_m = re.search(r"## Output Structure\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    ne = len([l for l in os_m.group(1).splitlines() if l.strip()]) if os_m else 0
    dims["output_structure"] = 2 if ne >= 5 else (1 if ne else 0)

    score = float(sum(dims.values()))
    failing = [d for d, v in dims.items() if v < 2]
    return {
        "skill": skill_dir.name,
        "score": score,
        "dimensions": dims,
        "failing_dimensions": failing,
        "suggested_workflows": sorted({SUGGESTED[d] for d in failing if d in SUGGESTED}),
    }


def apply_fix(skill_dir: Path, report: dict) -> list[str]:
    """Safe, idempotent remediations for failing dimensions (FR-016)."""
    fixes = []
    sk = Path(skill_dir) / "SKILL.md"
    if sk.is_file():
        text = sk.read_text(encoding="utf-8")
        if "## Error Handling" not in text and _ERR_TEMPLATE.exists():
            block = _ERR_TEMPLATE.read_text(encoding="utf-8")
            block = re.sub(r"^<!--.*?-->\n", "", block, flags=re.DOTALL)
            sk.write_text(text.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")
            fixes.append("added ## Error Handling from template")
    kf = Path(skill_dir) / "references" / "knowledge-frameworks.md"
    if not kf.is_file():
        tmpl = CONTRACTS / "knowledge-frameworks-template.md"
        if tmpl.exists():
            kf.parent.mkdir(parents=True, exist_ok=True)
            kf.write_text(tmpl.read_text(encoding="utf-8").replace("{skill_name}", Path(skill_dir).name), encoding="utf-8")
            fixes.append("created knowledge-frameworks.md from template")
    return fixes


def _skill_dirs(skills_root: Path) -> list[Path]:
    return [p.parent for p in sorted(Path(skills_root).glob("vertical-plugins/*/skills/agentii/*/SKILL.md"))]


def persist_scores(reports: list[dict], registry_path: Path) -> None:
    for rep in reports:
        entry = _registry.get_skill(rep["skill"], path=registry_path)
        if entry is None:
            continue
        prev = entry.get("quality_score")
        if prev is not None:
            entry["quality_score_prev"] = prev
        entry["quality_score"] = rep["score"]
        _registry.upsert_skill(entry, path=registry_path)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="5-dimension skill quality scan (spec 039 US3)")
    p.add_argument("--skill", help="score a single skill by name")
    p.add_argument("--threshold", type=float)
    p.add_argument("--blocking", action="store_true", help="fail CI below threshold (default warn-only)")
    p.add_argument("--fix", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-persist", action="store_true")
    p.add_argument("--registry", type=Path, default=_registry.DEFAULT_REGISTRY_PATH)
    p.add_argument("--skills-root", type=Path, default=REPO_ROOT / "plugins")
    args = p.parse_args(argv)

    dirs = _skill_dirs(args.skills_root)
    if args.skill:
        dirs = [d for d in dirs if d.name == args.skill]
        if not dirs:
            print(f"skill '{args.skill}' not found", file=sys.stderr)
            return 2

    reports = []
    for d in dirs:
        rep = score_skill(d)
        if args.fix:
            rep["fixes_applied"] = apply_fix(d, rep)
            rep = {**score_skill(d), "fixes_applied": rep["fixes_applied"]}
        reports.append(rep)

    if not args.no_persist and args.registry.exists():
        persist_scores(reports, args.registry)

    below = [r for r in reports if args.threshold is not None and r["score"] < args.threshold]

    if args.json:
        print(json.dumps({"threshold": args.threshold, "blocking": args.blocking,
                          "below_threshold": [r["skill"] for r in below], "results": reports}))
    else:
        for r in reports:
            flag = "" if not below or r not in below else "  ⚠ BELOW"
            print(f"{r['skill']:32s} {r['score']:.1f}/10  fail={r['failing_dimensions']}{flag}")
        if below:
            print(f"\n{len(below)} skill(s) below threshold {args.threshold}; "
                  f"suggested: {sorted({w for r in below for w in r['suggested_workflows']})}")

    if below and args.blocking:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
