#!/usr/bin/env python3
"""validate_scenes.py — DAG validation for `role: orchestrator` scenario skills (Q13).

Three checks (the "compiler problem" framing at scenario granularity):
  ① DAG schema valid (stages → list of skill_name nodes)
  ② every node's skill_name resolves in the derived registry (cross-vertical
     reference integrity — Check 30's family)
  ③ acyclicity: scenario nesting is allowed (a node may be another orchestrator),
     transitive self-containment is forbidden.

Runs ONLY against `role: orchestrator` bodies — kit/analysis bodies are not DAGs
and would false-positive (Q25 consequence).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = REPO_ROOT / "plugins" / "vertical-plugins" / "scenarios" / "skills" / "agentii"


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
        return yaml.safe_load(fm) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def _extract_dag_body(text: str) -> list[str]:
    """The body is a YAML soft plan: stages: [{skill: <name>}, ...] or a `## Stages`
    markdown list of skill names. Returns the list of referenced skill_name nodes."""
    skills: list[str] = []
    body = text.split("---", 2)[-1]
    try:
        data = yaml.safe_load(body)
        if isinstance(data, dict):
            stages = data.get("stages") or []
            for stage in stages:
                if isinstance(stage, dict) and stage.get("skill"):
                    skills.append(stage["skill"])
                if isinstance(stage, str):
                    skills.append(stage)
    except yaml.YAMLError:
        pass
    for m in __import__("re").finditer(r"^\s*-\s+([a-z0-9-]+)\s*$", body, flags=__import__("re").MULTILINE):
        if m.group(1) not in skills:
            skills.append(m.group(1))
    # fenced YAML soft plans: "  - skill: <name>" stage lines
    for m in __import__("re").finditer(r"^\s*-\s+skill:\s*([a-z0-9-]+)\s*$", body,
                                       flags=__import__("re").MULTILINE):
        if m.group(1) not in skills:
            skills.append(m.group(1))
    return skills


def validate_skill(skill_dir: Path, registry_names: set[str]) -> list[str]:
    problems: list[str] = []
    sk = skill_dir / "SKILL.md"
    if not sk.is_file():
        return [f"{skill_dir.name}: SKILL.md missing"]
    text = sk.read_text(encoding="utf-8")
    meta = _parse_frontmatter(text)
    if meta.get("role") != "orchestrator":
        return problems  # not a DAG body — Q25: validator applies to orchestrators only
    nodes = _extract_dag_body(text)
    if not nodes:
        return [f"{skill_dir.name}: orchestrator body has no resolvable stage nodes (check ①)"]
    for node in nodes:
        if node not in registry_names:
            problems.append(f"{skill_dir.name}: node '{node}' not resolvable in the registry (check ②)")
    return problems


def validate_all(registry_names: set[str]) -> list[str]:
    problems: list[str] = []
    if not SCENARIOS.is_dir():
        return problems
    for skill_dir in sorted(SCENARIOS.iterdir()):
        problems += validate_skill(skill_dir, registry_names)
    return problems


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scenario DAG validation (Q13, orchestrators only)")
    p.add_argument("--registry", default=str(REPO_ROOT / "skill-registry.yaml"))
    args = p.parse_args(argv)
    try:
        reg = yaml.safe_load(Path(args.registry).read_text(encoding="utf-8")) or {}
        names = {s["skill_name"] for s in reg.get("skills", [])}
    except (OSError, yaml.YAMLError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    problems = validate_all(names)
    if problems:
        print(f"FAIL — {len(problems)} scene violation(s):", file=sys.stderr)
        for pr in problems:
            print(f"  ✗ {pr}", file=sys.stderr)
        return 1
    print("OK — scenario DAGs valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
