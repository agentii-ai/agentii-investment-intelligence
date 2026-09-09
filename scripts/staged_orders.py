#!/usr/bin/env python3
"""staged_orders.py — the research side's privilege ceiling (spec 046 Q74).

A staged order is a PROPOSAL written upstream of spec 021's stage_order. The five
preconditions checked at write time are the control plane's convergence point:
IC adjudication exists + constitution scalar/aggregate pass + stale_price == false
+ blind-estimate ordering + no blocking data-quality flags. While the constitution
is unratified the proposal HARD-FAILS (Q83 — the money boundary accepts no
placeholder governance). No agentii.* path ever transmits.
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

REQUIRED_FIELDS = ("symbol", "side", "qty", "price", "thesis_id", "claim_id",
                   "ic_approval_ref", "expires_at")


def check_preconditions(proposal: dict, *, constitution_pin: str,
                        stale_price: bool, blind_order_ok: bool,
                        blocking_flags: bool, aggregate_pass: bool) -> list[str]:
    """The five preconditions (Q74 A+) + schema completeness. Empty = writable."""
    problems: list[str] = []
    if constitution_pin == "unratified":
        problems.append("REFUSED: constitution_pin unratified — the money boundary "
                        "accepts no placeholder governance (Q83 hard-fail)")
    for field in REQUIRED_FIELDS:
        if not proposal.get(field):
            problems.append(f"missing required field: {field} (expires_at is "
                            f"mandatory — an expired proposal is a decision on "
                            f"changed facts)")
    if not proposal.get("ic_approval_ref"):
        problems.append("IC adjudication missing (Q66)")
    if stale_price:
        problems.append("stale_price == true — price is not decision-fresh (Q41)")
    if not blind_order_ok:
        problems.append("blind-estimate ordering violated (Q73)")
    if blocking_flags:
        problems.append("blocking data-quality flag present (Q78)")
    if not aggregate_pass:
        problems.append("aggregate constitution check failed (Q35)")
    return problems


def write_proposal(thesis: Path, proposal: dict) -> Path:
    """Write {ts}-{ticker}.yaml — the proposal is the research side's last word.
    Transmission is exclusively the human's, via spec 021 + 033."""
    stamp = datetime.now(NY_TZ).strftime("%Y-%m-%dT%H%M%S")
    out_dir = thesis / "staged-orders"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stamp}-{proposal['symbol']}.yaml"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(yaml.safe_dump(proposal, sort_keys=False), encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return path


if __name__ == "__main__":
    print("staged_orders is a library — proposals are written by the implement "
          "path after all five preconditions pass (Q74)")
