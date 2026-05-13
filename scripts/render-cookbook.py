#!/usr/bin/env python3
"""
Render managed-agent cookbook agent.yaml from plugin.json + cookbook.config.yaml.

Scaffold (T024 per tasks.md). Full implementation in Phase 7 (US7).

Phase 7 will add: plugin manifest merge, subagent yaml resolution, failure-policy
attachment, evidence-pack contract wiring, and agent.yaml emission.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cookbook", type=str, default="agentii-equity-agent")
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()
    cookbook_dir = ROOT / "managed-agent-cookbooks" / args.cookbook
    print(f"[scaffold] render-cookbook.py — full impl lands in Phase 7 (US7)")
    print(f"[scaffold] cookbook dir: {cookbook_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
