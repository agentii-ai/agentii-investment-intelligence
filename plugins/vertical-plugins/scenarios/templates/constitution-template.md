---
# The constitution's writer. `agentii.constitution amend` is the owner's deliberate
# rewrite — it is the only writer this file declares, and any other writer's write is
# refused as a second writer (Q127). The same rule governs the thesis instruments;
# see contracts/thesis.md for the reasoning.
writer: agentii.constitution
---

<!--
Sync Impact Report (spec 046 Q33 — executable input, not decoration):
  version: [OLD_VERSION] → [NEW_VERSION]
  amended: [LIST OF PRINCIPLES CHANGED]
  added: [LIST]
  removed: [LIST]
  deferred: [DELIBERATELY POSTPONED TODO]
  Re-examination scope: only pillars depending on the amended principles need review.
-->

# Investment Constitution — [WORKSPACE_NAME]

**CONSTITUTION_VERSION**: 0.1.0-unratified
**RATIFICATION_DATE**: [YYYY-MM-DD]
**LAST_AMENDED_DATE**: [YYYY-MM-DD]

> `constitution_pin: unratified` is legal until ratification (spec 046 Q83). Thesis
> creation is refused while unratified; aggregate constitution checks and staged
> orders hard-fail on placeholder values. Ratify by replacing every `[ALL_CAPS]`
> placeholder with real values and bumping to a real SemVer.

## Macro Regime (updated monthly)

- **Regime**: [EXPANSION_OR_CONTRACTION_OR_STAGFLATION_OR_RECOVERY]
- **Portfolio Bias**: [NET_LONG_OR_NET_SHORT_OR_NEUTRAL]
- **Key Leading Indicators**: ISM [VALUE], Yield Curve [SHAPE], Credit Spreads [LEVEL]

## Sector Preferences

| Sector | Bias | Conviction | Rationale |
|--------|------|:---:|------|
| [SECTOR] | [OVERWEIGHT_OR_UNDERWEIGHT] | [HIGH_MEDIUM_LOW] | [RATIONALE] |

## Research Scope Constraints

- **Market Cap**: [MIN]–[MAX]
- **Regions**: [REGIONS]
- **Sectors Out of Scope**: [SECTORS]
- **Max Concurrent Positions**: [COUNT]

## Risk Framework

- **Single Position**: [DEFAULT_PCT] default, [BINARY_PCT] binary catalyst, [MAX_PCT] max
- **Sector Concentration**: ≤ [PCT] any single sector
- **Macro-Driven Exposure**: ≤ [PCT] total
- **Stop-Loss**: [PCT] thesis-driven; [PCT] technical invalidation

## Methodology Foundation

- **Equity Research**: [WORKFLOW]
- **Valuation**: [PRIMARY_METHOD]
- **Catalyst Requirement**: Dateable catalyst within [DAYS] days for any trade idea

---

*SemVer rules (Q33): MAJOR = a principle removed or incompatibly redefined; MINOR =
a principle added or substantially extended; PATCH = wording only. MAJOR/MINOR bumps
mark `constitution_pin`-older theses `stale` and dispatch re-examination after the
gate-5 budget confirm. PATCH never triggers review.*
