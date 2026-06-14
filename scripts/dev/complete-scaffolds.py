#!/usr/bin/env python3
"""
Idempotent scaffold-completion migration for vertical-plugin SKILL.md files.

Brings every skill up to the contracts/skill-methodology-template.md + check.py
contract that the previously-dead CI gate (skills/*/SKILL.md glob bug) had been
silently skipping. Safe to re-run — only inserts what is missing.

Transforms (all idempotent):
  1. Frontmatter: add multi_ticker_semantics (curated map) if absent.
  2. Frontmatter: repair the corrupted `retrieval_scope: <x>\n  - read_source_deep_outline`
     orphan-list-item bug; for unstructured_document_search skills the deep-outline
     tool is moved INTO allowed_tools (FR-116, eligible); for structured_only it is
     dropped (retrieval.md Layer 2.5a — not available to structured_only).
  3. Frontmatter: strip document-retrieval tools from structured_only allowed_tools
     (FR-060 / check.py Check 21).
  4. Body: ensure a `## Preflight` section carrying the X-Agentii-Trace block.
  5. Body: ensure `## Methodology` has all 5 required subsections.
  6. Body: ensure `## Output Structure` has >= 5 non-empty lines + path template.
  7. models-and-pitches: ensure `## Deliverable Chain` + `## Validation Gates`
     and references/{formula-sheet,validation-checklist,institutional-defaults}.md.

Usage: python3 scripts/dev/complete-scaffolds.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERTICALS = ROOT / "plugins" / "vertical-plugins"

DOCUMENT_TOOLS = {
    "read_source_outline", "read_source_deep_outline", "read_source_pages",
    "search_keyword_in_source", "search_documents", "search_sec_filings",
}

MTS_REQUIRED_PEERS = {"comps", "peer-bench", "competitive", "competitive-positioning"}
# Sector/thematic skills analyze a theme with optional tickers. basket_v1_1 is
# reserved/forbidden at v1.0 (validate-multi-ticker-syntax.py), so use optional-peers.
MTS_OPTIONAL = {
    "valuation-methods", "dcf", "lbo", "sotp-valuation", "ddm-valuation",
    "peg-valuation", "reverse-dcf", "residual-income", "ratio-analysis",
    "growth-strategy", "business-model", "revenue-decomp",
    "sector-overview", "supply-chain", "secular-trends",
}

TOOL_JUSTIFY = {
    "search_companies": "ticker resolution + company context (entity-alias fuzzy match)",
    "search_xbrl_facts": "primary structured financial facts (is_primary default)",
    "list_xbrl_concepts": "US-GAAP concept discovery for non-standard line items",
    "get_company_financials": "consolidated IS/BS/CF highlights",
    "get_company_profile": "sector/industry classification + metadata",
    "search_earnings_calendar": "EPS actual/estimate/surprise + report dates",
    "get_company_fiscal_calendar": "fiscal period format resolution (FY vs Q4)",
    "get_ticker_coverage": "pre-flight data-source coverage routing",
    "list_coverage": "universe-level coverage discovery",
    "search_documents": "Layer 1 document discovery (page-level silver records)",
    "search_sec_filings": "Layer 1 SEC filing metadata index",
    "read_source_outline": "Layer 2 lightweight page map (description + keywords)",
    "read_source_deep_outline": "Layer 2.5a deep page map (table_titles/drivers/metrics)",
    "search_keyword_in_source": "Layer 2.5b keyword page filter for large documents",
    "read_source_pages": "Layer 3 deep read of selected pages with table markers",
    "search_cross_period": "server-side parallel multi-period three-layer retrieval",
    "get_entity_knowledge": "knowledge-graph entity facts",
    "list_domains": "knowledge-domain discovery",
    "read_rendered_statement": "pre-rendered financial statement HTML/markdown",
    "get_statement": "XBRL Part B statement assembly",
    "get_statement_structure": "XBRL presentation tree (concept hierarchy)",
    "get_calculation_tree": "XBRL calculation linkbase (weights)",
    "validate_calculation": "XBRL calc-consistency validation",
    "get_financial_ratios": "pre-computed profitability/efficiency/leverage ratios",
    "get_segment_data": "segment/product/geography dimensional breakdown",
    "get_realtime_quote": "latest market price for valuation cross-checks",
    "batch_search": "consolidate 3+ same-tool queries into one metered call",
}

PREFLIGHT_PROBE = (
    '!curl -s -o /dev/null -w "%{http_code}" --max-time 2 '
    'https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"'
)
TRACE_BLOCK = (
    "**Agent Call Tracing**: The first tool you call will return a `_run_id` in its "
    "result. On every subsequent tool call, include HTTP header "
    "`X-Agentii-Trace: agent={skill_name}; parent={caller_name}; instance={instance_label}`. "
    "The MCP server will inject run_id, depth, and user_id automatically. When spawning "
    "parallel sub-agents of the same type, assign each a unique instance label (e.g., "
    "equity-research-1, equity-research-2). See `contracts/x-agentii-trace-header.md` for "
    "the full contract."
)

MODELS = "models-and-pitches"


def split_fm(text: str):
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parts[1], parts[2]


def get_scalar(fm: str, key: str):
    m = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", fm, re.MULTILINE)
    return m.group(1).strip() if m else None


def get_list(fm: str, key: str):
    m = re.search(rf"^{re.escape(key)}:\s*\n((?:[ \t]*-\s*.+\n?)+)", fm, re.MULTILINE)
    if not m:
        return []
    return [re.sub(r"^[ \t]*-\s*", "", ln).strip() for ln in m.group(1).splitlines() if ln.strip()]


def mts_for(name: str) -> str:
    if name in MTS_REQUIRED_PEERS:
        return "target_with_required_peers"
    if name in MTS_OPTIONAL:
        return "target_with_optional_peers"
    return "single_target"


def temporal(fm: str):
    blk = re.search(r"^temporal_scope:\s*\n((?:[ \t]+.+\n?)+)", fm, re.MULTILINE)
    body = blk.group(1) if blk else ""
    dq = re.search(r"default_quarters:\s*(\d+)", body)
    mq = re.search(r"max_quarters:\s*(\d+)", body)
    return (dq.group(1) if dq else "1"), (mq.group(1) if mq else "4")


def subsection_bodies(name: str, rs: str, tools: list[str], dq: str, mq: str) -> dict[str, str]:
    """Return generated body text (without heading) for each of the 5 subsections."""
    scope_sent = {
        "structured_only": "This skill performs structured data retrieval only (XBRL facts, financials, earnings calendar) — no unstructured document search.",
        "unstructured_document_search": "This skill performs unstructured document search at scale via the three-layer protocol (Layer 1→2→2.5→3), escalating to `read_source_deep_outline` only when lightweight labels cannot disambiguate pages.",
        "simple_lookup": "This skill uses only profile/entity metadata tools — no document or XBRL retrieval at scale.",
        "single_document": "This skill targets a single known document via direct `read_source_outline` → `read_source_pages`.",
    }.get(rs, "This skill follows the agentii retrieval protocol.")
    branch = {
        "structured_only": "(a) Structured Data Query",
        "unstructured_document_search": "(b)/(c) Unstructured Query via the three-layer protocol",
        "simple_lookup": "(d) Simple Lookup",
        "single_document": "(c) Single-Document Query",
    }.get(rs, "(a) Structured Data Query")
    tool_lines = "\n".join(
        f"- `{t}` — {TOOL_JUSTIFY.get(t, 'used by this skill per the retrieval strategy')}"
        for t in tools
    ) or "- (declared in frontmatter `allowed_tools`)"
    return {
        "Retrieval Scope": f"`retrieval_scope: {rs}`. {scope_sent}",
        "Retrieval Strategy": (
            f"Follows the retrieval strategy decision tree in `retrieval.md`. Primary branch: **{branch}**. "
            "Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call."
        ),
        "Temporal Scope": (
            f"Default lookback: {dq} fiscal quarter(s); maximum: {mq}. "
            "The default balances recency against the trend window this analysis requires."
        ),
        "Tool Allowlist": "Per frontmatter `allowed_tools`:\n\n" + tool_lines,
    }


def build_methodology(name: str, rs: str, tools: list[str], dq: str, mq: str) -> str:
    scope_sent = {
        "structured_only": "It performs structured data retrieval only (XBRL facts, financials, earnings calendar) — no unstructured document search. Document-retrieval tools are excluded from `allowed_tools`.",
        "unstructured_document_search": "It performs unstructured document search at scale via the three-layer retrieval protocol (Layer 1→2→2.5→3), escalating to `read_source_deep_outline` only when lightweight labels cannot disambiguate pages, plus structured XBRL where needed.",
        "simple_lookup": "It uses only profile/entity metadata tools — no document or XBRL retrieval at scale.",
        "single_document": "It targets a single known document via direct `read_source_outline` → `read_source_pages`.",
    }.get(rs, "It follows the agentii retrieval protocol.")
    branch = {
        "structured_only": "(a) Structured Data Query",
        "unstructured_document_search": "(b)/(c) Unstructured Query via the three-layer protocol",
        "simple_lookup": "(d) Simple Lookup",
        "single_document": "(c) Single-Document Query",
    }.get(rs, "(a) Structured Data Query")
    tool_lines = "\n".join(
        f"- `{t}` — {TOOL_JUSTIFY.get(t, 'used by this skill per the retrieval strategy')}"
        for t in tools
    ) or "- (declared in frontmatter `allowed_tools`)"

    if rs == "structured_only":
        proto = (
            "1. **Pre-flight (mandatory)**: call `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`; route on coverage.\n"
            "2. **Concept discovery** (non-standard concepts only): `list_xbrl_concepts(query=<term>, ticker=<T>)`.\n"
            "3. **Structured retrieval**: `search_xbrl_facts(ticker, concept=[...], fiscal_year=[...])` (is_primary default) and/or `get_company_financials/{ticker}`.\n"
            "4. **Batch rule**: 3+ same-tool queries → consolidate via `batch_search` (≤8 sub-queries).\n"
            "5. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`."
        )
    elif rs == "simple_lookup":
        proto = (
            "1. **Pre-flight**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`.\n"
            "2. **Lookup**: `get_company_profile/{ticker}` / `get_entity_knowledge` for the requested metadata field(s).\n"
            "3. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`."
        )
    else:  # unstructured / single_document
        proto = (
            "1. **Pre-flight (mandatory)**: `get_company_fiscal_calendar/{ticker}` then `get_ticker_coverage/{ticker}`; route on coverage.\n"
            "2. **Layer 1 — discovery**: `search_documents` / `search_sec_filings` to find candidate filings by ticker/form_type/date.\n"
            "3. **Layer 2 — page map**: `read_source_outline/{ticker}/{citation_id}`; skip NULL-description pages; escalate to `read_source_deep_outline` only when labels can't disambiguate.\n"
            "4. **Layer 2.5 (optional)**: `search_keyword_in_source` to narrow documents >50 pages.\n"
            "5. **Layer 3 — deep read**: `read_source_pages/{ticker}/{citation_id}?row_numbers=page<N>,...` for the 3–5 selected pages only.\n"
            "6. **Multi-period** (if applicable): `search_cross_period` after fiscal-calendar resolution.\n"
            "7. **Output**: write the deliverable per `## Output File`, then append to `agentii.md`."
        )

    return (
        "## Methodology\n\n"
        "### 1. Retrieval Scope\n\n"
        f"This skill operates with `retrieval_scope: {rs}`. {scope_sent}\n\n"
        "### 2. Retrieval Strategy\n\n"
        f"Follows the retrieval strategy decision tree in `retrieval.md`. Primary branch: **{branch}**. "
        "Resolve the canonical ticker first (exact → fuzzy alias → share-class) before any data call.\n\n"
        "### 3. Temporal Scope\n\n"
        f"Default lookback: {dq} fiscal quarter(s); maximum: {mq}. The default balances recency against the trend window this analysis requires.\n\n"
        "### 4. Tool Allowlist\n\n"
        "Per frontmatter `allowed_tools`:\n\n"
        f"{tool_lines}\n\n"
        "### 5. Protocol\n\n"
        f"{proto}\n"
    )


OUTPUT_STRUCTURE = (
    "## Output Structure\n\n"
    "Write to `{ticker}/{YYYY-MM-DD_HHMM}_%(name)s_{affix}.md` (see `## Output File`).\n\n"
    "1. **Executive Summary** (≤200 words) — headline conclusions for the analysis.\n"
    "2. **Data Sources** — filings + structured endpoints used, with `{ticker} {citation_id} page<N>` citations.\n"
    "3. **Analysis** — the core findings, tables, and commentary for this dimension.\n"
    "4. **Key Metrics** — the quantitative results with QoQ/YoY context where relevant.\n"
    "5. **Coverage Gaps & Citations** — data not retrievable + citation index.\n\n"
    "**Citation density**: ≥1 citation per 200 words; bare `page_no` integers are forbidden — "
    "always cite as `{ticker} {citation_id} page<N>`. After writing, append a YAML block to "
    "`agentii.md` per `contracts/agentii-md-schema.md`.\n"
)

DELIVERABLE_CHAIN = (
    "## Deliverable Chain\n\n"
    "**Inputs** → **Build** → **Validate** → **Output** → **Next**\n\n"
    "1. **Inputs**: resolved ticker + structured facts (`search_xbrl_facts`, `get_company_financials`) and any filing pages from the three-layer protocol.\n"
    "2. **Build**: assemble the workbook/deck spec and call `xlsx.build` / `pptx.build` (office plane).\n"
    "3. **Validate**: run `xlsx.audit` (or recalc) and the `## Validation Gates` below.\n"
    "4. **Output**: write the artifact path per `## Output File`.\n"
    "5. **Next**: append to `agentii.md`; hand off to a downstream pitch/review skill if requested.\n"
)

VALIDATION_GATES = (
    "## Validation Gates\n\n"
    "1. **Sources tie to filings** — every input figure carries a `{ticker} {citation_id} page<N>` citation or an XBRL `source_accession`.\n"
    "2. **Recalc clean** — `xlsx.audit` / recalc returns zero hardcoded-over-formula overrides in computed cells.\n"
    "3. **Balance checks** — statement identities hold (Assets = Liabilities + Equity; CF ties to cash delta) within rounding.\n"
    "4. **Coverage attestation** — any missing dimension is listed in the Coverage Gaps section, never silently dropped.\n"
)

REF_FILES = {
    "formula-sheet.md": "# Formula Sheet\n\nCanonical formulas for this model. All figures must tie to XBRL facts or cited filing pages.\n\n- Revenue growth = (Rev_t / Rev_{t-1}) - 1\n- Gross margin = GrossProfit / Revenues\n- Operating margin = OperatingIncomeLoss / Revenues\n- FCF = OperatingCashFlow - CapEx\n",
    "validation-checklist.md": "# Validation Checklist\n\n- [ ] Every input figure cites a filing page or XBRL accession.\n- [ ] Recalc/audit returns no hardcoded-over-formula cells.\n- [ ] Statement identities balance within rounding.\n- [ ] Period labels match `get_company_fiscal_calendar`.\n- [ ] Coverage gaps are surfaced, not silently dropped.\n",
    "institutional-defaults.md": "# Institutional Defaults\n\n- Lookback: per skill `temporal_scope`.\n- Currency: reporting currency from the first XBRL fact `unit` (no conversion at v1.0).\n- XBRL: `is_primary = true` default; `?include_all_sources=true` only for audit/reconciliation.\n- Dedup: API-side; do not re-implement client-side.\n",
}


def process(path: Path) -> list[str]:
    name = path.parent.name
    vertical = path.parents[3].name  # .../<vertical>/skills/agentii/<name>/SKILL.md
    text = path.read_text()
    fm, body = split_fm(text)
    if fm is None:
        return [f"SKIP (no frontmatter): {name}"]
    changes: list[str] = []

    # --- 2. repair corrupted retrieval_scope orphan ---
    rs = get_scalar(fm, "retrieval_scope") or ""
    if " - read_source_deep_outline" in rs or "read_source_deep_outline" in rs.split():
        rs = rs.split(" - ")[0].strip()
    # also remove a literal orphan line form
    fm2 = re.sub(r"(^retrieval_scope:\s*\S+).*$", r"\1", fm, flags=re.MULTILINE)
    fm2 = re.sub(r"^\s*-\s*read_source_deep_outline\s*\n", "", fm2, flags=re.MULTILINE)
    if fm2 != fm:
        changes.append("repaired retrieval_scope orphan")
        fm = fm2
    rs = (get_scalar(fm, "retrieval_scope") or "").split(" - ")[0].strip()

    tools = get_list(fm, "allowed_tools")

    # --- 3 + FR-116: tools per retrieval_scope ---
    new_tools = list(tools)
    if rs == "structured_only":
        new_tools = [t for t in new_tools if t not in DOCUMENT_TOOLS]
    elif rs == "unstructured_document_search":
        if "read_source_deep_outline" not in new_tools:
            # insert right after read_source_outline if present, else append
            if "read_source_outline" in new_tools:
                new_tools.insert(new_tools.index("read_source_outline") + 1, "read_source_deep_outline")
            else:
                new_tools.append("read_source_deep_outline")
    if new_tools != tools:
        # rebuild the allowed_tools block preserving indent style " - "
        indent_m = re.search(r"^allowed_tools:\s*\n([ \t]*)-", fm, re.MULTILINE)
        ind = indent_m.group(1) if indent_m else " "
        block = "allowed_tools:\n" + "".join(f"{ind}- {t}\n" for t in new_tools)
        fm = re.sub(r"^allowed_tools:\s*\n(?:[ \t]*-\s*.+\n?)+", block, fm, flags=re.MULTILINE)
        changes.append(f"allowed_tools {len(tools)}→{len(new_tools)} (scope={rs})")
        tools = new_tools

    # --- 1. multi_ticker_semantics ---
    if "multi_ticker_semantics" not in fm:
        val = mts_for(name)
        fm = re.sub(r"(^name:\s*.+\n)", rf"\1multi_ticker_semantics: {val}\n", fm, count=1, flags=re.MULTILINE)
        changes.append(f"+multi_ticker_semantics: {val}")

    # reassemble
    text = "---" + fm + "---" + body

    # --- 4. Preflight section ---
    if "## Preflight" not in text:
        pf = f"## Preflight\n\n{PREFLIGHT_PROBE}\n\n{TRACE_BLOCK}\n\n"
        # drop a loose trace block if present (it will live under Preflight)
        text = text.replace(TRACE_BLOCK + "\n", "")
        # insert before first '## ' section after the H1 title
        m = re.search(r"^(# .+\n)(.*?)(?=^## )", text, re.DOTALL | re.MULTILINE)
        if m:
            text = text[: m.end()] + pf + text[m.end():]
            changes.append("+## Preflight")

    # --- 5. Methodology subsections (per-subsection, preserves custom Protocol) ---
    dq, mq = temporal(fm)
    SUBS_ORDER = ["Retrieval Scope", "Retrieval Strategy", "Temporal Scope", "Tool Allowlist", "Protocol"]
    present = {
        s: bool(re.search(rf"^###\s+(?:\d+\.\s+)?{re.escape(s)}\b", text, re.MULTILINE))
        for s in SUBS_ORDER
    }
    if not all(present.values()):
        if not re.search(r"^## Methodology\b", text, re.MULTILINE):
            # no methodology at all → insert a full block before Output File/Structure
            method = build_methodology(name, rs or "structured_only", tools, dq, mq)
            anchor = re.search(r"^## (Output File|Output Structure|Error Handling)\b", text, re.MULTILINE)
            if anchor:
                text = text[: anchor.start()] + method + "\n" + text[anchor.start():]
            changes.append("+## Methodology (full)")
        elif not any(present[s] for s in SUBS_ORDER):
            # methodology heading exists but has zero subsections (placeholder body)
            method = build_methodology(name, rs or "structured_only", tools, dq, mq)
            text = re.sub(r"^## Methodology\b.*?(?=^## )", method + "\n", text, count=1, flags=re.DOTALL | re.MULTILINE)
            changes.append("+## Methodology subsections")
        else:
            # partial methodology → insert only missing subsections before Protocol (or end)
            bodies = subsection_bodies(name, rs or "structured_only", tools, dq, mq)
            insert_at = re.search(r"^###\s+(?:\d+\.\s+)?Protocol\b", text, re.MULTILINE)
            if not insert_at:
                # before the next '## ' after Methodology
                m_meth = re.search(r"^## Methodology\b", text, re.MULTILINE)
                nxt = re.search(r"^## ", text[m_meth.end():], re.MULTILINE)
                pos = m_meth.end() + nxt.start() if nxt else len(text)
            else:
                pos = insert_at.start()
            block = ""
            for s in SUBS_ORDER:
                if s == "Protocol" or present[s]:
                    continue
                block += f"### {s}\n\n{bodies[s]}\n\n"
            if block:
                text = text[:pos] + block + text[pos:]
                changes.append("+missing methodology subsections: " + ", ".join(s for s in SUBS_ORDER if not present[s] and s != "Protocol"))

    # --- 6. Output Structure >=5 lines ---
    osec = re.search(r"^## Output Structure\s*\n(.*?)(?=^## )", text, re.DOTALL | re.MULTILINE)
    nonempty = len([l for l in osec.group(1).splitlines() if l.strip()]) if osec else 0
    if nonempty < 5:
        block = OUTPUT_STRUCTURE % {"name": name}
        if osec:
            text = text[: osec.start()] + block + "\n" + text[osec.end():]
        else:
            anchor = re.search(r"^## Error Handling\b", text, re.MULTILINE)
            if anchor:
                text = text[: anchor.start()] + block + "\n" + text[anchor.start():]
        changes.append("enriched ## Output Structure")

    # --- 7. models-and-pitches extras ---
    if vertical == MODELS:
        if "## Deliverable Chain" not in text:
            anchor = re.search(r"^## (Validation Gates|Tool Fallbacks|Output File)\b", text, re.MULTILINE)
            if anchor:
                text = text[: anchor.start()] + DELIVERABLE_CHAIN + "\n" + text[anchor.start():]
                changes.append("+## Deliverable Chain")
        if "## Validation Gates" not in text:
            anchor = re.search(r"^## (Tool Fallbacks|Output File)\b", text, re.MULTILINE)
            if anchor:
                text = text[: anchor.start()] + VALIDATION_GATES + "\n" + text[anchor.start():]
                changes.append("+## Validation Gates")
        refs = path.parent / "references"
        for fn, content in REF_FILES.items():
            fp = refs / fn
            if not fp.exists() or fp.stat().st_size < 50:
                refs.mkdir(exist_ok=True)
                fp.write_text(content)
                changes.append(f"+references/{fn}")

    if changes:
        path.write_text(text)
    return [f"{vertical}/{name}: {', '.join(changes)}"] if changes else []


def main():
    total = 0
    for path in sorted(VERTICALS.glob("*/skills/agentii/*/SKILL.md")):
        for line in process(path):
            print(line)
            total += 1
    print(f"\n{total} skill(s) modified.")


if __name__ == "__main__":
    main()
