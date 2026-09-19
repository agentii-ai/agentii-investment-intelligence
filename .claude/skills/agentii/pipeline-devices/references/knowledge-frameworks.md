# Pipeline Devices — Knowledge Frameworks

Static grounding for `pipeline-devices` (spec 055). Runtime records are retrieved via the knowledge tools and cited with /v/ URLs; this file carries the device stage ladder, design-iteration discipline, RWE ladder, post-market obligations, and failure modes. Shared regulatory scaffolding (scrutiny axes) lives in `../../fda-catalyst-analysis/references/knowledge-frameworks.md`.

## Device Stage Ladder (iteration, not phases)

- **Feasibility**: first-in-human, small N, safety and signal — the design is not yet frozen.
- **Pivotal**: registrational study sized to the evidence bar of the expected track: PMA (highest), De Novo (novel classification), 510(k) (equivalence — often no pivotal at all).
- **Submission / decision**: PMA approval, De Novo grant, or 510(k) clearance; the track determines the size of the binary event.
- **Post-market**: surveillance studies, MDR reporting, next-generation design work — the pipeline does not end at approval.

Devices iterate: version freezes, design changes, and equivalence testing between generations are the milestones. A device "pipeline" is a sequence of design cycles, not a fixed phase ladder.

## Design-Iteration Discipline

- Track the current design version per asset and whether it is frozen (a freeze is the submission-readiness signal).
- Design changes mid-pivotal reset evidence: flag any asset that changed design after study start.
- Next-generation programs: the v2 asset cannibalizes the v1 installed base — model them together, not separately.

## RWE Ladder

- **Registries**: longitudinal product-outcome data, often conditionally required post-approval.
- **Claims analyses**: utilization and outcome signals at scale, supporting label expansion and coverage.
- **Post-approval studies**: FDA-required commitments (conditions of approval) with their own timelines.
- RWE is a pipeline asset: it extends labels, supports coverage, and feeds the next design cycle.

## Post-Market Obligations

- PMAs carry conditions of approval and surveillance requirements; missing them risks recall-class escalation.
- MDR trends are early-warning data: a rising adverse-event series precedes formal action.
- Installed-base economics: the obligation set scales with the base — utilization data settles whether the base is healthy.

## POS / Scenario Discipline (cross-cutting)

Unadjusted peak x POS = the modeled number; both terms shown; POS changes logged with reasons. Reimbursement is a probability input: an asset without a plausible coverage path gets a discounted POS. Bull/base/bear with named-driver grids (track outcome, coverage timing, adoption rate); explicit abstention where unquantifiable.

## Commercial Context (P1 launch board, applied forward)

Consensus sales ÷ ASP ÷ procedure ramp → required procedure volume → linear path vs at least two named same-category adoption curves. ASP carries label-expansion annotations: each expansion re-prices the opportunity. Installed base, placements, procedures, and utilization are the forward vocabulary for every pivotal asset.

## Failure Modes

- **Applying drug-phase labels to devices**: feasibility/pivotal stages are iteration points, not fixed phases; a "Phase II device" mislabels the evidence bar.
- **Ignoring the design-freeze signal**: submission readiness is the freeze, not the enrollment count.
- **Sizing without the reimbursement gate**: approval-track value assumed, coverage path absent.
- **Ignoring post-market obligations**: the liability tail is part of pipeline value.
- **v1/v2 double-counting**: next-generation programs modeled independently of the base they cannibalize.

## Structured Data Surfaces

- `get_company_devices` / `search_universe_devices` — device inventory and owner joins.
- `search_clinical_trials` / `get_clinical_trial` — study stage, design type, status, enrollment.
- `get_device_decision` — decision history and upcoming decisions per device.

## Cross-Cutting Habits

- **Buy-side lens**: track where investor attention sits; the client-question pattern — answer the most common question directly (e.g. "has the design frozen, or is another iteration coming?"); per-asset bull/bear pivot conditions.
- **Living-thesis loop**: estimates move first, ratings last; append exhibits to the prior note, never rewrite; design-version history persists across updates.
- **Badge mapping (FR-092)**: verifiable facts `[FACT]`, derived arithmetic `[DEDUCTED]`, judgments `[VIEW]` — with a Category/Count/% summary table.

## Authoring-time citations

Spec 055 med strategies and cases are linked here as they reach `approved` status; at runtime retrieve via `search_knowledge_entries` and cite with /v/ URLs.
