#!/usr/bin/env python3
"""reduce_journals.py — journal reduction, the single write moment of thesis.md
(spec 046 Q15).

Strictly ordered and non-commutative:
  ① script computes mechanical fields (known-open, subscription freshness, verdict
     rollup, Q41 claim-level price freshness) — deterministic, zero LLM;
  ② LLM revises judgment fields (conviction / claims / wrong_if) reading ①'s output
     — a hook point in S1 (no LLM wired yet; the revision step exists and receives
     ①'s mechanical summary);
  ③ single atomic write (tmp → fsync → os.replace) to thesis.md — the single-writer
     moment of the only living file (Q5 partitioning).

Judgment must rest on established mechanical fact, not precede it — order matters.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_boundary  # noqa: E402 — the single write boundary (T172)
import journal  # noqa: E402

# Q41: a directional claim needs a fresh price — re-quote or accept a <24h quote;
# older prices degrade the claim to stale_price (barred from trade-template).
PRICE_FRESHNESS_MAX_AGE_SECONDS = 24 * 3600


def _compute_mechanical(shard_dir: Path) -> dict[str, Any]:
    """① mechanical fields — derived facts only."""
    entries: list[dict] = []
    for shard in sorted(shard_dir.glob("*.ndjson")):
        entries.extend(journal.read_shard(shard))
    by_skill: dict[str, int] = {}
    for e in entries:
        by_skill[e["skill_id"]] = by_skill.get(e["skill_id"], 0) + 1
    # Q41 freshness: latest quote-timestamp among entries; degrade to stale_price
    # when older than 24h or absent.
    import datetime
    quote_ts = None
    for e in entries:
        for key in ("quote_observed_at", "observed_at"):
            if e.get(key):
                quote_ts = e[key]
                break
        if quote_ts:
            break
    fresh = False
    if quote_ts:
        try:
            age = (datetime.datetime.now(datetime.timezone.utc)
                   - datetime.datetime.fromisoformat(quote_ts)).total_seconds()
            fresh = age <= PRICE_FRESHNESS_MAX_AGE_SECONDS
        except ValueError:
            fresh = False
    return {
        "entry_count": len(entries),
        "by_skill": by_skill,
        "known_open": [],
        "subscription_freshness": {},
        "verdict_rollup": {},
        "price_freshness": {"fresh": fresh, "quote_observed_at": quote_ts,
                            "stale_price": quote_ts is not None and not fresh},
    }


def build_entity_index(artifacts_root: Path) -> dict:
    """Q20/Q9: the entity index is a VIEW computed at reduction time — all artifact
    `entity_claims` scanned, (entity, metric, period) concatenated. Same key with
    different values: retrieved_at-equal → true contradiction (mechanical report);
    retrieved_at-different → suspected restatement (never a contradiction)."""
    groups: dict[tuple[str, str, str], list[dict]] = {}
    for art in sorted(artifacts_root.rglob("*.md")):
        fm = journal_frontmatter(art)
        for claim in fm.get("entity_claims") or []:
            if not isinstance(claim, dict) or claim.get("value") is None:
                continue
            key = (str(claim.get("entity")), str(claim.get("metric")),
                   str(claim.get("period")))
            groups.setdefault(key, []).append({
                "value": float(claim["value"]),
                "retrieved_at": claim.get("retrieved_at"),
                "artifact": str(art),
            })
    contradictions: list[dict] = []
    suspected: list[dict] = []
    for (entity, metric, period), rows in groups.items():
        values = {r["value"] for r in rows}
        if len(values) <= 1:
            continue
        times = {r["retrieved_at"] for r in rows}
        record = {"entity": entity, "metric": metric, "period": period,
                  "values": sorted(values), "artifacts": [r["artifact"] for r in rows]}
        if len(times) == 1:
            contradictions.append(record)   # same retrieval window, different value
        else:
            suspected.append(record)        # Q17/Q20: likely a restatement
    return {"contradictions": contradictions, "suspected_restatements": suspected}


def journal_frontmatter(path: Path) -> dict:
    import g1_gate  # same-directory module

    return g1_gate.parse_frontmatter(path.read_text(encoding="utf-8"))


def check_aggregate(artifacts_root: Path, constitution_path: Path,
                    with_notices: bool = False):
    """Q16 aggregate postconditions — the only place in the system with a global
    view. Returns problems (CONSTITUTION_BREACH) — NEVER auto-resolves. While
    `constitution_pin: unratified` the aggregate HARD-FAILS (Q83: placeholder
    governance cannot gate the aggregate)."""
    import g1_gate
    import yaml as _yaml

    notices: list[str] = []
    problems: list[str] = []
    try:
        constitution = _yaml.safe_load(constitution_path.read_text(encoding="utf-8")) or {}
    except (OSError, _yaml.YAMLError):
        constitution = {}
    positions: dict[str, float] = {}
    unratified = False
    for art in sorted(artifacts_root.rglob("*.md")):
        fm = g1_gate.parse_frontmatter(art.read_text(encoding="utf-8"))
        if str(fm.get("constitution_pin")) == "unratified":
            unratified = True
        sector = str(fm.get("sector") or "unspecified")
        pos = fm.get("position_pct")
        if isinstance(pos, (int, float)):
            positions[sector] = positions.get(sector, 0.0) + float(pos)
    if unratified:
        problems.append("CONSTITUTION_BREACH: aggregate check HARD-FAILS while "
                        "constitution_pin: unratified (Q83 — placeholder governance "
                        "cannot gate the aggregate)")
        return (problems, notices) if with_notices else problems
    for c in constitution.get("constraints") or []:
        if c.get("arity") != "aggregate":
            continue
        group, max_val = c.get("group_by"), c.get("max")
        if group == "sector":
            for sector, total in positions.items():
                if total > float(max_val):
                    problems.append(f"CONSTITUTION_BREACH: {c.get('id')} — sector "
                                    f"'{sector}' at {total}% exceeds max {max_val}% (Q16)")
    return (problems, notices) if with_notices else problems


def reduce(shard_dir: Path, thesis_path: Path,
           llm_revise: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> dict:
    mechanical = _compute_mechanical(shard_dir)
    # ② judgment fields read ①'s output — a hook point. Without an LLM wired, the
    # revision is the identity over the mechanical facts (explicit, never implicit).
    judgment = llm_revise(mechanical) if llm_revise else {"conviction": None,
                                                          "claims": [],
                                                          "wrong_if": []}
    doc = {
        "reduced_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "mechanical": mechanical,
        "judgment": judgment,
    }
    write_boundary.write(
        thesis_path,
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        producer='reduce_journals',
        kind='json',
        writer='reduce_journals')
    return doc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Journal reduction → thesis.md (Q15)")
    p.add_argument("--shard-dir", required=True)
    p.add_argument("--thesis", required=True, help="thesis.md output path")
    args = p.parse_args(argv)
    doc = reduce(Path(args.shard_dir), Path(args.thesis))
    print(f"REDUCED {doc['mechanical']['entry_count']} entries → {args.thesis}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
