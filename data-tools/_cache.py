#!/usr/bin/env python3
"""_cache.py — file cache + backoff + failover for data-tools (spec 039 US5, T056).

- FileCache: ~/.agentii/cache/<category>/<key>.json with per-category TTL.
- backoff_delay: exponential backoff schedule (capped).
- failover_order / try_sources: try in-category sources by ascending priority
  until one succeeds; report which was used.

License: MIT-only imports (stdlib) — no copyleft.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional

DEFAULT_ROOT = Path(os.path.expanduser("~/.agentii/cache"))

# Per-category default TTL in seconds (fresh-enough windows; overridable per call).
CATEGORY_TTL = {
    "macro": 6 * 3600,        # macro series update slowly
    "market": 300,            # quotes are volatile
    "earnings": 3600,
    "alternative": 1800,
    "calendar": 12 * 3600,
    "global": 900,
}


class FileCache:
    def __init__(self, root: Path | str = DEFAULT_ROOT, clock: Callable[[], float] = time.time):
        self.root = Path(root)
        self.clock = clock

    def _path(self, category: str, key: str) -> Path:
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        return self.root / category / f"{h}.json"

    def get(self, category: str, key: str) -> tuple[bool, Any]:
        p = self._path(category, key)
        if not p.is_file():
            return False, None
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return False, None
        if self.clock() > rec.get("expires_at", 0):
            return False, None
        return True, rec.get("value")

    def set(self, category: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            ttl = CATEGORY_TTL.get(category, 900)
        p = self._path(category, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = {"value": value, "expires_at": self.clock() + ttl, "stored_at": self.clock()}
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(rec), encoding="utf-8")
        os.replace(tmp, p)


def backoff_delay(attempt: int, base: float = 0.5, cap: float = 30.0) -> float:
    """Exponential backoff: base * 2**attempt, capped."""
    return min(cap, base * (2 ** attempt))


def failover_order(sources: list[dict]) -> list[dict]:
    """Sort sources by ascending priority (lower tried first)."""
    return sorted(sources, key=lambda s: s.get("priority", 1_000))


def try_sources(sources: list[dict]) -> tuple[Any, Optional[str]]:
    """Try each source's `fn` in priority order until one returns without raising.
    Returns (result, used_source_name). Raises the last error if all fail."""
    last_err: Optional[Exception] = None
    for src in failover_order(sources):
        fn = src.get("fn")
        if fn is None:
            continue
        try:
            return fn(), src.get("name")
        except Exception as e:  # noqa: BLE001 - failover
            last_err = e
            continue
    if last_err:
        raise last_err
    raise RuntimeError("no sources available")
