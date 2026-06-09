# Period-Search Subagent Prompt Construction Contract

Documents the runtime prompt construction for `period-search-subagent` instances spawned by `search_cross_period` per the period-search-subagent prompt contract.

## Overview

The `period-search-subagent` is a general-purpose per-period retriever — an internal delegation pattern within `retrieval-subagent`, spawned via the `search_cross_period` MCP tool when the temporal scope spans 2+ fiscal periods. Its prompt is **NOT a separate committed file** — it is constructed at runtime by `search_cross_period` from `retrieval.md` + per-period context injection.

## Prompt Construction

`search_cross_period` constructs each sub-agent's prompt from the following components:

### 1. `<period_scope>` Block (Prepended)

Locks the sub-agent to exactly one fiscal period:

```
<period_scope>
You are searching ONLY fiscal period {period_label}.
The earnings calendar confirms this period spans {start_date} to {end_date} for {ticker}.
Ignore filings with filing_date outside this date range.
You are one of {N} parallel sub-agents, each assigned to a different period.
Do NOT attempt cross-period comparison or synthesis — you are purely a single-period data collector.
</period_scope>
```

Where `{period_label}` is resolved from `get_company_fiscal_calendar/{ticker}` (e.g., `FY24`, `2024Q4`).

### 2. `<role>` Block

From `retrieval.md` block 1: "data-gathering and agentic search specialist. You collect evidence; do NOT synthesize, reason, or produce final deliverables."

### 3. `<retrieval_strategy>` Block

From `retrieval.md` block 2: the full 4-branch decision tree (the retrieval strategy decision tree). The **full** decision tree operates within the sub-agent — not scoped to single-period only — because the sub-agent may need structured data (`search_xbrl_facts`), unstructured document search (three-layer protocol), single-document retrieval, OR simple lookups within its assigned period.

### 4. `<three_layer_protocol>` Block

From `retrieval.md` block 3: the Layer 1→2→2.5→3 procedure with exact tool names and sequence-position guidance.

### 5. `<task>` Block (Injected at Runtime)

The specific retrieval query scoped to this period:

```
<task>
In {period_label}, {collect_task}
</task>
```

Where `{collect_task}` is the original query passed to `search_cross_period`.

### 6. `<output_contract>` Block

From `retrieval.md` block 5, scoped to single-period output:

```json
{
 "fiscal_period": "string (e.g., FY24)",
 "sources": [
 {
 "kind": "filing|xbrl|transcript|sell_side|news",
 "url": "string",
 "accession": "string",
 "page_range": "string",
 "snippet": "string",
 "citation_label": "string (v1.0 citation format)",
 "page_outline?": [
 {
 "page_no": "integer",
 "description": "string",
 "keywords": ["string"],
 "table_titles?": ["string"],
 "views?": ["string"],
 "drivers?": ["string"],
 "metrics?": ["string"]
 }
 ]
 }
 ],
 "xbrl_facts": [
 {
 "concept": "string (us-gaap:Revenues)",
 "value": "number",
 "period": "string",
 "unit": "string",
 "source_accession": "string"
 }
 ],
 "findings": [
 {
 "claim": "string (factual statement)",
 "citation_label": "string (v1.0 citation format)",
 "confidence": "string (high|medium|low)"
 }
 ],
 "coverage_gaps": [
 {
 "dimension": "string (what was sought)",
 "reason": "string (why unavailable within this period)"
 }
 ]
}
```

## Scope Confirmation

The `period-search-subagent` is a **general-purpose per-period retriever**:

- **Has access to**: BOTH `search_xbrl_facts` (structured financial data within its assigned period) AND the three-layer document retrieval tools (`search_documents`, `read_source_outline`, `read_source_pages`, `search_keyword_in_source`).
- **Decision tree**: The full 4-branch decision tree (the retrieval strategy decision tree) operates within the sub-agent. If the task asks for Revenue by segment, the sub-agent uses `search_xbrl_facts`. If it asks for management commentary, it uses the three-layer protocol.
- **Must NOT do**: Cross-period comparison or synthesis. The sub-agent is purely a single-period data collector. Cross-period verification (the parallel multi-period search mechanism(e) is the responsibility of the parent `retrieval-subagent`.

## Concurrency

- `search_cross_period` fans out period sub-queries concurrently server-side (max 8 concurrent per Neon connection pool per the concurrency limit).
- Periods beyond 8 execute in sequential batches transparently.
- The skill makes exactly ONE tool call to `search_cross_period` regardless of how many fiscal periods it covers.
