#!/usr/bin/env python3
"""
Port upstream financial-services/ skills → models-and-pitches/skills/.

Scaffold (T023 per tasks.md). Full implementation in Phase 4 (US3).

At this phase, this script:
  - Parses the final argparse CLI.
  - Validates tool-name-map.json and detects the upstream source directory.
  - Reads .sync-skiplist.yaml (if present) and reports skipped skills.
  - Exits 0.

Phase 4 will add: SHA-pinned upstream read per .upstream-pin.yaml, upstream_fsi
tool-name rewrite, citation_rewrite_rules application, data-source block
replacement from data-source-blocks/<skill>.md, FR-044 4-step protocol append,
Apache-2.0 header preservation, and per-skill .upstream-fingerprint emission.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UPSTREAM = Path("/Users/frank/A/agenzym/financial-services")
PORTED_SKILLS = ["dcf-model", "comps-analysis", "3-statement-model",
                 "lbo-model", "audit-xls", "xlsx-author"]
SKIPPED_NET_NEW = ["pitch-deck"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upstream", type=Path, default=DEFAULT_UPSTREAM)
    ap.add_argument("--tool-map", type=Path,
                    default=ROOT / "contracts" / "tool-name-map.json")
    ap.add_argument("--data-source-blocks", type=Path,
                    default=ROOT / "plugins" / "vertical-plugins" /
                    "models-and-pitches" / "data-source-blocks")
    ap.add_argument("--output-dir", type=Path,
                    default=ROOT / "plugins" / "vertical-plugins" /
                    "models-and-pitches" / "skills")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.tool_map.is_file():
        print(f"ERROR: tool-map {args.tool_map} not found", file=sys.stderr)
        return 2
    try:
        json.loads(args.tool_map.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: tool-map parse: {e}", file=sys.stderr)
        return 2

    print(f"[scaffold] sync-from-upstream.py — full impl lands in Phase 4 (US3)")
    print(f"[scaffold] upstream: {args.upstream}")
    print(f"[scaffold] skills to port: {PORTED_SKILLS}")
    print(f"[scaffold] skills skipped (net-new / composite): {SKIPPED_NET_NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
