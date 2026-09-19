#!/usr/bin/env python3
"""portfolio_aggregate.py — the derived portfolio view (spec 046 Q61).

Q4/Q16 "derive, never ledger" applied at workspace scale: the portfolio view is
RECOMPUTED on every run from thesis claims + artifact frontmatter — a persisted
portfolio file would silently diverge from the theses that produced it.

Pipeline: scan active claims (exclude pending_review/retired) → conviction-weighted
ticker aggregation with divergence flags → sector aggregation with Q16 aggregate
gates → emit `_portfolio/portfolio-view.md` (derived) + `_portfolio/conflicts.md`
(IC agenda input). Adjudication is Q66 `retired_by_ic` — NEVER automated.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_boundary  # noqa: E402 — the single write boundary (T172)
import g1_gate
import thesis_doc  # noqa: E402 — where machine state lives  # noqa: E402

ACTIVE_STATES = {"pinned", "stale_price"}  # pending_review / retired excluded (Q61)


def scan_active_claims(workspace: Path) -> list[dict[str, Any]]:
    """Read every thesis.md judgment claim + its artifact positions."""
    rows: list[dict[str, Any]] = []
    theses_dir = workspace / "theses"
    if not theses_dir.is_dir():
        return rows
    for thesis_dir in sorted(theses_dir.iterdir()):
        doc, _src = thesis_doc.read_machine(thesis_dir)
        if _src == "none":
            print(thesis_doc.no_machine_reason(thesis_dir), file=sys.stderr)
            continue
        conviction = doc.get("judgment", {}).get("conviction") or 0.5
        for claim in (doc.get("judgment") or {}).get("claims") or []:
            if not isinstance(claim, dict):
                continue
            if claim.get("state") not in ACTIVE_STATES:
                continue
            # direction + position from the claim or its artifacts
            direction = claim.get("direction", "long")
            pos = claim.get("position_pct")
            if pos is None:
                for art in sorted((thesis_dir / "artifacts").rglob("*.md")):
                    fm = g1_gate.parse_frontmatter(art.read_text(encoding="utf-8"))
                    if isinstance(fm.get("position_pct"), (int, float)):
                        pos = float(fm["position_pct"])
                        break
            rows.append({"thesis_id": thesis_dir.name, "claim_id": claim.get("id"),
                         "ticker": claim.get("entity"), "direction": direction,
                         "position_pct": float(pos) if pos is not None else 0.0,
                         "sector": claim.get("sector", "unspecified"),
                         "conviction": float(conviction)})
    return rows


def _claims_by_thesis(workspace: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    theses = workspace / "theses"
    if not theses.is_dir():
        return out
    for d in sorted(theses.iterdir()):
        doc, _src = thesis_doc.read_machine(d)
        if _src == "none":
            print(thesis_doc.no_machine_reason(d), file=sys.stderr)
            continue
        out[d.name] = [c for c in (doc.get("judgment") or {}).get("claims") or []
                       if isinstance(c, dict)]
    return out


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Conviction-weighted ticker aggregation with divergence flags + sector sums."""
    by_ticker: dict[str, dict[str, Any]] = {}
    for r in rows:
        t = r["ticker"]
        if t not in by_ticker:
            by_ticker[t] = {"directions": set(), "weighted": 0.0, "sector": r["sector"]}
        by_ticker[t]["directions"].add(r["direction"])
        by_ticker[t]["weighted"] += r["position_pct"] * r["conviction"]
    sectors: dict[str, float] = {}
    for t, agg in by_ticker.items():
        sectors[agg["sector"]] = sectors.get(agg["sector"], 0.0) + agg["weighted"]
    conflicts = [{"ticker": t, "directions": sorted(a["directions"])}
                 for t, a in by_ticker.items() if len(a["directions"]) > 1]
    return {"by_ticker": {t: {"weighted": round(a["weighted"], 2),
                              "sector": a["sector"]} for t, a in by_ticker.items()},
            "by_sector": {s: round(v, 2) for s, v in sectors.items()},
            "conflicts": conflicts}


# ── hypothesis identity (T119, Q89) ─────────────────────────────────────────
#
# The identity key is `subject entity + metric + threshold + source` (Q89). Two
# theses asserting the SAME hypothesis are ONE row — not two, and not merged
# silently. Q89's measured reason for the key being four fields rather than one:
# a register keyed on the subject alone would fuse "NVDA grows" with "NVDA
# margins hold", which are different claims that happen to share a ticker.

