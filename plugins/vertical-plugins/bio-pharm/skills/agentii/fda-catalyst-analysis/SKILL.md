---
name: fda-catalyst-analysis
description: Dated FDA catalyst calendar (PDUFA target dates, AdCom meetings, device decisions, trial readouts, earnings) with AdCom-style scrutiny outcome framing and historical-case grounding. The FDA decision is the strongest stock catalyst in med.medicines_biotech — use this skill to enumerate, verify, and size upcoming catalysts for any biotech/pharma ticker or watchlist.
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Forward catalyst window default 4 quarters; up to 8 for long-horizon pipeline mapping."
allowed_tools:
  - get_upcoming_pdufa
  - get_pdufa_decision
  - get_device_decision
  - search_adcom_meetings
  - get_adcom_meeting
  - search_clinical_trials
  - get_clinical_trial
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
  - search_technical_setups
  - get_technical_setup
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
| include_superseded | false | Active-only events by default; supersede chains available on request |
| min_verification | false | Show all events; annotate unverified instead of hiding |
| horizon_days | 180 | Default for get_upcoming_pdufa horizon |
| domain | event-driven | Med catalyst analysis is event-driven by construction |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before catalyst queries.

## Triggers

- "What FDA catalysts are coming up for [ticker]?"
- "When is the PDUFA date for [drug/ticker]?"
- "Build a catalyst calendar for my biotech watchlist."
- "What AdCom meetings are scheduled for [ticker]?"
- "How does the market typically react to [approval/CRL/AdCom vote]?"
- "What are the binary events for [ticker] over the next 6 months?"
- "Which med names have FDA decisions this quarter?"
- "Evaluate the approval odds for [drug] ahead of its PDUFA."
- "What happened the last time a similar drug went to AdCom?"
- "List upcoming device decisions (PMA/De Novo/510(k)) for [ticker]."
- "Which catalysts overlap with [ticker]'s earnings date?"
- "Recap the decision history for [application/drug]."

## Production Grounding

- FDA decisions (approve/CRL/withdraw) are the strongest price catalysts in `med.medicines_biotech`; AdCom votes often pre-move the stock by days.
- Regulatory mechanics: PDUFA target dates, priority review, breakthrough designation, accelerated approval, CRL remediation timelines, AdCom vote patterns (approve/reject/deferral/conditional), post-marketing requirements.
- AdCom-style scrutiny axes to apply when framing outcome odds: safety signals, statistical adequacy, subgroup analyses, missing data, endpoint appropriateness, benefit-risk reasoning (per `references/knowledge-frameworks.md`).
- Devices: PMA / De Novo / 510(k) decisions carry similar binary-event dynamics (`get_device_decision`).
- Never fabricate dates, votes, or outcomes. When a tool returns nothing, annotate the coverage gap.

## Data Source Priority

1. Structured catalyst data: `get_upcoming_pdufa` / `get_pdufa_decision` / `get_device_decision` (pipeline.fda_calendar_event / device_decision_event).
2. Trial context: `search_clinical_trials` / `get_clinical_trial`; approval history: `search_fda_approvals` / `get_fda_approval`.
3. Company/filing context: `get_company_profile`, `search_documents`, `read_source_outline/pages` (incl. adcom briefing docs via meeting slugs).
4. Historical grounding: `search_investment_cases` (sectors=med, event_type=adcom_vote/pdufa_decision/crl/approval), `search_by_analogue`, `search_investment_strategies` (sectors=med).
5. Earnings overlap: `search_earnings_calendar` / `list_upcoming_earnings`.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve ticker(s) via `search_companies`; collect company_id/cik for device queries.
2. Pull active catalyst events: `get_upcoming_pdufa` (ticker, horizon_days=default), `get_device_decision`, upcoming earnings.
3. For each major event, pull decision history (`get_pdufa_decision` by drug/application) and trial context (`search_clinical_trials`).
4. For AdCom events, retrieve the meeting documents via `list_sources(source_type=adcom_briefing)` + `read_source_outline/pages` using meeting slug citations; apply scrutiny axes.
5. Ground the play in knowledge: `search_investment_cases`/`search_by_analogue` with med filters; cite /v/ records.

### Temporal Scope
See frontmatter temporal_scope block. Historical decision history may span up to 8 quarters back when requested.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Ticker resolution
2. Catalyst enumeration (dated events)
3. Per-event outcome framing (scrutiny axes + decision history)
4. Historical analogue retrieval
5. Calendar synthesis + risk flags

## Modes

- **Watchlist** (default, multi-ticker): produce one calendar with per-ticker sections; sort by date.
- **Single ticker deep-dive**: full event timeline + per-event probability framing + positioning context.
- **Event type**: restrict to PDUFA / AdCom / devices / trials / earnings on request.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_upcoming_pdufa empty | Search filings (`search_documents` keyword PDUFA) + `search_sec_filings` 8-Ks; annotate coverage_gap |
| AdCom retrieval path 404 | `search_documents` with source_institution filter; degrade to calendar metadata |
| search_clinical_trials unavailable | Use filings/announcements; flag degraded |
| Knowledge tools empty | Proceed with structured data only; annotate knowledge coverage_gap |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_fda-catalyst-analysis_{affix}.md` (watchlist: `watchlist/{YYYY-MM-DD_HHMM}_fda-catalyst-calendar_{affix}.md`)

## Output Structure

1. **Executive Summary** — highest-impact catalysts in the window, 2-3 sentences
2. **Catalyst Calendar** — dated table: date, ticker, event type, drug/device, application, expected-impact framing
3. **Per-Event Analysis** — scrutiny-axes assessment (safety/statistics/subgroups/benefit-risk) + decision history
4. **Historical Analogues** — matched cases with /v/ citations and quantified outcomes
5. **Risk Assessment** — binary-risk sizing, overlap clusters, low-verification flags
6. **Coverage Gaps** — missing data, degraded modes, unverified events

## Error Handling

| Error | Fallback |
|-------|----------|
| No PDUFA rows | Fall back to earnings + pipeline events; annotate `coverage_gap` — never fabricate dates |
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
