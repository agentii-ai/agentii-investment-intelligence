---
name: synthesize
description: Thesis report synthesis — turn a thesis's markdown artifacts into its letter-size thesis-report.html, then OPTIMIZE it against real page renders. Four-step loop — pack (deterministic Python bundle of all sources + report/metrics.json), author (the LLM writes report/content.html — narrative, KPI tiles, badges, timeline, tables and citations are LLM judgment), assemble (deterministic validation, template injection, Q50 pins, Q47 overflow gate), render + optimize (Chrome headless per-page PNGs — the LLM reads them and iterates until every page is visually clean). Spec 046 Q46–Q50.
role: kit
market_data_stage: none
allowed_tools: []
retrieval_scope: structured_only
---

# agentii.synthesize

The single-point HTML generation step (spec 046 Q46–Q50): ONE `thesis-report.html`
per thesis, authored from the markdown artifacts and then optimized against
real renders. Analysis skills emit markdown only (Q49); the report is assembled
here, at the synthesis step, after the cross-stock synthesis
(`_cross/*_synthesis.md`) exists.

## When to run

- After the synthesis tasks complete (the `_cross/` deliverable is written).
- When `converge` emits an `html_stale` finding (sources or template moved).
- On explicit request, or once at thesis completion (Q50 regeneration triggers).

## The loop (four steps + optimize)

```bash
cd agentii-investment-intelligence
# 1. PACK — deterministic bundle of every source, verbatim (no timestamps),
#    PLUS report/metrics.json (per-ticker key_metrics/conclusions/counts —
#    machine-ready numbers for KPI tiles and kpi_trend charts, RAW values):
python3 scripts/synthesize_report.py pack --thesis <theses/{nnn}-{slug}>

# 2. AUTHOR — read <thesis>/report-input.md (verbatim sources + citations)
#    and <thesis>/report/metrics.json (numbers). Write
#    <thesis>/report/content.html — the report's actual content is YOUR judgment.

# 3. ASSEMBLE — validate + inject + gate (advisories on stderr are guidance,
#    the hard gates are silent until they fail):
python3 scripts/synthesize_report.py assemble --thesis <thesis-dir> --check-only  # fit loop
python3 scripts/synthesize_report.py assemble --thesis <thesis-dir>               # deliver

# 4. RENDER — Chrome headless → letter PDF → per-page PNGs + manifest:
python3 scripts/render_report.py render --thesis <thesis-dir>

# 5. OPTIMIZE (required, not optional): READ the PNGs page by page, in batches
#    of 3–4. Fix real problems the estimator cannot see — clipped tables, ugly
#    URL wrapping, weak density, orphan headings, oversized tiles. Edit
#    content.html → re-assemble → re-render until EVERY page is visually clean.
```

Renders never gate CI (Chrome/poppler may be absent) — **the author's own visual
pass is the gate**. `assemble --check-only` remains the estimator fallback; a
missing render is a hard stop for delivery, not a silent skip. `render --verify`
also checks each PNG is letter-width at the requested dpi.

## content.html contract (the assembler hard-gates every rule)

You author **only the page sequence** — a fragment, never a document:

1. One or more `<section class="page">…</section>` blocks, no nesting. The cover
   is page 1 and is template-owned: **do not author it** — the assembler fills
   kicker / title / claim / pins / universe / generated / TOC, and injects the
   running sheet head/foot, page marks (`NN / TOTAL`) and corner registration
   marks into every page.
2. Fragment only — `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`, `<style>`,
   `<script>` are rejected. Element whitelist: `section h1 h2 h3 p ul ol li
   table thead tbody tr th td b strong i em code a div span br hr blockquote`.
3. No `<img>` and no id starting `cover-` or equal to `stale-bar`.
4. **Reserved classes — never emit these** (assembler chrome):
   `sheet-head`, `sheet-foot`, `reg`, `cover`, `page-mark`.
5. **Citation gate (anti-fabrication):** every viewer link you emit must be
   copied **verbatim** from `report-input.md` — the pack's links have the form
   `…/v/{TICKER}/{citation_id}/{N}` on the agentii viewer. The assembler
   rejects any `{ticker}/{citation_id}` pair it cannot find in the sources,
   with an offender list. Never invent a citation_id; every `[FACT]` number
   you surface keeps its citation link. `metrics.json` carries NO citation
   ids — never build viewer links from tiles. Citations that only exist as
   bare text in the pack (keyword scans like `ISRG × ect75 × page1`) may be
   rendered as plain text — do not turn them into fake links.
