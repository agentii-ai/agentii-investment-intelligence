# us2_catalyst_medicines — NDA/BLA catalyst calendar (fda-catalyst-medicines)

## Prompt

Build the next-4-quarter FDA catalyst calendar for LLY: enumerate PDUFA dates, AdCom meetings and sNDA/sBLA label-expansion decisions from the catalyst surface, flag any biosimilar interchangeability or 180-day exclusivity exposure, and label holiday weeks explicitly.

## Rubric Checks

- [ ] Every dated event has a source tool call or a coverage_gap annotation
- [ ] Biosimilar/180-day exclusivity states named where applicable
- [ ] Holiday weeks labeled, never silently included
- [ ] No fabricated date, vote, or outcome
- [ ] Badge summary table present
