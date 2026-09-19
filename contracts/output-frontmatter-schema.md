# Output File YAML Frontmatter Schema

Every skill output file MUST include a YAML frontmatter block at the top of the markdown file with machine-parseable metadata. This enables cross-analysis memory discovery without loading full files.

## Required Frontmatter Block

```yaml
---
ticker: LLY # uppercase ticker (or tickers: [LLY, NVO, PFE] for multi-ticker per FR-106)
as_of: 2026-06-03 # ISO 8601. T168: this is the date the analysis is AS OF; `date` is retired
skill: recent-quarter # matches skill frontmatter `name` field
affix: consolidated-p-and-l # short descriptive slug
key_metrics: # dict of most important computed values
 revenue: "$18.5B"
 eps: "$2.34"
 gross_margin: "80.0%"
 qoq_revenue_growth: "+12%"
conclusions: >- # 1-3 sentence synthesis
 Q1 2026 revenue $18.5B (+12% QoQ), EPS $2.34 beat consensus by 4%.
 Gross margin expanded 200bps to 80%. Mounjaro supply constraints easing.
claims: # T196 (Q146): EVERY material claim, each with its own class.
 - {claim_class: FACT,     text: "Q1 2026 revenue $18.5B", citation: "LLY 10-Q p.4"}
 - {claim_class: DEDUCTED, text: "+12% QoQ revenue growth", citation: "prior-quarter revenue"}
 - {claim_class: VIEW,     text: "Mounjaro supply constraints are easing"}
mechanism_outcome: EXECUTED # Q129/Q135: EXECUTED | VACUOUS — an un-run gate must say so
facts_count: 1 # DERIVED — counted from `claims`, not authored (Check 45 recomputes)
deducted_count: 1 # DERIVED
views_count: 1 # DERIVED
citation_count: 23 # total inline citations
---
```

> **The counts are DERIVED, so this example's numbers are consistent with its `claims`
> list on purpose.** Three numbers that must agree by construction are three numbers
> that can disagree silently — and did: the pre-T196 example carried
> `facts_count: 12 / deducted_count: 8 / views_count: 3` with no list behind them,
> so nothing in the file could have contradicted them.

## Fields — LAYERED (T167/T168/T169, Q145/Q146)

**This table is one layer, not the whole shape.** Q145 measured that this contract
and the thesis-mode `artifact-frontmatter.schema.json` shared **zero** fields — so
an artifact written in one mode was unreadable in the other, and a gate declared
`both` had an input that existed in one mode only. The fix is a **public core**
required in both modes, plus a mode-specific extension.

### Layer 1 — public core (required in BOTH modes)

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `ticker` | Conditional | string | Single ticker. Exactly one of `ticker` or `tickers` MUST be present. |
| `tickers` | Conditional | string[] | Multi-ticker array. Used by `_cross/` and `_sector/` outputs. |
| `as_of` | **Yes** | ISO 8601 | **The date this analysis is as of.** Renamed from `date` by **T168** |
| `skill` | Yes | string | Skill name matching the `name` field in SKILL.md frontmatter |
| `affix` | Yes | string | Descriptive slug capturing analysis focus |
| `key_metrics` | Yes | dict | Most important computed values as human-readable strings |
| `conclusions` | Yes | string | 1-3 sentence synthesis of key findings |
| `claims` | **Yes** | object[] | **Every material claim, each carrying its own `claim_class ∈ {FACT, DEDUCTED, VIEW}`** — T196 corrects T169, which put the class on the ARTIFACT |
| `mechanism_outcome` | **Yes** | enum | **`EXECUTED` \| `VACUOUS`** — Q129/Q135. In the CORE because Q142 classifies `VACUOUS` reporting as mode-independent: an un-run gate must say it did not run, whether or not a thesis exists |

> **T168 — the `date` / `as_of` collision, resolved to ONE name.** The two mode
> contracts named the same fact differently: this one said `date`, the thesis one
> said `as_of`. **`as_of` wins, and not by preference** — it is what the machinery
> reads. It is one of FR-090's `FIVE_PINS` (`g1_gate.FIVE_PINS`), and it is read by
> `g1_gate`, `dispatch.reuse_verdict`, `converge` and `synthesize_report`. **`date`
> was read by nothing.** Renaming to the name that four components already depend
> on is the change with no migration; the reverse would have been a rename in four
> places to satisfy one table.

