#!/usr/bin/env python3
"""knowledge_bridge.py — spec-037 MCP → enrichment record bridge (spec 039 US4, FR-018..FR-023).

Maps each enrichment preset to a spec-037 query and shapes results into the
knowledge-frameworks row format consumed by enhance-skill.insert_citations.
The spec-037 client is injected (duck-typed) so this module is unit-testable
without network/keys; enhance-skill.py supplies a real MCP-backed client at runtime.

Graceful degradation (R1/FR-023): on client error → status=coverage_gap (no rows);
on empty result → status=empty; on L4-only preset applied to non-L4 skill → status=skipped.
"""
from __future__ import annotations

from typing import Any, Optional

CITATION_TMPL = "https://agentii.ai/v/{ticker}/{citation_id}/{page}"

# Runtime analogue axis by query domain (contracts/analogue-retrieval-pattern.md).
_AXIS_KEYWORDS = {
    "strategy": ["valuation", "financial", "fundamental", "earnings", "growth"],
    "case": ["competitive", "positioning", "turnaround", "event", "merger", "case"],
    "setup": ["price action", "technical", "chart", "pattern", "setup"],
}


def select_analogue_axis(domain: str) -> str:
    d = (domain or "").lower()
    for axis, kws in _AXIS_KEYWORDS.items():
        if any(k in d for k in kws):
            return axis
    return "strategy"  # safe default


def _cite(row: dict) -> str:
    return CITATION_TMPL.format(
        ticker=row.get("ticker", "MKT"),
        citation_id=row.get("citation_id", "unknown"),
        page=row.get("page", 1),
    )


def _strategy_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        out.append({
            "citation_id": r["citation_id"],
            "columns": [r["citation_id"], r.get("title", ""), r.get("kind", ""),
                        r.get("summary", ""), _cite(r)],
        })
    return out


def _case_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        out.append({
            "citation_id": r["citation_id"],
            "columns": [r["citation_id"], r.get("title", ""), r.get("time_horizon", ""),
                        r.get("domain", ""), r.get("summary", ""), _cite(r)],
        })
    return out


def _setup_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        out.append({
            "citation_id": r["citation_id"],
            "columns": [r["citation_id"], r.get("title", ""), r.get("pattern_type", ""),
                        r.get("timeframe", ""), _cite(r)],
        })
    return out


def fetch_enrichment(client: Any, workflow_name: str, skill_entry: dict) -> dict[str, Any]:
    """Query spec-037 for a preset and return {status, records, [coverage_gap]}.

    records maps knowledge-frameworks table name -> list[{citation_id, columns}].
    """
    layers = set(skill_entry.get("layer_tags") or [])
    cats = skill_entry.get("category_tags") or []

    try:
        if workflow_name in ("strategy-enrichment", "comprehensive-enrichment"):
            raw = client.search_investment_strategies(layer_tags=list(layers), category_tags=cats, top_k=5)
            rows = _strategy_rows(raw)
            table = "strategies"
        elif workflow_name == "case-enrichment":
            raw = client.search_investment_cases(layer_tags=list(layers),
                                                 sectors_focus=skill_entry.get("sectors_focus", []), top_k=3)
            rows = _case_rows(raw)
            table = "cases"
        elif workflow_name == "setup-enrichment":
            if "L4" not in layers:
                return {"status": "skipped", "records": {},
                        "reason": "setup-enrichment is L4-only"}
            raw = client.search_technical_setups(pattern_type=skill_entry.get("pattern_type"))
            rows = _setup_rows(raw)
            table = "setups"
        else:
            return {"status": "skipped", "records": {}, "reason": f"no bridge for '{workflow_name}'"}
    except Exception as e:  # noqa: BLE001 - degrade gracefully (FR-023)
        return {"status": "coverage_gap", "records": {},
                "coverage_gap": f"spec-037 unavailable for {workflow_name}: {e}"}

    if not rows:
        return {"status": "empty", "records": {table: []}}
    return {"status": "ok", "records": {table: rows}}


def methodology_analogue_block(default_axis: str = "strategy") -> str:
    """The runtime search_by_analogue step injected into ## Methodology (FR-018/FR-023)."""
    return (
        "\n### Runtime Analogue Discovery\n"
        "1. Derive the analogue axis from the query domain "
        "(valuation→strategy, competitive→case, technical→setup).\n"
        "2. Call `search_by_analogue(target=<ticker>, axis=<axis>, top_k=3)`.\n"
        "3. Cite each hit with its `/v/` link; if empty, state "
        "\"no relevant historical analogues found\" and proceed — never fabricate.\n"
        "4. If spec-037 is unreachable, annotate `coverage_gap` and use the "
        "authoring-time knowledge-frameworks set only.\n"
    )
