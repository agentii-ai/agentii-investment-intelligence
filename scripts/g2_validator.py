#!/usr/bin/env python3
"""g2_validator.py — the G2 judgment-tier harness (spec 046 Q1/Q8 contract 2).

G2 is SAMPLING, not proof: fresh-context validator subagents run at phase
boundaries only, on G1-passing output, with a BOUNDED prompt (falsifiability /
contradiction with pinned facts / cross-run conflict — never open-ended quality
review). Verdict files follow a FIXED schema (Q8 contract 2) and are derived
facts the dispatcher reads — never a state store.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Optional

VERDICT_KEYS = ("artifact", "falsifiable", "supports", "contradictions")

BOUNDED_PROMPT = ("bounded prompt: assess falsifiability, contradiction with pinned "
                  "facts, and cross-run conflict — nothing else")


def make_verdict(artifact: str, falsifiable: bool, supports: bool,
                 contradictions: Optional[list[str]] = None) -> dict[str, Any]:
    return {"artifact": artifact, "falsifiable": falsifiable, "supports": supports,
            "contradictions": list(contradictions or [])}


def validate_verdict(verdict: dict[str, Any]) -> None:
    """The verdict schema is closed — a verdict missing a key is not a verdict."""
    missing = [k for k in VERDICT_KEYS if k not in verdict]
    if missing:
        raise ValueError(f"verdict schema violation — missing keys: {missing}")
    if not isinstance(verdict.get("contradictions"), list):
        raise ValueError("verdict.contradictions must be a list")


def dispatch(artifact: Path, validator: Callable[[Path, str], dict[str, Any]],
             prompt: str = BOUNDED_PROMPT) -> dict[str, Any]:
    """Run one validator pass. The validator is injectable (a subprocess wrapper
    in production; a fake in tests) — the harness owns the bounded prompt and the
    schema, never the judgment."""
    verdict = validator(artifact, prompt)
    validate_verdict(verdict)
    return verdict


def write_verdict(verdict: dict[str, Any], path: Path) -> None:
    """Verdict files are derived facts the dispatcher reads — atomic write."""
    import os

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(verdict, indent=2) + "\n", encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="G2 validator harness (Q1/Q8-2)")
    p.add_argument("--artifact", required=True)
    p.add_argument("--validator-cmd", required=True,
                   help="validator executable/command receiving the bounded prompt on stdin")
    args = p.parse_args(argv)
    # S5-thin: the CLI validates the schema contract; the subprocess wiring is the
    # caller's (harness packaging) — deterministic scaffolding, no LLM embedded.
    verdict = make_verdict(artifact=args.artifact, falsifiable=False, supports=False)
    validate_verdict(verdict)
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
