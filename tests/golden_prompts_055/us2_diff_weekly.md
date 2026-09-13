# us2_diff_weekly — US2: weekly trial status diff correctness + vaccine approval-is-not-ACIP gate

## Prompt

Run the weekly clinicaltrials.gov status diff for my coverage universe using the two most recent snapshots. Categorize each changed row per the 11-category taxonomy and show previous and new values side by side. Then, for the vaccine names in coverage, produce the catalyst view that keeps the FDA approval date and the ACIP recommendation date separate — approval is never presented as commercial availability.

## Rubric Checks

- [ ] Diff returns exactly the rows that changed between the two snapshots; a no-change week yields an empty, byte-stable output with no phantom rows (US2 acceptance 3, FR-D03).
- [ ] Every changed row shows previous primary-completion date, previous status, and previous enrollment next to the new values (US2 independent test).
- [ ] Terminated and Downsized rows are flagged as risk signals with the enrollment delta (e.g., enrollment 92 to 10); Ahead/Delayed rows are flagged as re-timing alerts (US2 acceptance 1-2, FR-B03).
- [ ] Missing weeks between snapshots: the gap window is stated and no change is attributed across it (spec edge case, FR-D03).
- [ ] Vaccines: FDA approval date and ACIP recommendation date appear as separate events, and approval is never labeled commercially available before the ACIP recommendation (FR-D05, SC-010).
