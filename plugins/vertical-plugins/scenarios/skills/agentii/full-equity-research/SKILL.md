---
name: full-equity-research
description: "The Auto 档 scenario — a soft-plan orchestrator for a complete fundamental equity research thesis: understand → financials → valuation → synthesize. The body is a soft plan (stages), not a rigid DAG; correctness is enforced by each referenced skill's own requires: preconditions, never by this plan's rigidity (Q2)."
role: orchestrator
market_data_stage: none
---

# full-equity-research

```yaml
scenario: full-equity-research
stages:
  - skill: business-model
  - skill: competitive
  - skill: recent-quarter
  - skill: valuation-methods
  - skill: dcf
notes: >-
  Foreign issuers use 20-F/6-K instead of 10-K/8-K; small caps may skip dcf.
  Dispatch each stage as its own subagent (context isolation, Q2); handoff
  passes artifact PATHS, never content (Q13 rule 3).
```

Validated by `validate_scenes.py`: registry-key references + acyclicity.
