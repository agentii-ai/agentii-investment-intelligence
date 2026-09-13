---
name: fda-catalyst-devices
description: "Device-track catalyst analysis: 510(k), PMA, and De Novo decision events, CMS coverage and NTAP milestones, recalls and watch actions as risk signals, and post-market surveillance obligations — dated, verified, and sized per event for any medtech ticker or watchlist."
sectors: [med.medicines_biotech, med.medical_devices]
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Forward catalyst window default 4 quarters; up to 8 for long-horizon coverage and surveillance mapping."
allowed_tools:
  - get_device_decision
  - search_universe_devices
  - get_company_devices
  - search_companies
  - get_company_profile
  - search_documents
  - search_sec_filings
  - read_source_outline
  - read_source_pages
  - search_investment_cases
  - search_by_analogue
  - search_knowledge_entries
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught medtech catalyst frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| forward_window_quarters | 4 | Standard catalyst window; extend to 8 on request |
| include_superseded | false | Active-only events by default; supersede chains on request |
| coverage_lens | true | Coverage and NTAP milestones tracked alongside decision events |
| recall_scan | true | Recalls and watch actions surfaced as risk signals by default |
| holiday_labeling | true | Holiday-shifted weeks flagged on every calendar row |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before catalyst queries.

## Triggers

- "What device decisions (510(k)/PMA/De Novo) are coming up for [ticker]?"
- "When is the PMA decision date for [device/ticker]?"
- "Which medtech names have device decisions this quarter?"
- "What coverage or NTAP milestones are pending for [ticker]?"
- "Has [ticker] had any recalls or watch-list actions recently?"
- "Build a device catalyst calendar for my medtech watchlist."
- "How do De Novo classifications differ from 510(k) as catalysts?"
- "Evaluate the approval odds for [device] ahead of its panel."
- "What post-market surveillance obligations does [ticker] carry?"
- "Which device decisions overlap with [ticker]'s earnings date?"
- "How did similar devices trade around their decision dates?"
- "What is the installed-base story behind [ticker]'s next label expansion?"

## Production Grounding

- Device decision tracks: 510(k) clearance (substantial equivalence), PMA approval (higher evidence bar), De Novo classification (novel low-to-moderate-risk path) — each carries a binary-event dynamic.
- Reimbursement is the second gate: CMS coverage determinations and NTAP milestones convert an approval into revenue; an approval without a coverage path is a hollow catalyst.
- Recall and watch actions invert the signal: recall classes, watch lists, and post-market surveillance findings are negative catalysts that can compound.
- Device vocabulary: installed base, placements, procedures, utilization, ASP with label-expansion annotations — the commercial context for sizing the post-decision move.
- Never fabricate decision dates, recall classes, or coverage outcomes; annotate coverage gaps (per `references/knowledge-frameworks.md`).

## Data Source Priority

1. Structured decision data: `get_device_decision` (device_decision_event); asset identity via `search_universe_devices` / `get_company_devices`.
2. Filing context: `search_documents` / `search_sec_filings` for PMA submissions, recall disclosures, MDRs.
3. Coverage and NTAP milestones: `search_documents` keyword coverage/NTAP + `read_source_outline`/`read_source_pages`.
4. Historical grounding: `search_investment_cases` (device decision/recall events), `search_by_analogue`.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve ticker(s) via `search_companies`; collect company_id for device queries.
2. Pull active decision events (`get_device_decision`) and asset inventory (`get_company_devices`).
3. Overlay coverage/NTAP milestones and recall/watch actions from filings.
4. For panel meetings, retrieve briefing documents via `read_source_outline`/`read_source_pages`; apply scrutiny axes.
5. Ground the play: `search_investment_cases` / `search_by_analogue` with device filters; cite /v/ records.

### Temporal Scope
See frontmatter temporal_scope block. Post-market surveillance windows may require looking back up to 8 quarters.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Ticker resolution
2. Decision enumeration (510(k) / PMA / De Novo)
3. Coverage and NTAP milestone overlay
4. Recall and watch risk scan
5. Analogue grounding + calendar synthesis

## Modes

- **Watchlist** (default, multi-ticker): one dated calendar with per-ticker sections, sorted by date.
- **Single ticker deep-dive**: full decision timeline, coverage state, and recall history.
- **Event type**: restrict to PMA / De Novo / 510(k) / coverage / recalls on request.
- **Risk scan**: recall and watch actions as a forward-looking risk screen.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| get_device_decision empty | `search_documents` keyword decision/PMA + `search_sec_filings`; annotate coverage_gap |
| Coverage milestone not found | Flag reimbursement status unknown; never assume a coverage path |
| Recall data missing | State surveillance data unavailable; do not infer recall classes |
| Knowledge tools empty | Proceed with structured data only; annotate knowledge coverage_gap |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_fda-catalyst-devices_{affix}.md` (watchlist: `watchlist/{YYYY-MM-DD_HHMM}_fda-catalyst-devices-calendar_{affix}.md`)

## Output Structure

1. **Executive Summary** — highest-impact device-track catalysts in the window, 2-3 sentences
2. **Catalyst Calendar** — dated table: date, ticker, event type, device, application, holiday-week flag, expected-impact framing
3. **Per-Event Analysis** — decision-track assessment (evidence bar, scrutiny axes) + decision history
4. **Coverage & Reimbursement State** — coverage determinations, NTAP milestones, ASP context
5. **Recall & Surveillance Scan** — recall classes, watch actions, post-market obligations
6. **Risk Assessment & Coverage Gaps** — binary-risk sizing, signal clusters, missing data

## Error Handling

| Error | Fallback |
|-------|----------|
| No device decision rows | Fall back to earnings + pipeline events; annotate `coverage_gap` — never fabricate dates |
| 510(k) vs PMA ambiguity | State both possibilities with the evidence-bar difference; do not guess the track |
| Ticker not in med universe | Resolve via CIK/device-universe match; surface the classification gap |

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