6. **Charts (Q48) are tokens, not images:**
   ```html
   <div data-chart="kpi_trend" data-spec='{"x":["FY2024","FY2025","H1 2026"],"y":[77.7,128.3,96.3]}' data-height="160"></div>
   ```
   `data-spec` is single-quoted JSON (no apostrophes inside).
   `kpi_trend` is for **non-price structured series** (capex trajectories,
   revenue series) built from `metrics.json` multi-period keys.
   `football_field {labels,lows,highs}`, `peer_bars {labels,values}`,
   `scatter {x,y}`, `scenario_tree {edges}` remain **market-data-only**.
   `data-height` is your page-budget claim — the overflow estimator counts it
   exactly, so keep it honest. Research-only theses (market-data stage none)
   emit only `kpi_trend`, if anything.

## Component rules (v0.3.0 design system)

- **KPI tiles**: the executive-summary page REQUIRED to open with a
  `.stat-row` of 2–4 thesis-level tiles (e.g. artifacts count · key-metrics
  count · pillars supported · GPT-3.5 window). Per-ticker sections carry 2–4
  ticker tiles. Structure: `div.stat > div.num + div.lbl + div.sub`. Numbers
  from `metrics.json`, formatted per style.md: `$28.5B` (not `$28,476M`; one
  decimal for billions, none for millions), `12.4%`, `+12.4%`, `14.2x`.
- **Badges** — two orthogonal axes, never confused:
  - taxonomy (FR-092): `[FACT]`→`.badge-fact`, `[DEDUCTED]`→`.badge-deducted`,
    `[VIEW]`→`.badge-view` — use on evidence-table rows and claim prose;
  - verdicts: `supported`→`.badge-supported`, `indeterminate`→
    `.badge-indeterminate`, `refuted`→`.badge-refuted` — every pillar verdict
    carries one.
- **Timeline**: the capability-timeline page uses `.timeline` with `.tl-item`
  blocks — `.tl-phase` holds the mono phase label, the prose keeps the
  synthesis's wording with its citations.
- **Kickers**: every page opens with a `.sec-kicker` (mono editorial label,
  e.g. `THE CORPUS · 24 ARTIFACTS`), never the heading text repeated.

## Letter-fit rules (author to these numbers)

A letter page holds ~40 lines of prose at 11pt — the `--check-only` gate, the
render PNGs and the in-browser red `⚠ overflow` outline are the enforcement.
Author conservatively:

- ≤ **40** prose lines per page (paragraphs + bullets, combined).
- ≤ **18** table rows per page when cells wrap ≤ 2 lines each; a citation cell
  counts as 2 lines. Split long tables across pages by ticker or period.
- A `.stat-row` costs ~4 lines; a `.tl-item` costs ~3; a chart token costs its
  `data-height` honestly.
- Headings cost budget: one `h1`/`h2` + 2–3 short paragraphs, or a table block —
  not both, unless the table is small.

## What a good report contains

- **Executive Summary** — the synthesis's own prose, condensed to the operative
  sentences; tile row; the headline callout (capability timeline band +
  confidence) kept intact; verdict list with badges.
- **Pillar verdicts** — every pillar: verdict badge, falsifier result, the best
  evidence bullets with citations (verbatim from the pack).
- **Capability timeline** — the synthesis §2 content as a styled `.timeline`
  (it is the thesis's headline output).
- **Evidence** — the cross-ticker table (§3) split to fit, `[FACT]` badges on
  rows, citation links inline; negative findings ("no MTBF disclosure
  anywhere") are evidence too — keep them.
- **Coverage gaps** — the synthesis §4 items; the mechanical rollup (entry
  counts by skill) may appear as one small table.
- **Data-quality flags** (§5) and **contract compliance** (§6), condensed.
- Nothing from the raw YAML/JSON of sources — the pack and metrics.json are
  your inputs, not your output; prose and structure are yours, facts and
  citations are verbatim.

## Quality checklist (MUST, before delivery)

1. Exec-summary tile row present (2–4 tiles).
2. All pillar verdicts carry colored badges; taxonomy badges on evidence rows.
3. Capability timeline styled (`.timeline`/`.tl-item`/`.tl-phase`).
4. Evidence tables follow style.md (Metric → Current → Prior → YoY → Citation)
   with inline citation links on every fact.
5. `.sec-kicker` on every page.
6. No empty pages, no orphan headings at page bottoms.
7. No raw markdown leakage (`**`, backtick fences, `### `).
8. Tier-0 `--check-only` pass AND `render` page-count == section-count AND
   every PNG visually verified clean (no clipped tables, no red overflow
   outlines, sane density).

## Regeneration discipline (Q50)

The assembled report embeds `sources_hash` (all markdown sources) +
`template_version`; `converge` flags `html_stale` when they drift. Re-run the
loop above when that finding appears — never hand-edit `thesis-report.html`.
