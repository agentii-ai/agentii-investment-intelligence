---
name: synthesize
description: Thesis report synthesis — turn a thesis's markdown artifacts into its letter-size thesis-report.html. Three-step loop — pack (deterministic Python bundle of all sources), author (the LLM writes report/content.html from the pack — narrative, tables and citations are LLM judgment), assemble (deterministic validation, template injection, Q50 pins, Q47 overflow gate). Spec 046 Q46–Q50.
role: kit
market_data_stage: none
allowed_tools: []
retrieval_scope: structured_only
---

# agentii.synthesize

The single-point HTML generation step (spec 046 Q46–Q50): ONE `thesis-report.html`
per thesis, authored from the markdown artifacts. Analysis skills emit markdown
only (Q49); the report is assembled here, at the synthesis step, after the
cross-stock synthesis (`_cross/*_synthesis.md`) exists.

## When to run

- After the synthesis tasks complete (the `_cross/` deliverable is written).
- When `converge` emits an `html_stale` finding (sources or template moved).
- On explicit request, or once at thesis completion (Q50 regeneration triggers).

## The loop (three steps)

```bash
cd agentii-investment-intelligence
# 1. PACK — deterministic bundle of every source, verbatim (no timestamps):
python3 scripts/synthesize_report.py pack --thesis <theses/{nnn}-{slug}>

# 2. AUTHOR — read <thesis>/report-input.md and write <thesis>/report/content.html
#    (the LLM step — the report's actual content is YOUR judgment, see contract).

# 3. ASSEMBLE — validate + inject + gate:
python3 scripts/synthesize_report.py assemble --thesis <thesis-dir> --check-only  # fit loop
python3 scripts/synthesize_report.py assemble --thesis <thesis-dir>               # deliver
```

`assemble --check-only` prints each page's estimated height against the letter
limit and writes nothing — iterate on `content.html` until **font tier 0** passes.
Tiers 1–2 (10pt / 9pt) are a safety net, not a target. If all tiers fail, the
assembler degrades: `thesis-report.md` (the full pack, a real markdown report) +
an HTML draft carrying a red DRAFT banner (Q47 failure semantics).

## content.html contract (the assembler hard-gates every rule)

You author **only the page sequence** — a fragment, never a document:

1. One or more `<section class="page">…</section>` blocks, no nesting. The cover
   is page 1 and is template-owned: **do not author it** — the assembler fills
   title / claim / pins / universe / generated / TOC from the thesis itself.
2. Fragment only — `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`, `<style>`,
   `<script>` are rejected. Element whitelist: `section h1 h2 h3 p ul ol li
   table thead tbody tr th td b strong i em code a div span br hr blockquote`.
3. No `<img>` and no id starting `cover-` or equal to `stale-bar`.
4. **Citation gate (anti-fabrication):** every viewer link you emit must be
   copied **verbatim** from `report-input.md` — the pack's links have the form
   `…/v/{TICKER}/{citation_id}/{N}` on the agentii viewer. The assembler
   rejects any `{ticker}/{citation_id}` pair it cannot find in the sources,
   with an offender list. Never invent a citation_id; every `[FACT]` number
   you surface keeps its citation link. Citations that only exist as bare
   text in the pack (keyword scans like `ISRG × ect75 × page1`) may be
   rendered as plain text — do not turn them into fake links.
5. **Charts (Q48) are tokens, not images** — only for theses with price /
   valuation data:
   ```html
   <div data-chart="peer_bars" data-spec='{"labels":["NVDA"],"values":[215.9]}' data-height="200"></div>
   ```
   `data-spec` is single-quoted JSON (no apostrophes inside); kinds:
   `football_field {labels,lows,highs}`, `peer_bars {labels,values}`,
   `kpi_trend {x,y}`, `scatter {x,y}`, `scenario_tree {edges}`.
   `data-height` is your page-budget claim — the overflow estimator counts it
   exactly, so keep it honest. Research-only theses (market-data stage none)
   emit no chart tokens.

## Letter-fit rules (author to these numbers)

A letter page holds ~40 lines of prose at 11pt — the `--check-only` gate and the
in-browser red `⚠ overflow` outline are the enforcement. Author conservatively:

- ≤ **40** prose lines per page (paragraphs + bullets, combined).
- ≤ **18** table rows per page when cells wrap ≤ 2 lines each; a citation cell
  counts as 2 lines. Split long tables across pages by ticker or period —
  e.g. the cross-ticker evidence table at ~44 rows becomes 3–4 pages.
- Headings cost budget: one `h1`/`h2` + 2–3 short paragraphs, or a table block —
  not both, unless the table is small.

## What a good report contains

- **Executive Summary** — the synthesis's own Executive Summary prose, condensed
  to the operative sentences; the headline callout (capability timeline band +
  confidence) kept intact.
- **Pillar verdicts** — every pillar: verdict, falsifier result, the best
  evidence bullet(s) with citations. Verdicts render as a table; the note text
  after `#` in `pillar_verdicts` frontmatter is the falsifier note column.
- **Capability timeline** — the synthesis §2 table verbatim-ish (it is the
  thesis's headline output).
- **Evidence** — the cross-ticker table (§3), split to fit; negative findings
  ("no MTBF disclosure anywhere") are evidence too — keep them.
- **Coverage gaps** — the synthesis §4 items, not the reducer JSON; the
  mechanical rollup (entry counts by skill) may appear as one small table.
- **Data-quality flags** (§5) and **contract compliance** (§6), condensed.
- Nothing from the raw YAML/JSON of sources — the pack is your input, not your
  output; prose and structure are yours, facts and citations are verbatim.

## Regeneration discipline (Q50)

The assembled report embeds `sources_hash` (all markdown sources) +
`template_version`; `converge` flags `html_stale` when they drift. Re-run the
loop above when that finding appears — never hand-edit `thesis-report.html`.
