# Output File YAML Frontmatter Schema (FR-090)

Every skill output file (FR-079) MUST include a YAML frontmatter block at the top of the markdown file with machine-parseable metadata. This enables cross-analysis memory discovery without loading full files.

## Required Frontmatter Block

```yaml
---
ticker: LLY                              # uppercase ticker (or tickers: [LLY, NVO, PFE] for multi-ticker per FR-093)
date: 2026-06-03                          # ISO 8601 date
skill: recent-quarter                     # matches skill frontmatter `name` field
affix: consolidated-p-and-l              # short descriptive slug
key_metrics:                             # dict of most important computed values
  revenue: "$18.5B"
  eps: "$2.34"
  gross_margin: "80.0%"
  qoq_revenue_growth: "+12%"
conclusions: >-                          # 1-3 sentence synthesis
  Q1 2026 revenue $18.5B (+12% QoQ), EPS $2.34 beat consensus by 4%.
  Gross margin expanded 200bps to 80%. Mounjaro supply constraints easing.
facts_count: 12                          # number of [FACT] claims per FR-092
deducted_count: 8                        # number of [DEDUCTED] claims
views_count: 3                           # number of [VIEW] claims
citation_count: 23                       # total inline citations
---
```

## Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `ticker` | Conditional | string | Single ticker. Exactly one of `ticker` or `tickers` MUST be present. |
| `tickers` | Conditional | string[] | Multi-ticker array per FR-093. Used by `_cross/` and `_sector/` outputs. |
| `date` | Yes | ISO 8601 | Date of analysis |
| `skill` | Yes | string | Skill name matching `name` field in SKILL.md frontmatter |
| `affix` | Yes | string | Descriptive slug capturing analysis focus |
| `key_metrics` | Yes | dict | Most important computed values as human-readable strings |
| `conclusions` | Yes | string | 1-3 sentence synthesis of key findings |
| `facts_count` | Yes | int | Count of `[FACT]` claims per FR-092 |
| `deducted_count` | Yes | int | Count of `[DEDUCTED]` claims |
| `views_count` | Yes | int | Count of `[VIEW]` claims |
| `citation_count` | Yes | int | Total inline citation references |

## Validation Rules

1. Exactly one of `ticker` (singular) or `tickers` (plural) MUST be present — never both.
2. `key_metrics` values MUST be human-readable strings with units ($, %, bps, x).
3. `facts_count + deducted_count + views_count` MUST equal the total number of classified claims in the file.
4. `citation_count` MUST be ≥1 per 200 words of body text (FR-079 citation density).

## Glob-Based Discovery Protocol

The agent's pre-flight (FR-075) MUST execute the following discovery sequence BEFORE any data retrieval:

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
