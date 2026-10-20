# FDA Catalyst Devices — Knowledge Frameworks

Static grounding for `fda-catalyst-devices` (spec 055). Runtime records are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the device pathway ladder, failure modes, and the pattern disciplines. Shared regulatory scaffolding (scrutiny axes, binary-event sizing) lives in `../../fda-catalyst-analysis/references/knowledge-frameworks.md`.

## Device Pathway Ladder

1. **Submission**: 510(k) (substantial equivalence to a predicate), PMA (de novo evidence of safety and effectiveness for high-risk), or De Novo (novel classification for low-to-moderate risk).
2. **Decision**: clearance (510(k)), approval (PMA), or classification grant (De Novo) — a binary event, but the evidence bar differs sharply by track.
3. **Reimbursement gate**: CMS coverage determination (NCD/LCD) and NTAP add-on payments — approval without coverage is a hollow catalyst.
4. **Launch / installed base**: placements, procedures, utilization ramps; ASP carries label-expansion annotations.
5. **Post-market**: surveillance studies, MDR reporting, recalls — an ongoing catalyst stream, mostly negative when it fires.

## Coverage and Recall Ladders

- **Coverage**: approval → coding → coverage determination → NTAP window → payment rate. Each step is a dated, tradeable milestone.
- **Recall classes**: Class I (serious harm/death risk), II, III — plus watch-list actions that precede recalls. Recalls compound: one class I often triggers guidance cuts and competitor share shifts.

## Failure Modes

- **Equating 510(k) clearance with PMA approval**: the evidence bar differs; sizing a 510(k) like a PMA decision overstates the move.
- **Ignoring the reimbursement gate**: the commercial catalyst is coverage, not clearance.
- **Missing recall signals**: watch actions and MDR trends precede formal recalls — a screen that skips them misses the negative side.
- **Treating approval as adoption**: installed-base ramp is the real revenue catalyst; utilization data settles whether the launch is tracking.
- **Unlabeled holiday weeks**: procedure volumes across holiday-shifted weeks read as trend when they are seasonality.

## Methodology Patterns (original paraphrase of publicly taught practice)

### Device vocabulary (P1, cross-cutting)

Installed base / placements / procedures / utilization / ASP ($/unit with label-expansion annotations). For launch tracking: consensus sales ÷ ASP ÷ procedure ramp → required procedure volume → linear path vs actuals, overlaid with at least two named same-category adoption curves.

### Event-takeaway anatomy (P4)

Headline verdict → per-stock takeaways with model numbers → KOL distillation → data lattices → modeled deltas vs consensus → what's-changed vectors (estimates / thesis / positioning) → risk bullets. Conflicting views surfaced and rated by materiality, never averaged.

### POS / scenario discipline (cross-cutting)

Unadjusted peak x POS = modeled number; both terms shown; POS changes logged with reasons. Bull/base/bear with named-driver grids; explicit abstention where unquantifiable. Reimbursement is a probability input, not an assumption: an uncovered device gets a discounted POS.

## Structured Data Surfaces

- `get_device_decision` — device_decision_event rows (track, status, date).
- `search_universe_devices` / `get_company_devices` — device identity and owner joins.
- Recall, coverage, and NTAP context is document-sourced; annotate when unavailable.

## Cross-Cutting Habits

- **Buy-side lens**: track where investor attention sits; the client-question pattern — answer the most common question directly (e.g. "does the coverage decision matter more than the clearance?"); per-name bull/bear pivot conditions.
- **Living-thesis loop**: estimates move first, ratings last; append exhibits to the prior note, never rewrite; holiday labels persist.
- **Badge mapping (FR-092)**: verifiable facts `[FACT]`, derived arithmetic `[DEDUCTED]`, judgments `[VIEW]` — with a Category/Count/% summary table.

## Authoring-time citations

Spec 055 med strategies and cases are linked here as they reach `approved` status; at runtime retrieve via `search_investment_cases` / `search_by_analogue` and cite with /v/ URLs.
