---
name: fda-catalyst-vaccines
description: "Vaccine catalyst analysis across the two-gate path: CBER BLA review and the ACIP recommendation gate that turns FDA approval into commercial availability. Lot release, procurement milestones, pediatric bridging, and healthy-population efficacy context — dated, verified, and sized per event."
sectors: [med.medicines_biotech, med.medical_devices]
category_tags:
  - fda-catalysts
  - acip
  - vaccines
multi_ticker_semantics: basket_v1_1
temporal_scope:
  default_quarters: 4
  max_quarters: 8
  description: "Forward catalyst window default 4 quarters; up to 8 for multi-season campaign and bridging cycles."
allowed_tools:
  - search_acip_events
  - get_acip_event
  - get_upcoming_pdufa
  - search_adcom_meetings
  - search_fda_approvals
  - search_companies
  - search_documents
  - search_sec_filings
  - search_investment_cases
  - search_by_analogue
  - search_knowledge_entries
retrieval_scope: unstructured_document_search
min_tool_diversity: 3
parameter_free: false
---

> Methodology inspired by publicly taught vaccine commercial frameworks; all text is an original paraphrase.

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| forward_window_quarters | 4 | Standard catalyst window; extend to 8 on request |
| include_superseded | false | Active-only events by default; supersede chains on request |
| acip_gate | true | ACIP status always shown next to FDA decisions — approval is not availability |
| procurement_lens | true | Government purchasing and campaign milestones tracked |
| holiday_labeling | true | Holiday-shifted weeks flagged on every calendar row |

## Preflight

Run canonical pre-flight per `contracts/preflight.md`. Propagate X-Agentii-Trace per `contracts/x-agentii-trace-header.md`. Confirm ticker resolution via `search_companies` before catalyst queries.

## Triggers

- "When is [vaccine]'s ACIP meeting, and what is the vote outlook?"
- "Is [vaccine] FDA-approved but still awaiting an ACIP recommendation?"
- "What does the ACIP vote mean for [ticker]'s commercial launch?"
- "What procurement milestones are pending for [vaccine/ticker]?"
- "When is lot release expected for [vaccine]?"
- "What pediatric or age-cohort bridging studies are pending?"
- "Build a vaccine catalyst calendar for my watchlist."
- "Which vaccine decisions land this quarter?"
- "How do ACIP recommendation categories change uptake?"
- "What happens between FDA approval and commercial availability?"
- "Which vaccine catalysts overlap with [ticker]'s earnings date?"
- "How did similar vaccines trade around their ACIP votes?"

## Production Grounding

- Two-gate path: FDA approval (CBER BLA) is necessary but not sufficient — the ACIP row (scheduled → voted → adopted) is the gate data, with CDC Director sign-off and MMWR publication distinct steps from the vote.
- ACIP recommendation categories (routine / catch-up / risk-based / shared-clinical-decision-making) set the uptake ceiling; votes move stocks like PDUFA dates move drug names.
- CBER context: healthy-population efficacy bar (large N, safety-first), lot-release testing, and manufacturing capacity as a catalyst in its own right.
- Procurement milestones: government stockpiles and purchase contracts (doses/serials, procurement value), seasonal campaign timing.
- Pediatric bridging, booster cycles, and age-cohort expansions re-open the catalyst window after launch.
- Holiday-week labeling discipline: campaign-week comps are noisy; label holiday weeks explicitly. Never fabricate votes, dates, or procurement values (per `references/knowledge-frameworks.md`).

## Data Source Priority

1. ACIP gate data: `search_acip_events` / `get_acip_event` (vote counts, status ladder).
2. FDA/CBER track: `get_upcoming_pdufa` / `search_fda_approvals` (BLA events).
3. Panel and filing context: `search_adcom_meetings` (VRBPAC) + `search_documents` / `search_sec_filings` for procurement and lot-release disclosures.
4. Historical grounding: `search_investment_cases` (acip_vote/approval events), `search_by_analogue`.

## Methodology

### Retrieval Scope
unstructured_document_search

### Retrieval Strategy
1. Resolve ticker(s) via `search_companies`; note vaccine product names.
2. Pull ACIP events (`search_acip_events`) and FDA-track dates (`get_upcoming_pdufa`); pair them per product.
3. For each ACIP event, retrieve vote detail (`get_acip_event` by vaccine + meeting date) and panel context.
4. Layer procurement and lot-release milestones from filings (`search_sec_filings` 8-Ks, `search_documents`).
5. Ground the play: `search_investment_cases` / `search_by_analogue` with vaccine filters; cite /v/ records.

### Temporal Scope
See frontmatter temporal_scope block. Seasonal campaigns may require looking back up to 8 quarters.

### Tool Allowlist
See frontmatter allowed_tools.

### Protocol
1. Ticker resolution
2. Two-gate enumeration (FDA date + ACIP row per product)
3. Per-event vote framing (recommendation category + history)
4. Procurement and lot-release overlay
5. Calendar synthesis + commercial-availability flags

## Modes

- **Watchlist** (default, multi-ticker): one dated calendar with per-ticker sections, sorted by date.
- **Single ticker deep-dive**: full two-gate timeline per vaccine + procurement state.
- **ACIP gate**: approval-to-recommendation transition tracking across names.

## Tool Fallbacks

| Failure | Fallback |
|---------|----------|
| search_acip_events empty | `search_documents` keyword ACIP + `search_sec_filings`; annotate coverage_gap |
| No ACIP row for a product | Flag the unmodeled commercial step explicitly; never assume approval = launch |
| Procurement data missing | State purchase-contract data unavailable; do not estimate values |
| Knowledge tools empty | Proceed with structured data only; annotate knowledge coverage_gap |

## Output File

`{ticker}/{YYYY-MM-DD_HHMM}_fda-catalyst-vaccines_{affix}.md` (watchlist: `watchlist/{YYYY-MM-DD_HHMM}_fda-catalyst-vaccines-calendar_{affix}.md`)

## Output Structure

1. **Executive Summary** — highest-impact vaccine catalysts in the window, 2-3 sentences
2. **Two-Gate Calendar** — dated table: date, ticker, product, FDA event, ACIP row, holiday-week flag, availability framing
3. **Per-Event Analysis** — vote context (recommendation category, committee read) + decision history
4. **Procurement & Lot Release** — contracts, stockpile status, campaign timing
5. **Historical Analogues** — matched vaccine cases with /v/ citations and quantified outcomes
6. **Risk Assessment & Coverage Gaps** — binary-risk sizing, two-gate failure modes, missing data

## Error Handling

| Error | Fallback |
|-------|----------|
| No ACIP or PDUFA rows | Fall back to earnings + pipeline events; annotate `coverage_gap` — never fabricate dates |
| Approval without ACIP row | Present the gap as the central risk; do not imply commercial availability |
| Ticker not in med universe | Resolve via CIK/vaccine-universe match; surface the classification gap |

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
