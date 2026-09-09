# Research Plan: [Thesis Name]

> Ordering rule (Q35/Q36): **fundamentals first, trade ideas last** — the plan
> must start with business understanding and end with dateable catalysts + sizing.

## Constitution Check (first evaluation — Q35)

| Constraint | Status | Evidence |
|---|---|---|
| scalar constraints (position/stop-loss) | PASS/FAIL | … |
| research scope (market cap / regions / excluded sectors) | PASS/FAIL | … |

## Phases

| Phase | Content | Skills (ticker × skill × mode) | Depends on |
|:---:|------|------|---|
| 1 — Foundation | business-model, competitive | … | constitution loaded |
| 2 — Financial Deep Dive | recent-quarter, valuation-methods | … | Phase 1 |
| 3 — Modeling | dcf, comps | … | Phase 2 |
| 4 — Synthesis | cross-stock synthesis + snapshot | … | Phases 1–3 |
| 5 — Trade Ideas | dateable catalysts + sizing per constitution.yaml | … | Phase 4 |

## Side artifacts (Q36 — produced by `agentii.plan`)

- `brief.md` — stage-0 context brief (Q18 retrieval keys: mechanical prefilter → pillar FTS → cold-start fallback; strategies top-N 3–5; `<ref:*>` framed blocks; `corpus_version` pin)
- `entities.md` — entity_claims schema + entity/metric map (**REQUIRED** for `market_data_stage: early` theses — Q42 bars schema)
- `reproduce.md` — skills + five pins + `as_of` (the one file an external reviewer needs)
- `contracts/` — output frontmatter schemas + `requires:` declarations

## Constitution Check (second evaluation — after sizing, Q35)

| Constraint | Status | Evidence |
|---|---|---|
| aggregate constraints (sector concentration / macro exposure) | PASS/FAIL | … |

## Deviation Register *(only when a violation is accepted — Q35)*

| Constraint | Why Accepted | Safer Alternative Rejected Because | Approver | Expiry |
|---|---|---|---|---|
| … | … | … | … | YYYY-MM-DD |

> No-defended-violation = plan not complete (`agentii.plan` must not report success).
