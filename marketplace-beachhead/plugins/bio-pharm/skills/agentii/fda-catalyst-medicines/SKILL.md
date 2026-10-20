---
name: fda-catalyst-medicines
description: "CDER-track catalyst analysis for medicines: PDUFA target dates, AdCom votes, sNDA/sBLA label expansions, biosimilar interchangeability and 180-day exclusivity, Orange Book state, and CRL remediation timelines — enumerated, verified, and sized per event for any biotech/pharma ticker or watchlist."
sectors: [med.medicines_biotech, med.medical_devices]
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Forward catalyst window default 4 quarters; up to 8 for long-horizon exclusivity and remediation mapping."
allowed_tools:
  - get_upcoming_pdufa
  - get_pdufa_decision
  - search_adcom_meetings
  - get_adcom_meeting
  - search_fda_approvals
  - get_fda_approval
  - search_companies
  - get_company_profile
  - search_documents
  - search_sec_filings
  - list_sources
  - read_source_outline
  - read_source_pages
  - search_earnings_calendar
  - list_upcoming_earnings
  - search_investment_cases
  - get_investment_case
  - search_investment_strategies
  - get_investment_strategy
  - search_by_analogue
  - search_knowledge_entries
  - get_knowledge_entry
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught biotech catalyst frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| forward_window_quarters | 4 | Standard catalyst window; extend to 8 on request |
| include_superseded | false | Active-only events by default; supersede chains on request |
| exclusivity_tracking | true | Orange Book and 180-day exclusivity state attached to launch-relevant events |
| holiday_labeling | true | Holiday-shifted weeks flagged on every calendar row |
| horizon_days | 180 | Default for get_upcoming_pdufa horizon |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md` — carry the `_run_id` from your first tool result and name yourself (and your parent, if you were spawned). Confirm ticker resolution via `search_companies` before catalyst queries.

## Triggers

- "When is the PDUFA date for [drug/ticker]?"
- "What AdCom meetings are coming up for [ticker]?"
- "Has [drug]'s sNDA/sBLA label expansion been approved?"
- "Which biosimilars have interchangeability designation, and when does 180-day exclusivity run?"
- "What is [drug]'s Orange Book patent and exclusivity state?"
- "How is [ticker]'s CRL remediation timeline shaping up?"
- "Build a PDUFA/AdCom calendar for my pharma watchlist."
- "Evaluate the approval odds for [drug] ahead of its AdCom."
- "What label expansions are pending for [ticker] this year?"
- "Which medicine decisions land this quarter?"
- "How do biosimilar launches erode the reference product's share?"
- "Which catalysts overlap with [ticker]'s earnings date?"

## Production Grounding

- CDER mechanics: NDA/BLA review tracks, PDUFA target dates, priority review, breakthrough designation, accelerated approval, CRL deficiency classes and the remediation reset, AdCom vote patterns.
- Label expansions (sNDA/sBLA) are the commercial catalysts beyond first approval; Orange Book patent and exclusivity state sets the generic or biosimilar entry window.
- Biosimilar timeline note: interchangeability plus 180-day exclusivity for the first interchangeable delays competing entry — and approval is not launch; commercial timing follows exclusivity expiry and patent-settlement terms.
- Holiday-week labeling discipline: comps across holiday-shifted weeks are noisy; every calendar row carries its caveat, and holiday weeks are labeled explicitly.
- Apply AdCom-style scrutiny axes when framing outcome odds; never fabricate dates, votes, or outcomes — annotate coverage gaps instead (per `references/knowledge-frameworks.md`).

## Data Source Priority

1. Structured catalyst data: `get_upcoming_pdufa` / `get_pdufa_decision` (pipeline.fda_calendar_event).
2. AdCom and approval history: `search_adcom_meetings` / `get_adcom_meeting`; `search_fda_approvals` / `get_fda_approval`.
3. Company and filing context: `get_company_profile`, `search_documents`, `search_sec_filings`; briefing docs via `list_sources(source_type=adcom_briefing)` + `read_source_outline`/`read_source_pages` with meeting slugs.
4. Historical grounding: `search_investment_cases` (event_type=adcom_vote/pdufa_decision/crl/approval), `search_by_analogue`, `search_investment_strategies` (sectors=med).
5. Earnings overlap: `search_earnings_calendar` / `list_upcoming_earnings`.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve ticker(s) via `search_companies`; note primary drug/application names.
2. Pull active PDUFA events (`get_upcoming_pdufa`, horizon_days=default); layer AdCom meetings and earnings dates.
3. Per event: decision history (`get_pdufa_decision` by drug/application), approval record (`get_fda_approval`), label and Orange Book state.
4. For AdCom events, retrieve briefing documents via `list_sources` + `read_source_outline`/`read_source_pages` using meeting slugs; apply scrutiny axes.
5. Ground the play in knowledge: `search_investment_cases` / `search_by_analogue` with med filters; cite /v/ records.

### Temporal Scope
See frontmatter temporal_scope block. Exclusivity windows may require looking back up to 8 quarters when requested.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Ticker resolution
2. Catalyst enumeration (PDUFA / AdCom / label expansion / exclusivity events)
3. Per-event outcome framing (scrutiny axes + decision history)
4. Historical analogue retrieval
5. Calendar synthesis + exclusivity and risk flags

## Modes

- **Watchlist** (default, multi-ticker): one dated calendar with per-ticker sections, sorted by date.
- **Single ticker deep-dive**: full event timeline, per-event probability framing, label and exclusivity state.
- **Event type**: restrict to PDUFA / AdCom / label expansion / biosimilar milestones on request.
- **Exclusivity scan**: Orange Book and 180-day windows as the launch-timing lens.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_upcoming_pdufa empty | Search filings (`search_documents` keyword PDUFA) + `search_sec_filings` 8-Ks; annotate coverage_gap |
| AdCom briefing path 404 | `search_documents` with source_institution filter; degrade to calendar metadata |
| Knowledge tools empty | Proceed with structured data only; annotate knowledge coverage_gap |
| Orange Book state unknown | Flag exclusivity window unavailable; never infer expiry dates |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_fda-catalyst-medicines_{affix}.md` (watchlist: `watchlist/{YYYY-MM-DD_HHMM}_fda-catalyst-medicines-calendar_{affix}.md`)

