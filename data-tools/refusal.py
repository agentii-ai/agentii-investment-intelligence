#!/usr/bin/env python3
"""refusal.py — the data-layer refusal surface (spec 046 Q6-A surface 1, S1-thin).

Refusal convention: envelope `error` strings carry a `CODE:` prefix from
contracts/taxonomy.yaml; remediation follows the colon (e.g.
"DATA_STALE: source data predates the artifact as_of — re-run after refresh").

Why this shape: it is transport-proof (any JSON-text MCP transport passes it
losslessly — verified in the S1 spike), deterministic (parsers match the prefix,
no LLM), and harness-agnostic (the refusal lives in our components, not in the
agent's prompt — Q10).

License: MIT-only imports (stdlib) — no copyleft.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _envelope  # noqa: E402


def refuse(code: str, remediation: str) -> dict:
    """Build a structured refusal envelope. `code` must be an error_code value from
    contracts/taxonomy.yaml (closed enum, Q6)."""
    return _envelope.error(f"{code}: {remediation}")


def require_observed_at(data: Optional[dict]) -> Optional[dict]:
    """Q71 hard rule: a quote lacking observed_at may not be used in any pinned
    artifact. Returns the refusal envelope, or None when the datum is pinnable."""
    if not data or not data.get("observed_at"):
        return refuse("DATA_STALE",
                      "quote lacks observed_at (Q71 — unusable for pinned artifacts)")
    return None


def parse_error_code(error: Optional[str]) -> Optional[str]:
    """Deterministic parser for the CODE: prefix convention (used by G1/dispatcher)."""
    if not error:
        return None
    code = error.split(":", 1)[0]
    return code if code.isupper() and "_" in code else None


def require_price_access(stage: str, tool: str) -> Optional[dict]:
    """Q41/Q42: `late`-stage skills never touch `get_price_history` (price is the
    final check, not the raw material). Returns a refusal envelope or None."""
    if stage == "late" and tool == "get_price_history":
        return refuse("PRICE_ACCESS_PREMATURE",
                      "late-stage mode requested get_price_history — price is the "
                      "final check for fundamental work, never the raw material "
                      "(Q41/Q42; get_realtime_quote at the end only)")
    return None
