# us5_mechanism_map — US5: mechanism competitor map via drug-knowledge reverse lookups + provenance conflict case

## Prompt

Map the mechanism and indication competitors for a marketed drug in the spec-054 silver layer (e.g., a GLP-1 or PCSK9 drug). Use the drug-knowledge tools end to end: forward lookup by drug name for mechanism/targets/indications/clinical phase, then reverse lookups by target and by indication to build the competitor map with tickers. Include a conflict case: where two sources disagree on a drug's mechanism annotation, show both values with their provenance.

## Rubric Checks

- [ ] Forward lookup by drug name returns mechanism, targets, indications, and clinical phase, each with source attribution (US5 acceptance 1).
- [ ] Reverse lookup by target returns all drugs mapped to that target (US5 acceptance 2).
- [ ] Reverse lookup by indication returns all drugs mapped to that indication (US5 independent test).
- [ ] Conflict case: both mechanism values are returned with provenance — never silently merged (US5 acceptance 3).
- [ ] Competitor map ties each competitor drug to its ticker, so downstream peer-bench mechanism-overlap scoring can consume it (US5 purpose).
- [ ] Zero fabrication: an unknown drug_key yields an explicit not-found, never a guessed record; every row traces to a tool result.