## Output Structure

1. **Executive Summary** — highest-impact CDER-track catalysts in the window, 2-3 sentences
2. **Catalyst Calendar** — dated table: date, ticker, event type, drug, application, holiday-week flag, expected-impact framing
3. **Per-Event Analysis** — scrutiny-axes assessment (safety/statistics/subgroups/benefit-risk) + decision history
4. **Label & Exclusivity State** — sNDA/sBLA status, Orange Book state, 180-day windows, biosimilar entry timing
5. **Historical Analogues** — matched cases with /v/ citations and quantified outcomes
6. **Risk Assessment & Coverage Gaps** — binary-risk sizing, overlap clusters, unverified or missing data

## Error Handling

| Error | Fallback |
|-------|----------|
| No PDUFA rows | Fall back to earnings + AdCom + label events; annotate `coverage_gap` — never fabricate dates |
| Superseded dates | Active-only by default; expose supersede chain via `include_superseded=true` |
| Ticker not in med universe | Resolve via CIK/drug-universe match; surface the classification gap |

## Memory Load

See `contracts/memory-load.md`.

## Snapshot

See `contracts/snapshot-synthesis.md`.

## Final Summary (TUI)

Include ### Key Citations block with 0-10 clickable /v/ URLs.

## References

- `contracts/citation-and-memory.md`
- `contracts/output-frontmatter-schema.md`
- `contracts/memory-load.md`
- `contracts/snapshot-synthesis.md`
- `contracts/preflight.md`
- `references/knowledge-frameworks.md`
