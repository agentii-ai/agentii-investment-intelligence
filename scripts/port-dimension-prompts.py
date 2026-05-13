#!/usr/bin/env python3
"""
Port references/prompts/{1..8}/*.yaml → equity-research-core/skills/dim-*/SKILL.md.

Scaffold (T022 per tasks.md). Full implementation in Phase 3 (US2).

At this phase, this script:
  - Parses the full argparse CLI the final implementation will expose.
  - Locates source prompt directories and reports discovered YAMLs.
  - Validates tool-name-map.json is parseable.
  - Exits 0.

Phase 3 will add: filename-form dispatch (5 forms), YAML extraction of 8
required blocks, slugification, _optimized version resolution, overview-file
mapping (T061a), audit-table drift detection (T061b), essentials budget
check (FR-052a), and SKILL.md rendering with per-mode output schema YAMLs.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Users/frank/A/agenzym/references/prompts")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help=f"Path to references/prompts/ (default: {DEFAULT_SOURCE})")
    ap.add_argument("--tool-map", type=Path,
                    default=ROOT / "contracts" / "tool-name-map.json")
    ap.add_argument("--output-dir", type=Path,
                    default=ROOT / "plugins" / "vertical-plugins" /
                    "equity-research-core" / "skills")
    ap.add_argument("--audit-budget", action="store_true",
                    help="Print per-dim essentials tool-call budget table (FR-052a)")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()

    if not args.tool_map.is_file():
        print(f"ERROR: tool-map {args.tool_map} not found", file=sys.stderr)
        return 2
    try:
        json.loads(args.tool_map.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: tool-map parse: {e}", file=sys.stderr)
        return 2

    if not args.source.is_dir():
        print(f"WARN: source {args.source} not found (scaffold mode)", file=sys.stderr)
        return 0

    discovered = {}
    for dim in range(1, 9):
        dim_dir = args.source / str(dim)
        if dim_dir.is_dir():
            discovered[dim] = sorted([p.name for p in dim_dir.glob("*.yaml")])
        else:
            discovered[dim] = []

    print("[scaffold] port-dimension-prompts.py — full impl lands in Phase 3 (US2)")
    for dim, files in discovered.items():
        print(f"[scaffold] dim-{dim}: {len(files)} YAML file(s)")

    if args.audit_budget:
        print("[scaffold] --audit-budget: per-dim essentials tool-call table (FR-052a)")
        print("[scaffold] Full budget computation implemented in Phase 3")

    return 0


if __name__ == "__main__":
    sys.exit(main())
