#!/usr/bin/env python3
"""challenge.py — the adversarial-verification core (spec 046 Q24/Q40/Q68).

S5 scope: finding cap with severity ordering, incremental scoping with the three
backstops, lifecycle-hook trigger decisions, content-derived IDs. The
cross-run contradiction surface reads the entity index (reduce_journals); the
pre-mortem / inversion prompt bodies live in the SKILL.md.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import finding_id  # noqa: E402

MAX_FINDINGS = 50  # Q40 cap — deterministic checks excepted (they live in converge)


def cap_findings(findings: list[dict]) -> tuple[list[dict], dict]:
    """Q40: ≈50 findings sorted by severity; overflow aggregates by category into
    a count summary (never silently dropped)."""
    order = {"high": 0, "medium": 1, "low": 2}
    ordered = sorted(findings, key=lambda f: order.get(f.get("severity"), 3))
    if len(ordered) <= MAX_FINDINGS:
        return ordered, {}
    kept, overflow = ordered[:MAX_FINDINGS], ordered[MAX_FINDINGS:]
    summary: dict[str, int] = {}
    for f in overflow:
        cat = f"{f.get('gap_type')}:{f.get('severity')}"
        summary[cat] = summary.get(cat, 0) + 1
    return kept, {"overflow_summary": summary, "dropped": len(overflow)}


def incremental_scope(artifacts: dict[str, str], since_state: dict[str, str]) -> list[str]:
    """Q40 A+: incremental — only artifacts whose pins/as_of changed since the
    last run are in scope. Cost scales with the CHANGE, not the corpus."""
    return [name for name, state in artifacts.items()
            if since_state.get(name) != state]


def backstop_trigger(nth_converge: int, constitution_bumped: bool,
                     subscriptions_changed: bool, n: int = 10) -> list[str]:
    """Q40's three backstops: every Nth converge / constitution MINOR-MAJOR /
    subscription change (a new subscription IS a new comparison pair — Q9)."""
    out = []
    if nth_converge % n == 0:
        out.append("periodic_full_sweep")
    if constitution_bumped:
        out.append("constitution_bump")
    if subscriptions_changed:
        out.append("subscription_change")
    return out


def lifecycle_hook(event: str) -> bool:
    """Q68: challenge fires at decision moments — pillar-complete / thesis-complete
    / pre-reduction. Unchallenged claims never enter the knowledge base (Q64)."""
    return event in ("pillar_complete", "thesis_complete", "pre_reduction")


def make_finding(entity: str, metric: str, period: str, gap_type: str,
                 severity: str = "medium", **extra: Any) -> dict:
    f = {"entity": entity, "metric": metric, "period": period,
         "gap_type": gap_type, "severity": severity,
         "id": finding_id.finding_id(entity, metric, period, gap_type)}
    f.update(extra)
    return f


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="challenge core (Q40/Q68)")
    p.add_argument("--nth-converge", type=int, default=1)
    p.add_argument("--constitution-bumped", action="store_true")
    p.add_argument("--subscriptions-changed", action="store_true")
    p.add_argument("--thesis", default=None,
                   help="thesis dir — report entity-index contradictions + suspected "
                        "restatements (the cross-run surface, Q9/Q20)")
    args = p.parse_args(argv)
    print("backstops:", backstop_trigger(args.nth_converge, args.constitution_bumped,
                                         args.subscriptions_changed))
    if args.thesis:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import reduce_journals  # noqa: E402

        thesis = Path(args.thesis)
        idx = reduce_journals.build_entity_index(thesis / "artifacts")
        findings = []
        for rec in idx["contradictions"]:
            findings.append(make_finding(rec["entity"], rec["metric"], rec["period"],
                                        "contradicts", "high",
                                        values=rec["values"], artifacts=rec["artifacts"]))
        for rec in idx["suspected_restatements"]:
            findings.append(make_finding(rec["entity"], rec["metric"], rec["period"],
                                        "contradicts", "medium",
                                        restatement=True, values=rec["values"]))
        kept, overflow = cap_findings(findings)
        print(f"contradictions: {len(kept)} (dropped {overflow.get('dropped', 0)})")
        for f in kept:
            print(f"  - [{f['severity']}] {f['entity']}.{f['metric']}@{f['period']} "
                  f"values={f.get('values')} id={f['id']}"
                  f"{' (suspected restatement)' if f.get('restatement') else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