> **T169 — `claim_class` as a FIELD, because of what a G1 gate IS.** Q146: a G1
> gate is defined as *deterministic, pure-script, millisecond, zero-LLM*. Making it
> parse prose to count `[FACT]` claims **injects non-determinism into the gate whose
> entire purpose is determinism**. So the class is a field, the inline
> `[FACT]`/`[DEDUCTED]`/`[VIEW]` badges become **rendering generated from it**, and
> `facts_count` / `deducted_count` / `views_count` become **derived** rather than
> independently maintained. Three fields that must agree by construction is three
> fields that can disagree silently.

> **T196 — T169 put the field at the wrong altitude, and the error defeated its own
> purpose.** T169 made `claim_class` a scalar on the ARTIFACT: one element of
> `{FACT, DEDUCTED, VIEW}` per file. But Q146 requires the three counts to be
> **derived from the classes**, and **three counts are not derivable from one value**.
> A file reading `claim_class: FACT` can only ever yield `1 / 0 / 0`, whatever it
> actually contains — so the count would be derived in name and authored in fact,
> which is the arrangement T169 was written to end. Worse, it was **satisfiable
> while enforcing nothing**: a file declaring `FACT` and holding twenty `DEDUCTED`
> claims passed the schema, and the anti-fabrication gate read a number nothing
> guaranteed. The class is now a property of each claim (`claims[]`, and
> `entity_claims[]` in thesis mode), and **Check 45** recomputes the counts from the
> list — because "derived" that is not recomputed is a declaration like any other.

### Layer 2 — derived (no longer authored)

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `facts_count` | Derived | int | `claims` whose `claim_class` is `FACT` — **recomputed by Check 45** |
| `deducted_count` | Derived | int | `claims` whose `claim_class` is `DEDUCTED` — **recomputed by Check 45** |
| `views_count` | Derived | int | `claims` whose `claim_class` is `VIEW` — **recomputed by Check 45** |
| `citation_count` | Yes | int | Total inline citation references |

### Layer 3 — thesis-mode extension

Not in this contract. `specs/046-…/contracts/artifact-frontmatter.schema.json`
carries the thesis layer (`assumption_pin`, `corpus_version`, `constitution_pin`,
`skill_pin`, `mode`, `data_class`, `entity_claims`, `writer`, …) — **added to** the
public core, never instead of it.

> **Here stood an orphaned copy of the pre-T167 table** — eight rows (`skill`,
> `affix`, `key_metrics`, `conclusions`, `facts_count`, `deducted_count`,
> `views_count`, `citation_count`) left behind when the layered tables replaced it.
> It re-required the three counts as *authored* (`Yes`), directly contradicting
> Layer 2's *Derived* eight lines above, and it listed `conclusions` as required
> while Layer 1 had by then omitted it. Removed 2026-09-19 (T196): a reader who
> reached it — and it sat **after** the point where the layers end, so reaching it
> means having read the correct tables first — would have taken the stale
> requirement as the operative one.

## Validation Rules

1. Exactly one of `ticker` (singular) or `tickers` (plural) MUST be present — never both.
2. `key_metrics` values MUST be human-readable strings with units ($, %, bps, x).
3. `facts_count + deducted_count + views_count` MUST equal the number of entries in `claims` — and since both sides are now recomputable, a disagreement is a **defect, not a discrepancy to reconcile** (**Check 45**). The counts are outputs of the derivation, not inputs to it.
4. `citation_count` MUST be ≥1 per 200 words of body text (citation density).
5. Every entry in `claims` MUST carry a `claim_class`; an unclassed claim is invisible to the anti-fabrication gate, which is the one outcome Q146 exists to prevent.

## Glob-Based Discovery Protocol

The agent's pre-flight MUST execute the following discovery sequence BEFORE any data retrieval:

1. **Glob for output files**: `ls {ticker}/*.md` for single-ticker; `ls _cross/*{ticker}*.md` for cross-analyses involving this ticker.
2. **Parse frontmatter**: `head -20` each file to extract YAML frontmatter (no need to load full file).
3. **Build memory summary**: aggregate `key_metrics` and `conclusions` from all prior analyses for this ticker.
4. **Inject into context**: include the memory summary in the agent's initial context before tool calls begin.

This achieves the File-First Hybrid Architecture goal (research-memory.md) — machine-parseable metadata without a vector database.

## Cross-Reference

- **FR-079**: Output file naming convention
- **FR-087**: agentii.md memory index
- **FR-091**: Two-tier output model
- **FR-092**: FACT/DEDUCTED/VIEW classification taxonomy
- **FR-093**: Multi-ticker output convention (`_cross/`, `_sector/`)
