#!/usr/bin/env python3
"""_envelope.py — AGENT_CONTRACT response envelope builder/validator (spec 039 US5, T055).

All data-tools/*.py return envelopes built here. Validation is against
contracts/envelope.schema.json (jsonschema) with the invariants from AGENT_CONTRACT.md.

License: MIT-only imports (no copyleft) — enforced by check.py Check 30b.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "contracts" / "envelope.schema.json"


def _envelope(status: str, data: Any, source: Optional[str], *, cache_hit: bool = False,
              rate_limit_remaining: Optional[int] = None, error: Optional[str] = None) -> dict:
    return {
        "status": status,
        "data": data,
        "source": source,
        "cache_hit": cache_hit,
        "rate_limit_remaining": rate_limit_remaining,
        "error": error,
    }


def ok(data: Any, *, source: str, cache_hit: bool = False,
       rate_limit_remaining: Optional[int] = None) -> dict:
    if data is None:
        raise ValueError("ok() requires non-null data (invariant 1)")
    return _envelope("ok", data, source, cache_hit=cache_hit,
                     rate_limit_remaining=rate_limit_remaining, error=None)


def degraded(data: Any, *, source: str, error: str, cache_hit: bool = False,
             rate_limit_remaining: Optional[int] = None) -> dict:
    if not error:
        raise ValueError("degraded() requires an error reason (invariant 3)")
    return _envelope("degraded", data, source, cache_hit=cache_hit,
                     rate_limit_remaining=rate_limit_remaining, error=error)


def error(reason: str, *, source: Optional[str] = None) -> dict:
    if not reason:
        raise ValueError("error() requires a reason (invariant 2)")
    return _envelope("error", None, source, cache_hit=False,
                     rate_limit_remaining=None, error=reason)


_SCHEMA_CACHE: Optional[dict] = None


def validate(env: dict) -> None:
    """Validate against the JSON schema. Raises jsonschema.ValidationError on failure."""
    global _SCHEMA_CACHE
    import jsonschema

    if _SCHEMA_CACHE is None:
        _SCHEMA_CACHE = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(env, _SCHEMA_CACHE)


def to_model_dict(payload: Any, model_cls: Any) -> Any:
    """Map a raw payload to a shared agentii_models Pydantic type when available
    (Constitution I/IX). Falls back to the raw payload if the model can't be built."""
    try:
        return model_cls(**payload).model_dump() if isinstance(payload, dict) else payload
    except Exception:  # noqa: BLE001
        return payload
