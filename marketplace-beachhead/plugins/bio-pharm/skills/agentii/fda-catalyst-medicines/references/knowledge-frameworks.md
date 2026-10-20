# FDA Catalyst Medicines — Knowledge Frameworks

Static grounding for `fda-catalyst-medicines` (spec 055). Runtime records (approved med strategies and cases) are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the CDER pathway ladder, failure modes, and the pattern disciplines those records rest on. Shared regulatory scaffolding (FDA/EMA process, AdCom mechanics, the six scrutiny axes, catalyst sizing) lives in the fda-catalyst-analysis skill's reference: `../../fda-catalyst-analysis/references/knowledge-frameworks.md`.

## CDER Pathway Ladder

1. **Filing**: NDA (small molecules) or BLA (biologics) submitted; review track assigned — standard (~10 months) or priority (~6 months), with breakthrough designation enabling rolling review.
2. **Review + AdCom**: FDA reviewer analyses, sponsor briefings, advisory committee vote where the approval is ambiguous. The vote is advisory but moves the stock before the date.
3. **PDUFA target date**: the negotiated decision date — the anchor of any medicines catalyst calendar.
4. **Decision**: approval, Complete Response Letter (CRL — deficiencies listed; the sponsor's remediation resets the clock), or withdrawal.
5. **Label expansion**: sNDA/sBLA filings extend indications, populations, and formulations — the recurring catalyst stream after first approval.
6. **Loss of exclusivity (LOE)**: Orange Book patents and exclusivities (NCE, NCI, ODE, PTE) expire; generic or biosimilar entry follows the earliest expiry.

## Biosimilar Timeline Note

- Interchangeability is a designation, not an approval: a biosimilar can be approved but not interchangeable.
- The first interchangeable biosimilar earns 180-day exclusivity against other interchangeables — a genuine entry-window moat.
- Approval date is not launch date: launch sequencing follows patent-settlement terms, at-risk launches, and exclusivity expiry — size the launch catalyst, not the approval one.

## Failure Modes

- **Fabricated dates**: filling an empty tool response with an assumed PDUFA date — always annotate `coverage_gap` instead.
- **Treating an AdCom vote as the decision**: the vote is advisory; the decision lands on the PDUFA date.
- **Ignoring superseded dates**: a supersede chain is information — a pushed date re-times the whole calendar.
- **Ignoring exclusivity state**: a launch catalyst sized without Orange Book state misses the entry-window question.
- **Unlabeled holiday weeks**: week-over-week comparisons across holiday-shifted weeks read as signal when they are noise.
- **CRL remediation treated as free**: every remediation resets the target date and delays the cash-flow start.

## Methodology Patterns (original paraphrase of publicly taught practice)

### P4 event-takeaway anatomy (post-decision notes)

Headline verdict first → per-stock takeaways with model numbers → KOL distillation → raw data and cross-trial comparison lattices → modeled deltas vs consensus (peak x POS) → three what's-changed vectors (estimates / thesis / positioning) → upside/downside bullets. Conflicting KOL views are surfaced verbatim and rated by materiality — never silently averaged.

### P1 launch board (commercial context for post-approval catalysts)

Actual prescription share overlaid with at least two named same-class launch curves and a consensus-implied trajectory: consensus sales ÷ net price per script ÷ script duration → required weekly scripts → linear path vs actuals. LOE erosion: entrant share series and branded year-over-year decay side by side, approval and launch dates on the timeline.

### POS / scenario discipline (cross-cutting)

Unadjusted peak x probability of success = the modeled number; both terms shown. Every POS change is logged with its reason. Bull/base/bear always carries a named-driver assumption grid — never a single point number. Explicit abstention ("no view on likelihood") where unquantifiable.

## Structured Data Surfaces

- `get_upcoming_pdufa` / `get_pdufa_decision` — pipeline.fda_calendar_event rows (horizon_days default 180).
- `search_adcom_meetings` / `get_adcom_meeting` — committee/product/ticker/date/vote filters; briefing-doc inventory per meeting.
- `search_fda_approvals` / `get_fda_approval` — approval history with label and designation state.

## Cross-Cutting Habits

- **Buy-side lens**: track where investor attention sits; frame per-name bull/bear pivot conditions; the client-question pattern — surface the question most often asked about the event (e.g. "does the AdCom vote pre-empt the PDUFA?") and answer it directly.
- **Living-thesis loop**: estimates move first, ratings last; append new exhibits to the prior note, never rewrite; holiday labels persist across updates.
- **Badge mapping (FR-092)**: every output line carries a badge — verifiable facts `[FACT]`, arithmetic derived from facts `[DEDUCTED]`, judgments and interpretations `[VIEW]` — summarized in a Category/Count/% table.

## Authoring-time citations

Spec 055 med strategies and cases are linked here as they reach `approved` status; at runtime retrieve via `search_investment_strategies(sectors=med)` / `search_investment_cases` and cite with /v/ URLs.
