# Market-Share Tracking — Knowledge Frameworks

Static grounding for `market-share-tracking` (spec 055). Runtime records (approved med strategies/cases) are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the commercial-tracking methodology the skill's arithmetic rests on. All content is an original paraphrase of publicly taught tracking practice.

## The Three-Window Lattice

- Every share and growth figure is reported in three windows: current week / rolling 4-week / rolling 12-week. A single window alone is never a verdict — windows separate noise from trend.
- Every delta displays the previous value next to the new value. A change without its prior reading is unauditable.
- Holiday weeks (New Year, Memorial Day, Good Friday) distort script counts; rows falling on them carry an explicit holiday label instead of being treated as clean reads.

## Launch-Board Arithmetic

- The consensus-implied trajectory is a chain: consensus sales ÷ net price per script ÷ script duration → required TRx → linear weekly path from launch. The actual curve is overlaid on that path; the gap, not the level, is the story.
- Every input (consensus sales, net price assumption, script duration) is stated with its source or assumption label. If any input is missing, the step degrades to a `coverage_gap` listing the required inputs — the arithmetic is never run on invented numbers.
- The board also overlays ≥2 named same-class analog curves (prior launches in the same class/channel), each with its own launch date so curves align at week zero, not calendar date.

## Analog Selection

- Analogs match on class and channel (oral vs injectable, specialist vs primary care) before size or company. A mismatched-channel analog misleads more than it informs.
- Where disclosed, analog curves come from company-reported sales/scripts; where unavailable, the analog is named with its series labeled as unavailable rather than replaced with a fabricated curve.

## LOE / Biosimilar Erosion Series

- Erosion is two series side by side: branded YoY decay (weekly/4-wk/12-wk) and entrant share accumulation, with the entrant's approval date and launch date marked on the timeline.
- Biosimilar erosion speed varies by interchangeability designation and payer tiering; the series must state which regime applies, never a generic "cliff" assumption.

## GTN / Net-Price Stress

- GTN is bracketed (e.g., flex from 50% to 80% of list) rather than pointed; the bracket spans channel-mix outcomes (Medicaid/340B/contracts).
- $/Rx is derived as quarterly reported sales ÷ script volume, labeled `[DEDUCTED]`.
- A net price approximated as half of sales-minus-volume growth is a stated judgment `[VIEW]`, always attributed as an approximation, never a fact.

## Derived-Share Rule

- Share derived from company-reported franchise sales across ≥2 named competitors is the licensed-panel fallback and is always labeled `[DEDUCTED]`. When fewer than two comparable series exist, no share number is produced — `coverage_gap` instead.

## Per-Row Caveat Register

A number without a caveat annotation is a defect. The register covers:

- **Restricted scripts** — panel restrictions stated verbatim; no share number is offered while the restriction applies.
- **Rounding-to-hundreds** — low-volume series move in coarse steps; small changes may be rounding, not signal.
- **Indication-mixed series** — scripts that span indications cannot be attributed to one label without a stated assumption.
- **IV invisibility** — infused products are invisible to Rx panels; tracking falls back to revenue/units.
- **Holiday weeks** — labeled, never smoothed away.

## Modality Vocabularies

- **Drugs & biologics**: TRx/NRx, share, erosion, $/Rx, GTN.
- **Devices**: installed base, placements/procedures per quarter, utilization, ASP trajectory with label-expansion annotations — a device is never expressed in script terms.
- **Vaccines**: doses/serials administered, procurement contract value, ACIP-cohort uptake — FDA approval is never equated with commercial availability.

## Consensus Approximation

- Consensus is company-level only (`search_earnings_calendar`). Product-level consensus is approximated as segment share × company consensus, labeled `[DEDUCTED]`; without a segment split, the product cell is a `coverage_gap`.

## Data Tiers (free-first)

1. Pipeline track (`search_commercial_track`).
2. Company-reported product sales (10-K/Q XBRL + MD&A).
3. Transcript commentary on scripts/share/persistence.
4. Payer coverage/PA announcements; openFDA label events.
5. Licensed Rx panels — documented future enrichment, never assumed present.

## Authoring-time citations

Med strategies/cases extracted in spec 052 are linked below as they reach `approved` status (enriched per FR-005):
<!-- /v/knowledge/{citation_id} citations appended by the spec-052 enrichment step -->