def _hypothesis_key(claim: dict[str, Any]) -> tuple | None:
    f = claim.get("falsifier") or claim.get("wrong_if")
    if isinstance(f, dict):
        metric, threshold, source = f.get("metric"), f.get("threshold"), f.get("source")
    elif isinstance(f, str) and f.count("=") >= 2:
        parts = dict(p.split("=", 1) for p in f.split() if "=" in p)
        metric = parts.get("metric")
        threshold = parts.get("threshold")
        source = parts.get("source")
    else:
        return None
    subject = claim.get("entity") or claim.get("subject")
    if not all((subject, metric, threshold, source)):
        return None
    return (str(subject), str(metric), str(threshold), str(source))


def hypothesis_register(rows: list[dict[str, Any]],
                        claims_by_thesis: dict[str, list[dict]]) -> dict[str, Any]:
    """T119/T122 (Q86/Q89): the DERIVED register — never a stored one.

    Q4's fourth application: a persisted hypothesis register would diverge from
    the theses that produced it, silently, exactly as a persisted portfolio file
    would. So it is recomputed on every run and written to
    `_portfolio/hypotheses-view.md`.

    Disagreement is the interesting case and it does NOT create a second row:
    two theses asserting one hypothesis with different conclusions become ONE row
    carrying both, and route to `conflicts.md`. A new enum value would be Q76's
    collapse; a second row would hide the disagreement by splintering it."""
    reg: dict[tuple, dict[str, Any]] = {}
    for thesis_id, claims in claims_by_thesis.items():
        for c in claims:
            if not isinstance(c, dict):
                continue
            if c.get("state") not in ACTIVE_STATES:
                continue
            key = _hypothesis_key(c)
            if key is None:
                continue          # no mechanical falsifier ⇒ not a hypothesis (T121)
            row = reg.setdefault(key, {"subject": key[0], "metric": key[1],
                                       "threshold": key[2], "source": key[3],
                                       "theses": [], "verdicts": set()})
            row["theses"].append(thesis_id)
            st = c.get("epistemic_state")
            if st:
                row["verdicts"].add(str(st))
    out = []
    for r in reg.values():
        r["theses"] = sorted(set(r["theses"]))
        r["verdicts"] = sorted(r["verdicts"])
        r["disagreeing"] = len(r["verdicts"]) > 1
        out.append(r)
    return {"rows": out,
            "conflicts": [r for r in out if r["disagreeing"]]}


def render_hypotheses(hyp: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED by portfolio_aggregate.py — DERIVED, never stored (Q86/Q4) -->",
             "", "## Hypothesis register (derived)", "",
             "| subject | metric | threshold | source | theses | epistemic |",
             "|---|---|---|---|---|---|"]
    for r in sorted(hyp["rows"], key=lambda x: (x["subject"], x["metric"])):
        flag = " ⚠️" if r["disagreeing"] else ""
        lines.append(f"| {r['subject']} | {r['metric']} | {r['threshold']} | "
                     f"{r['source']} | {len(r['theses'])} | "
                     f"{', '.join(r['verdicts']) or '—'}{flag} |")
    if not hyp["rows"]:
        lines.append("| _(none yet)_ | | | | | |")
    lines += ["", f"{len(hyp['rows'])} hypothesis/hypotheses from "
                  f"{len({t for r in hyp['rows'] for t in r['theses']})} thesis/es."]
    return "\n".join(lines) + "\n"


def render(agg: dict[str, Any]) -> str:
    lines = ["<!-- GENERATED by portfolio_aggregate.py — derived; regenerate to update -->", "",
             "## Portfolio View (derived)", "", "| ticker | conviction-weighted position | sector |",
             "|---|---|---|"]
    for t, a in sorted(agg["by_ticker"].items()):
        lines.append(f"| {t} | {a['weighted']}% | {a['sector']} |")
    lines += ["", "## Sector aggregation", "", "| sector | total |", "|---|---|"]
    for s, v in sorted(agg["by_sector"].items()):
        lines.append(f"| {s} | {v}% |")
    return "\n".join(lines) + "\n"


def render_conflicts(agg: dict[str, Any]) -> str:
    lines = ["# Cross-thesis conflicts — IC agenda input", ""]
    if not agg["conflicts"]:
        lines.append("(none)")
    for c in agg["conflicts"]:
        lines.append(f"- {c['ticker']}: opposite directions "
                     f"({' vs '.join(c['directions'])}) — adjudicate via Q66 retired_by_ic")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Derived portfolio view (Q61)")
    p.add_argument("--workspace", required=True)
    args = p.parse_args(argv)
    agg = aggregate(scan_active_claims(Path(args.workspace)))
    write_boundary.write(
        Path(args.workspace) / "_portfolio" / "portfolio-view.md",
        render(agg),
        producer='portfolio_aggregate')
    write_boundary.write(
        Path(args.workspace) / "_portfolio" / "conflicts.md",
        render_conflicts(agg),
        producer='portfolio_aggregate')
    print(f"portfolio-view.md + conflicts.md emitted — {len(agg['conflicts'])} conflict(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
