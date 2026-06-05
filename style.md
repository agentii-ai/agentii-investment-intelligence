# Agentii Output Formatting Standard (FR-094)

Canonical formatting standards for all agent output files. Skills reference this via `## Output Structure` sections. Per-workspace `style.md` at the project root can override these defaults.

---

## Number Formatting

### Currency
- **Compact notation required**: $18.5B (not $18,500,000,000), $425M, €12.7B, ¥850B
- **Unit suffix**: B (billions), M (millions), K (thousands)
- **Precision**: one decimal place for billions (18.5B), no decimals for millions (425M)
- **Negative values**: parenthesized ($425M) or prefixed -$425M — be consistent within a document
- **Non-USD**: always annotate with ISO 4217 code on first use: "ASML reports in EUR (€)"

### Percentages
- **Format**: 12.4% (one decimal), 80% (no decimal when whole number)
- **Basis points**: 200bps (not 2.0%), use for small changes (<1%)
- **Growth rates**: +12.4% or -3.2% (sign prefix mandatory)
- **Margin changes**: "expanded 200bps" (basis points preferred for YoY changes)

### Shares and Units
- **Shares outstanding**: 1.25B, 850M
- **Per-share values**: $2.34 (two decimals)
- **Multiples**: 14.2x, 22.5x (one decimal)

---

## Table Conventions

### Column Ordering (standard financial table)
```
Metric → Current Period → Prior Period → YoY Change → Citation
```

### Alignment
| Data Type | Alignment | Example |
|-----------|-----------|---------|
| Labels (metric names) | Left | `Revenue` |
| Numbers (values, $) | Right | `$18.5B` |
| Percentages | Right | `+12.4%` |
| Citations | Left | `[📄 LLY 10-Q p.12](...)` |

### Minimum Structure
- At least **3 data columns** before wrapping
- **Header row** bold with border-bottom
- **Total/subtotal rows** bold
- **Alternating row shading** optional but preferred for tables >10 rows

---

## YAML Frontmatter (FR-090)

All output files MUST include the following frontmatter fields:

```yaml
---
ticker: LLY                              # or tickers: [LLY, NVO] for multi-ticker
date: 2026-06-03                          # ISO 8601
skill: recent-quarter                     # skill name
affix: consolidated-p-and-l              # descriptive slug
key_metrics:                             # dict of key computed values
  revenue: "$18.5B"
  eps: "$2.34"
conclusions: >-                          # 1-3 sentence synthesis
  Key findings summary.
facts_count: 12
deducted_count: 8
views_count: 3
citation_count: 23
---
```

Fields marked optional in `contracts/output-frontmatter-schema.md` may be omitted.

---

## Citation Placement (FR-081)

- **Inline after every numeric claim**: "Revenue was $18.5B [📄 LLY 10-Q p.12](https://www.agentii.ai/view?ticker=LLY&citation_id=sec178&page_no=page12), up 12% QoQ."
- **No footnote-only citations**: citations live next to the data they support, not in a separate section.
- **Citation density**: ≥1 citation per 200 words of body text (FR-079).
- **Link format**: `[📄 {ticker} {form_type} p.{N}](https://www.agentii.ai/view?ticker={ticker}&citation_id={id}&page_no=page{N})`

---

## Taxonomy Badges (FR-092)

Every claim in Tier 2 snapshots MUST carry exactly one badge:

| Badge | Color | Meaning | Example |
|-------|-------|---------|---------|
| `**[FACT]**` | Green | Verifiable from SEC filings | "Q1 2026 revenue was $18.5B" |
| `**[DEDUCTED]**` | Blue | Mathematical/logical deduction | "QoQ growth = +12% ($16.5B → $18.5B)" |
| `**[VIEW]**` | Orange | Subjective assessment/opinion | "GLP-1 pipeline undervalued vs $100B TAM" |

### Snapshot Summary Table

Every Tier 2 snapshot MUST include at the top:

```markdown
| Category | Count | % |
|----------|-------|---|
| [FACT] | 12 | 52% |
| [DEDUCTED] | 8 | 35% |
| [VIEW] | 3 | 13% |
| **Total** | **23** | 100% |
```

---

## Per-Workspace Overrides

A user-authored `style.md` at the workspace root can override these defaults:

| Setting | Package Default | Description |
|---------|----------------|-------------|
| `default_lookback_quarters` | Skill-specific | Override temporal scope (e.g., 12 quarters for deep analysis) |
| `reporting_currency` | USD | Preferred reporting currency for non-US companies |
| `sector_focus` | (none) | Limit analysis to specified sectors |
| `output_verbosity` | standard | concise / standard / comprehensive |
| `peer_universe` | (none) | Default peer list for comps analysis |

### Override Precedence
```
workspace style.md > package style.md > skill defaults
```

Skills MUST check for `./style.md` during FR-075 pre-flight and apply overrides.

---

## Cross-Reference

- **FR-079**: Output file convention
- **FR-081**: Citation link format
- **FR-090**: YAML frontmatter schema
- **FR-092**: FACT/DEDUCTED/VIEW taxonomy
- **FR-094**: This standard
