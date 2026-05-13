#!/usr/bin/env python3
"""
Port references/prompts/system_v2_7.py → agents/agentii-equity-agent.md.

Scaffold (T021 per tasks.md). Full implementation in Phase 6 (US6).

At this phase, this script:
  - Parses argparse CLI with the flags the final implementation will support.
  - Reads contracts/tool-name-map.json (system_v2_7 block).
  - Emits a placeholder agent.md stub with correct frontmatter so check.py
    passes once an agent file is added.
  - Exits 0.

Phase 6 will add: system_v2_7.py AST walk, tool-name rewriting, triggers
extraction, multi_ticker_semantics inference, and full agent.md authoring.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path("/Users/frank/A/agenzym/references/prompts/system_v2_7.py")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help=f"Path to system_v2_7.py (default: {DEFAULT_SOURCE})")
    ap.add_argument("--tool-map", type=Path,
                    default=ROOT / "contracts" / "tool-name-map.json",
                    help="Path to tool-name-map.json")
    ap.add_argument("--output", type=Path,
                    default=ROOT / "plugins" / "agent-plugins" /
                    "agentii-equity-agent" / "agents" / "agentii-equity-agent.md",
                    help="Output agent.md path")
    ap.add_argument("--check-only", action="store_true",
                    help="Validate inputs without writing output")
    args = ap.parse_args()

    # Validate inputs
    if not args.source.is_file():
        print(f"WARN: source {args.source} not found (scaffold mode)", file=sys.stderr)
    if not args.tool_map.is_file():
        print(f"ERROR: tool-map {args.tool_map} not found", file=sys.stderr)
        return 2
    try:
        json.loads(args.tool_map.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: tool-map JSON parse: {e}", file=sys.stderr)
        return 2

    print(f"[scaffold] port-system-prompt.py — full impl lands in Phase 6 (US6)")
    print(f"[scaffold] source: {args.source}")
    print(f"[scaffold] tool-map: {args.tool_map}")
    print(f"[scaffold] output: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
