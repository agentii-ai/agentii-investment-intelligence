#!/usr/bin/env python3
"""workspace_cache.py — the workspace-level shared raw-data cache (spec 046 Q44/Q82).

The layer that survives zero-key rate limits under N parallel theses: filesystem
first, API second. File names carry ISO8601 timestamps; INDEX.md records the
latest fetch per ticker+data_type. Atomic writes throughout (tmp + rename).

Layout:
    workspace/market-data/quotes/NVDA_2026-09-08T1430Z.json
    workspace/market-data/history/NVDA_1y_1d_2026-09-08T1200Z.json
    workspace/market-data/INDEX.md
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

DEFAULT_TTL = {"quote": 900, "history": 24 * 3600}  # Q44 dual TTL


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _file_age_seconds(path: Path) -> float:
    try:
        stamp = datetime.strptime(path.name.split("_")[-1].split(".")[0],
                                  "%Y-%m-%dT%H%MZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - stamp).total_seconds()
    except (ValueError, IndexError):
        return float("inf")


def write_quote(root: Path, ticker: str, data: dict, *, observed_at: str,
                ttl_seconds: Optional[int] = None) -> Path:
    return _write(root, "quotes", ticker, data, observed_at, ttl_seconds)


def _write(root: Path, kind: str, ticker: str, data: dict, observed_at: str,
           ttl_seconds: Optional[int]) -> Path:
    ttl = ttl_seconds if ttl_seconds is not None else DEFAULT_TTL["quote"]
    payload = {"data": data, "observed_at": observed_at, "stored_at": _now(),
               "ttl_seconds": ttl}
    path = root / kind / f"{ticker}_{_now()}.json"
    _atomic_write(path, json.dumps(payload))
    index = read_index(root)
    index[ticker] = {"kind": kind, "file": path.name, "stored_at": payload["stored_at"]}
    _atomic_write(root / "INDEX.md", json.dumps(index, indent=2) + "\n")
    return path


def read_latest(root: Path, kind: str, ticker: str,
                ttl_seconds: Optional[int] = None) -> tuple[bool, Any]:
    """Filesystem-first lookup with TTL enforcement. The entry's own recorded
    ttl_seconds (min with the caller's) governs — each write carries its TTL."""
    ttl = ttl_seconds if ttl_seconds is not None else DEFAULT_TTL.get("quote")
    hits = sorted((root / kind).glob(f"{ticker}_*.json"), reverse=True)
    for p in hits:
        effective_ttl = ttl
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
            effective_ttl = min(ttl, float(payload.get("ttl_seconds", ttl)))
        except (ValueError, OSError):
            return False, None
        if _file_age_seconds(p) > effective_ttl:
            return False, None  # newest already stale — anything older is staler
        return True, payload.get("data")
    return False, None


def write_raw(root: Path, source: str, key: str, data: Any) -> Path:
    """Q82: `slow`-class sources (filings/xbrl/corpus) keyed by accession number —
    TTL effectively infinite (filings are immutable once accepted, so caching them
    is strictly safer than caching quotes)."""
    out_dir = root / "raw-data" / source
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{key}.json"
    _atomic_write(path, json.dumps({"data": data, "stored_at": _now()}))
    return path


def read_raw(root: Path, source: str, key: str) -> tuple[bool, Any]:
    p = root / "raw-data" / source / f"{key}.json"
    if not p.is_file():
        return False, None
    try:
        return True, json.loads(p.read_text(encoding="utf-8"))["data"]
    except (ValueError, KeyError):
        return False, None


def read_index(root: Path) -> dict:
    idx = root / "INDEX.md"
    if not idx.is_file():
        return {}
    try:
        return json.loads(idx.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return {}
