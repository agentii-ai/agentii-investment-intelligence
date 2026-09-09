---
name: plan
description: "Author the research plan — fundamentals first, trade ideas last; Constitution Check evaluated twice; Deviation Register with mandatory Expiry; emits the four side artifacts (brief/entities/reproduce/contracts). Technical (market_data_stage: early) theses MUST emit the entities.md bars schema before implement (Q42)."
role: kit
market_data_stage: none
---

# agentii.plan

## Ordering rule (Q35/Q36)

The plan starts with business understanding and ends with dateable catalysts +
sizing. Constitution Check runs **twice**: plan start (scalar + scope) and after
sizing (aggregate — `position_pct` exists only then).

## Side artifacts

| artifact | content | hard requirement |
|---|---|---|
| `brief.md` | stage-0 context brief — Q18 retrieval keys (mechanical prefilter → pillar FTS → cold-start fallback); strategies top-N 3–5 with a `method_selection:` verdict each (Q7); `<ref:*>` framed blocks; `corpus_version` pin | — |
| `entities.md` | entity_claims schema + entity/metric map | **`market_data_stage: early` theses MUST define the bars schema (Q42) — without it, implement refuses** |
| `reproduce.md` | skills + five pins + `as_of` | — |
| `contracts/` | output frontmatter schemas + `requires:` declarations | — |

## Deviation Register (Q35)

An accepted violation without `Constraint | Why Accepted | Safer Alternative
Rejected Because | Approver | Expiry` means the plan is **not complete** —
`agentii.plan` must not report success. Every deviation carries an Expiry;
converge re-proposes re-justification at expiry.

## Invocation

```bash
python3 scripts/agentii_cmd.py plan --thesis theses/001-ai-semiconductors
```

Gate 2 (after plan, informational) shows phases + the Deviation Register.
