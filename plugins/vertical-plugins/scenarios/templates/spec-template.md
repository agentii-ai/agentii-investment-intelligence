# Research Thesis: [Thesis Name]

**Constitution Ref**: workspace/constitution.md
**Created**: [YYYY-MM-DD]
**Status**: Active | Completed | Archived
**Time Horizon**: [e.g. "Q3 2026 quarterly review"]

## 1. Research Question
[One sentence: what specific investment question is this thesis answering?]

## 1b. Pillars *(mandatory — Q30: pillar = user story; P1 = Minimum Defensible View)*

<!-- Each pillar MUST be independently FALSIFIABLE. wrong_if is the acceptance
     criterion and MUST be mechanically checkable (metric + threshold + source)
     per Q8 contract 4 — never prose. -->

### Pillar 1 — [Brief Title] (Priority: P1) 🎯 Minimum Defensible View
[What this pillar claims]
**Why this priority**: [why it bears the most weight]
**Independently falsifiable**: [how to falsify this pillar alone]
**wrong_if**: `metric=<…> threshold=<…> source=<…> [op=<</>/<=/>=/==>]`
**Subscribed**: `NVDA × business-model`, `NVDA × competitive`, …

### Pillar 2 — [Brief Title] (Priority: P2)
…

> Delivering P1 alone MUST yield a defensible partial conclusion. Research is
> frequently halted when budget runs out; pillar-ordering guarantees the halt
> point is a deliverable point.

## 2. Universe Definition
| Ticker | Company | Sector | Weight in Thesis | Rationale for Inclusion |
|--------|---------|--------|:---:|------|

## 3. Skill Deployment Matrix
| Skill | Vertical | Depth | Tickers | Market Data Stage (Q41) | Purpose |
|-------|----------|:---:|--------|:---:|------|

## 4. Depth Tiers
<!-- Q79: a tier selects (skill, mode-set) PAIRS. Light's mode-set IS the skill's
     own essentials_modes (single source of truth per Q12). -->
| Tier | Skills | mode-set | Tickers | Output |
|:---:|------|---|--------|------|

## 5. Cross-Cutting Analysis
- Sector Thesis / Pair Trade Opportunities / Macro Sensitivity

## 6. Output Contract
- Per-Ticker: `{ticker}/YYYY-MM-DD_HHMM_{skill}_{affix}.md`
- Cross-Stock: `_cross/{sector}_synthesis.md`
- Snapshot: `snapshots/{ticker}/{YYYY-MM-DD}_{semantic-slug}.md` — keyed by **ticker**, not thesis id (Q144), because a ticker always exists and a thesis id does not; the thesis attribution lives in the snapshot's frontmatter. The filename's slug names what the snapshot is *about* (`thesis`, `guidance-cut`, `margin-bridge`); `_thesis` is a degenerate slug, not a different convention.

## Clarifications *(filled by agentii.clarify — append-only)*

- [YYYY-MM-DD] Q: … → A: …

## 7. Thesis Phases
| Phase | Tasks | Duration | Dependencies |
|:---:|------|:---:|------|
| 1 — Foundation | … | Week 1 | Constitution loaded |
| … | … | … | … |
| N — Trade Ideas | Dateable catalysts + sizing per constitution.yaml | — | Prior phases complete |

**frontmatter** (thesis.md, machine-read):
```yaml
claim: …
pillars: [{id, priority, wrong_if: [{metric, threshold, source, op?}], subscriptions: []}]
budget: {max_tasks, max_retries_per_task}
expiry_triggers: [earnings_release, fda_decision, constitution_bump, skill_version_mix]
depends_on: [{thesis_id, claims: []}]
macro_sensitivity: high | medium | low
```
