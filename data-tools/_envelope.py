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
       rate_limit_remaining: Optional[int] = None,
       data_class: Optional[str] = None) -> dict:
    if data is None:
        raise ValueError("ok() requires non-null data (invariant 1)")
    # spec 046 Q72: data_class rides inside the payload — the closed envelope schema
    # (additionalProperties: false) makes a top-level field impossible without a
    # schema bump, and the payload position is the one the gates read anyway.
    if data_class is not None and isinstance(data, dict):
        data = {**data, "data_class": data_class}
    return _envelope("ok", data, source, cache_hit=cache_hit,
                     rate_limit_remaining=rate_limit_remaining, error=None)


def degraded(data: Any, *, source: str, error: str, cache_hit: bool = False,
             rate_limit_remaining: Optional[int] = None) -> dict:
    if not error:
        raise ValueError("degraded() requires an error reason (invariant 3)")
    return _envelope("degraded", data, source, cache_hit=cache_hit,
                     rate_limit_remaining=rate_limit_remaining, error=error)


def skipped(prerequisite: str, *, source: Optional[str] = None,
            detail: str = "") -> dict:
    """T180 (Q104): SKIPPED is not FAIL.

    A missing API key means the source was never attempted. Reporting that as an
    error makes a working keyless deployment look broken — and the zero-key path
    is the DEFAULT here: keys are not present on every machine, and five of the
    nine declared market sources need none.

    The distinction is the same one Q100 makes about citation failures: two
    conditions that need two different fixes must not share one message. "Add a
    key to unlock more sources" and "the data layer is down" are different, and
    the second is the only one anyone should be paged for."""
    reason = f"SKIPPED: {prerequisite}"
    if detail:
        reason += f" — {detail}"
    # `error` is the SINGLE source for this. The envelope's `additionalProperties:
    # false` rejected a separate `skip_reason` field, and on reflection it was
    # right to: two fields holding one fact is the divergence Q12 rule 3 forbids,
    # and the prefix makes the prerequisite machine-readable without a second key.
    return _envelope("skipped", None, source, cache_hit=False,
                     rate_limit_remaining=None, error=reason)


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


# ── symbol existence (T127) ─────────────────────────────────────────────────
#
# MEASURED, from the evidence base: `search_xbrl_facts(ticker="ALNT")` returned
# **ALNY (Alnylam)** — a different company — rather than an error. The session
# that hit it wrote the consequence exactly: *"A wrong symbol yields confident,
# fully-cited, wrong data"*, and classified it as a *"`SCHEMA_MISMATCH`-class
# error that voids the artifact"*.
#
# So this uses the EXISTING `SCHEMA_MISMATCH` code rather than coining
# `SYMBOL_NOT_FOUND`. Q76's rule is that a value must land on exactly one axis
# and that new values are a last resort; the evidence base already placed this
# one, and a second code for one defect would be the two-sources-of-truth
# divergence Q12 rule 3 forbids. The REFUSAL carries the specifics the code
# cannot: what was asked for, and what was probably meant.

def symbol_refusal(requested: str, known: "list[str] | set[str]", *,
                   source: Optional[str] = None, max_near: int = 5) -> Optional[dict]:
    """Return a structured refusal when `requested` is not a known symbol.

    Returns None when the symbol IS known — so callers read as:
        refusal = symbol_refusal(t, universe, source="get_ticker_coverage")
        if refusal: return refusal

    Why a refusal and not a fallback: the failure mode this replaces is not "no
    data" but "another company's data, fully cited and confident". Absence is
    recoverable; substitution is not, because nothing downstream can tell it
    happened.

    Near-misses are ranked by edit distance with a shared-prefix tiebreak —
    deterministic, stdlib, no LLM. `ALNT` → `ALNY` is one edit, which is exactly
    the case that produced this function.
    """
    import difflib

    if not requested:
        return error("SCHEMA_MISMATCH: empty symbol", source=source)
    known_list = sorted(known)
    if requested in known_list:
        return None

    near = difflib.get_close_matches(requested, known_list, n=max_near, cutoff=0.6)
    # A case- or separator-only difference is the SAME symbol, not a near miss —
    # `goog` for `GOOG` should never be reported as a mistake.
    norm = lambda s: s.upper().replace(".", "-").replace("_", "-")
    if any(norm(k) == norm(requested) for k in known_list):
        return None

    detail = (f"unknown symbol '{requested}'. "
              + (f"Near misses: {', '.join(near)}. " if near else "No near miss in the "
                 f"{len(known_list)} known symbols. ")
              + "REFUSED rather than resolved: a substituted symbol yields another "
                "company's data, fully cited, and nothing downstream can tell. ")
    if near:
        detail += (f"Did you mean '{near[0]}'? If not, this is SCHEMA_MISMATCH and "
                   f"the lookup must not proceed under the requested symbol.")
    return error(detail, source=source)
