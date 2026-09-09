#!/usr/bin/env python3
"""journal.py — per-subagent journal shards (spec 046 Q4 item 3, Q8 contract 3).

8 parallel appends to one file interleave and corrupt — a concurrency fact, not a
preference. Each subagent writes its own NDJSON shard; a reduction pass folds them.
Single-line O_APPEND writes are the concurrency-safe primitive (one corrupt line
cannot damage the rest).
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")  # Q65: system clock for logs

# Q8 contract 3 + Q79: entries must carry these keys for per-skill attribution.
REQUIRED_KEYS = ("skill_id", "ticker", "mode", "thesis_id", "tool_trace", "timestamp")


def make_entry(skill_id: str, ticker: str, mode: str, thesis_id: str,
               tool_trace: list[str], **extra: Any) -> dict:
    entry = {
        "skill_id": skill_id,
        "ticker": ticker,
        "mode": mode,
        "thesis_id": thesis_id,
        "tool_trace": list(tool_trace),
        "timestamp": datetime.now(NY_TZ).isoformat(),
    }
    entry.update(extra)
    return entry


def validate_entry(entry: dict) -> list[str]:
    return [f"missing key: {k}" for k in REQUIRED_KEYS if k not in entry]


def append_entry(shard_path: Path, entry: dict) -> None:
    """One NDJSON line per entry; append-only, single write call (POSIX O_APPEND)."""
    problems = validate_entry(entry)
    if problems:
        raise ValueError("; ".join(problems))
    shard_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(entry, ensure_ascii=False) + "\n"
    fd = os.open(shard_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def read_shard(shard_path: Path) -> list[dict]:
    if not shard_path.is_file():
        return []
    entries: list[dict] = []
    for line in shard_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except ValueError:
            continue  # a corrupt line must not damage the rest (NDJSON property)
    return entries
