# Thesis: [Thesis Name] — the living file

> **Single-writer living file (Q5/Q15)**: the ONLY writer is the reduction step
> (scripts/reduce_journals.py), one atomic write per cycle. Everything else —
> freshness, completion, run identity — is derived from artifacts, never stored here.

```yaml
# thesis.md frontmatter (machine-read)
claim: [one-sentence claim]
pillars:
  - id: [PIL-1]
    priority: P1
    wrong_if:
      - {metric: …, threshold: …, source: …, op: "<"}
    subscriptions: ["NVDA × business-model", …]
conviction: 0.62          # derived from evidence, never hand-set
known-open: []
depends_on: []
macro_sensitivity: medium
expiry_triggers: [earnings_release, fda_decision]
budget: {max_tasks: 80, max_retries_per_task: 2}
assumption_pin: 1
corpus_version: "2026-08"
as_of: YYYY-MM-DD
constitution_pin: 0.1.0
skill_pin: {recent-quarter: abc123}
```

## Claim History *(conviction is a function of evidence — Q8)*

| version | date | conviction | trigger |
|---|---|:---:|---|

## Wrong If *(machine-checkable — Q8 contract 4)*

| pillar | metric | threshold | source | op |
|---|---|---:|---|---|

## Known Open

- (unresolved items; converge re-proposes them next cycle — Q14)
