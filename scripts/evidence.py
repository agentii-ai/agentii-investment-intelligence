#!/usr/bin/env python3
"""evidence.py — committed immutable quote snapshots (spec 046 Q77).

Only CITED quotes become evidence: an uncited fetch stays in the volatile cache.
Each snapshot is a new timestamped file (append-style immutability — a snapshot
is never rewritten), carrying observed_at / retrieved_at / price_basis (Q71).
Evidence is COMMITTED to git; the caches are gitignored — the two roles of the
same underlying data, separated.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

NY_TZ = ZoneInfo("America/New_York")


def snapshot_quote(thesis: Path, ticker: str, data: dict, *, observed_at: str,
                   retrieved_at: str, price_basis: str) -> Path:
    evidence_dir = thesis / "evidence" / "quotes"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(NY_TZ).strftime("%Y-%m-%dT%H%M%S%f")  # sub-second uniqueness
    path = evidence_dir / f"{stamp}-{ticker}.yaml"
    record = {
        "ticker": ticker,
        "price": data.get("price"),
        "observed_at": observed_at,
        "retrieved_at": retrieved_at,
        "price_basis": price_basis,
        "source": data.get("_source"),
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return path


if __name__ == "__main__":
    print("evidence.snapshot_quote is a library function — invoked from the "
          "dispatch/reduction path for every cited quote (Q77)")
