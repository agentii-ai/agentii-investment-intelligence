#!/usr/bin/env python3
"""finding_id.py — content-derived stable finding IDs (spec 046 Q40).

The ID is a function of the finding's CONTENT, never its discovery order:
unchanged re-runs produce byte-identical IDs, which is what makes the eval
corpus aggregatable across runs (the same requirement that closed the error-code
enum in Q8 contract 1, applied one level up).
"""
from __future__ import annotations

import argparse
import hashlib
import sys


def finding_id(entity: str, metric: str, period: str, gap_type: str) -> str:
    seed = "|".join([entity or "", metric or "", period or "", gap_type or ""])
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Content-derived finding ID (Q40)")
    p.add_argument("--entity", default="")
    p.add_argument("--metric", default="")
    p.add_argument("--period", default="")
    p.add_argument("--gap-type", default="")
    args = p.parse_args(argv)
    print(finding_id(args.entity, args.metric, args.period, args.gap_type))
    return 0


if __name__ == "__main__":
    sys.exit(main())
