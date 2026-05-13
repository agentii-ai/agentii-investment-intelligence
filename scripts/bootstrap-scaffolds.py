#!/usr/bin/env python3
"""
One-shot scaffold generator for Phase 1 (T033–T040).

Emits:
  - 24 SKILL.md files (8 dim + 5 bi + 4 industry + 7 models-and-pitches)
    with valid frontmatter (name, description, multi_ticker_semantics) and
    all sections required by check.py Checks 9/10/11/12.
  - 21 command .md files with frontmatter (description, argument-hint) and
    placeholder ## Workflow section.

Idempotent — skips files that already exist.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins" / "vertical-plugins"

# (vertical, skill_name, description_stub, mts, analog_note)
SKILLS = [
    # equity-research-core (8 dimensions)
    ("equity-research-core", "dim-recent-quarter-performance",
     "Recent quarter performance analysis: revenue breakdown, margin drivers, EPS assessment, management guidance, reaction framework, and sequential-quarter momentum.",
     "single_target", "earnings-preview/morning-note"),
    ("equity-research-core", "dim-competitive-landscape",
     "Competitive landscape analysis: peer positioning, market-share dynamics, moat assessment, pricing power, and win/loss patterns across the sector.",
     "target_with_optional_peers", "sector-overview"),
    ("equity-research-core", "dim-growth-strategy",
     "Growth strategy analysis: organic vs inorganic growth, TAM expansion, product pipeline, M&A capacity, and capital-deployment discipline.",
     "single_target", "initiating-coverage"),
    ("equity-research-core", "dim-secular-tech-trends",
     "Secular technology trend analysis: AI adoption, platform shifts, data-infrastructure exposure, and long-duration tailwind assessment.",
     "target_with_optional_peers", "idea-generation"),
    ("equity-research-core", "dim-turnaround-stagnation",
     "Turnaround vs stagnation analysis: margin-recovery potential, leadership change impact, cost rationalization, and peer benchmarking for inflection signals.",
     "target_with_required_peers", "thesis-tracker"),
    ("equity-research-core", "dim-risk-analysis",
     "Risk analysis: regulatory exposure, customer concentration, supply-chain vulnerabilities, balance-sheet flexibility, and scenario-based downside assessment.",
     "single_target", "thesis-tracker"),
    ("equity-research-core", "dim-earnings-sentiment",
     "Earnings sentiment analysis: transcript tone, Q&A dynamics, management confidence signals, and sell-side estimate revision patterns.",
     "single_target", "catalyst-calendar"),
    ("equity-research-core", "dim-valuation-methods",
     "Valuation methods analysis: multiples-based, DCF-anchored, asset-value framework, and peer-relative valuation triangulation.",
     "single_target", "initiating-coverage"),
    # business-intelligence (5)
    ("business-intelligence", "business-model-analysis",
     "Business model analysis: revenue classification, customer concentration, unit economics extraction, and monetization-lever identification.",
     "single_target", ""),
    ("business-intelligence", "revenue-decomposition",
     "Revenue decomposition: segment-level breakdown, geographic split, product-line waterfall, and organic-vs-inorganic growth attribution.",
     "single_target", ""),
    ("business-intelligence", "unit-economics",
     "Unit economics: LTV/CAC, payback period, contribution margin, retention curves, and cohort-level profitability trajectory.",
     "single_target", ""),
    ("business-intelligence", "what-if-scenario",
     "What-if scenario analysis: base/bull/bear case construction, sensitivity tables, and probability-weighted outcome assessment.",
     "single_target", ""),
    ("business-intelligence", "operational-kpi-tracker",
     "Operational KPI tracker: sector-specific metrics (DAU/MAU, ARR, gross bookings, orders shipped), sequential trend, and peer comparison.",
     "single_target", ""),
    # industry-analysis (4)
    ("industry-analysis", "peer-benchmarking",
     "Peer benchmarking: growth/margin/valuation matrix across a peer group, with quartile rankings and outlier flagging.",
     "target_with_required_peers", ""),
    ("industry-analysis", "sector-overview",
     "Sector overview: structure, key players, secular dynamics, regulatory backdrop, and investment-framework summary.",
     "target_with_optional_peers", ""),
    ("industry-analysis", "competitive-positioning",
     "Competitive positioning: Porter's Five Forces, moat assessment, strategic-group analysis, and positioning map.",
     "target_with_optional_peers", ""),
    ("industry-analysis", "supply-chain-map",
     "Supply-chain map: upstream suppliers, downstream customers, key dependencies, and geopolitical-exposure analysis.",
     "single_target", ""),
    # models-and-pitches (7; 6 ported + pitch-deck net-new)
    ("models-and-pitches", "dcf-model",
     "DCF valuation model: 5-10 year projection, terminal value, WACC construction, and sensitivity tables. All projection/margin/discount/PV cells must be live formulas (FR-020/FR-044 hard gate).",
     "single_target", ""),
    ("models-and-pitches", "comps-analysis",
     "Trading comps analysis: peer-group selection, trading-multiple triangulation (EV/Sales, EV/EBITDA, P/E, P/B), and implied-valuation range.",
     "target_with_required_peers", ""),
    ("models-and-pitches", "3-statement-model",
     "3-statement integrated financial model: IS/BS/CFS triangulation, 5 historical + 5 forecast years, driver-based projection.",
     "single_target", ""),
    ("models-and-pitches", "lbo-model",
     "Leveraged buyout model: sources & uses, debt schedule, exit-multiple analysis, and sponsor IRR sensitivity.",
     "single_target", ""),
    ("models-and-pitches", "audit-xls",
     "Excel workbook audit: scan for hardcoded values in projection/margin/discount/PV/sensitivity cells, flag formula integrity issues.",
     "single_target", ""),
    ("models-and-pitches", "xlsx-author",
     "Excel workbook author: build formula-driven workbooks from an xlsx_spec using openpyxl-headless or Office JS binding.",
     "single_target", ""),
    ("models-and-pitches", "pitch-deck",
     "Pitch deck builder: 12-16 slide investment-thesis presentation with sourced-footers, financial highlights, comps, risks, and catalysts.",
     "single_target", "composite-origin: pptx-author + ppt-template-creator + deck-refresh + ib-check-deck"),
]

TRIGGERS_PHRASES = [
    "analyze {noun}",
    "run {noun} analysis",
    "produce {noun} report",
    "{noun} breakdown",
    "{noun} deep dive",
    "build a {noun}",
    "assess {noun}",
    "quantify {noun}",
    "compare {noun} across peers",
    "review {noun} for",
    "generate {noun} on",
    "{noun} for investment decision",
]


def render_skill(vertical: str, name: str, desc: str, mts: str, analog: str) -> str:
    noun = name.replace("-", " ")
    triggers = "\n".join(f"- {t.format(noun=noun)}" for t in TRIGGERS_PHRASES[:12])
    analog_comment = f"\n<!-- analog: {analog} -->\n" if analog else ""
    return f"""---
name: {name}
description: >-
  {desc}
multi_ticker_semantics: {mts}
parameter_free: false
---
{analog_comment}
## Preflight

!curl -s -o /dev/null -w "%{{http_code}}" --max-time 2 https://mcp.agentii.ai/mcp/health 2>/dev/null || echo "UNREACHABLE"

## Triggers

{triggers}

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| lookback_years | 3 | Historical data window |
| include_peers | false | Whether to surface a peer comparison block |

## Methodology

*This is a Phase 1 scaffold. Full methodology authored in Phase 3/4/5 (see tasks.md).*

## Output Structure

*Prescribed deliverable format authored in Phase 3/4/5. Must include per FR-020a: section headings, expected content per section, citation density (≥1 per 200 words).*

## Error Handling

| Failure Mode | Detection | Action | User-Facing Message |
|---|---|---|---|
| Missing data | Data API returns empty result set | Widen date range and retry once | "No data available for {{ticker}} in requested window." |
| Partial data | Data API returns <80% expected records | Proceed with coverage gaps section | "Analysis based on partial data; see Coverage Gaps section." |
| Sector mismatch | Peer sector != target sector | Filter out mismatched peers | "Removed {{n}} peer(s) due to sector mismatch." |
| Insufficient history | Ticker <3 years on public markets | Downgrade to limited-history profile | "Limited historical data; analysis adjusted accordingly." |
| MCP unreachable | Preflight probe fails | Halt with actionable error | "agentii data plane unreachable; check connection." |
"""


def render_command(vertical: str, cmd: str, skill: str, desc: str, arghint: str) -> str:
    return f"""---
description: {desc}
argument-hint: {arghint}
---

## Workflow

1. Validate ticker argument.
2. Delegate to the `{skill}` skill bundled under `{vertical}`.
3. Return the structured deliverable produced by the skill.

*Full workflow authored alongside the skill methodology (Phase 3/4/5).*
"""


COMMANDS = [
    # equity-research-core
    ("equity-research-core", "recent-quarter", "dim-recent-quarter-performance",
     "Recent quarter performance analysis", "<TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]"),
    ("equity-research-core", "competitive", "dim-competitive-landscape",
     "Competitive landscape analysis", "<TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]"),
    ("equity-research-core", "growth-strategy", "dim-growth-strategy",
     "Growth strategy analysis", "<TICKER> [--mode=<slug>]"),
    ("equity-research-core", "secular-trends", "dim-secular-tech-trends",
     "Secular technology trends analysis", "<TICKER> [--mode=<slug>] [--peers=<T1>,<T2>]"),
    ("equity-research-core", "turnaround", "dim-turnaround-stagnation",
     "Turnaround vs stagnation analysis", "<TICKER> --peers=<T1>,<T2> [--mode=<slug>]"),
    ("equity-research-core", "risk", "dim-risk-analysis",
     "Risk analysis", "<TICKER> [--mode=<slug>]"),
    ("equity-research-core", "earnings-sentiment", "dim-earnings-sentiment",
     "Earnings sentiment analysis", "<TICKER> [--mode=<slug>]"),
    ("equity-research-core", "valuation-methods", "dim-valuation-methods",
     "Valuation methods analysis", "<TICKER> [--mode=<slug>]"),
    # business-intelligence (4 commands; operational-kpi-tracker has no command at v1.0)
    ("business-intelligence", "business-model", "business-model-analysis",
     "Business model analysis", "<TICKER>"),
    ("business-intelligence", "revenue-decomp", "revenue-decomposition",
     "Revenue decomposition", "<TICKER>"),
    ("business-intelligence", "unit-economics", "unit-economics",
     "Unit economics analysis", "<TICKER>"),
    ("business-intelligence", "what-if", "what-if-scenario",
     "What-if scenario analysis", "<TICKER> [--mode=<scenario-slug>]"),
    # industry-analysis (3 commands; competitive-positioning has no command at v1.0)
    ("industry-analysis", "peer-bench", "peer-benchmarking",
     "Peer benchmarking", "<TICKER> --peers=<T1>,<T2>,<T3>"),
    ("industry-analysis", "sector-overview", "sector-overview",
     "Sector overview", "<TICKER> [--peers=<T1>,<T2>]"),
    ("industry-analysis", "supply-chain", "supply-chain-map",
     "Supply-chain map", "<TICKER>"),
    # models-and-pitches (6 commands)
    ("models-and-pitches", "dcf", "dcf-model",
     "Build a DCF valuation model", "<TICKER> [--peers=<T1>,<T2>]"),
    ("models-and-pitches", "comps", "comps-analysis",
     "Trading comps analysis", "<TICKER> --peers=<T1>,<T2>,<T3>"),
    ("models-and-pitches", "lbo", "lbo-model",
     "LBO model", "<TICKER>"),
    ("models-and-pitches", "3-statement", "3-statement-model",
     "3-statement financial model", "<TICKER>"),
    ("models-and-pitches", "audit-xls", "audit-xls",
     "Audit an Excel workbook for hardcoded values", "<FILE.xlsx>"),
    ("models-and-pitches", "pitch-deck", "pitch-deck",
     "Build a pitch deck", "<TICKER>"),
]


def main() -> int:
    written_skills = 0
    skipped_skills = 0
    for vertical, name, desc, mts, analog in SKILLS:
        skill_dir = PLUGINS / vertical / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        target = skill_dir / "SKILL.md"
        if target.exists() and target.stat().st_size > 0:
            skipped_skills += 1
            continue
        target.write_text(render_skill(vertical, name, desc, mts, analog))
        written_skills += 1

    written_cmds = 0
    skipped_cmds = 0
    for vertical, cmd, skill, desc, arghint in COMMANDS:
        cmd_dir = PLUGINS / vertical / "commands"
        cmd_dir.mkdir(parents=True, exist_ok=True)
        target = cmd_dir / f"{cmd}.md"
        if target.exists() and target.stat().st_size > 0:
            skipped_cmds += 1
            continue
        target.write_text(render_command(vertical, cmd, skill, desc, arghint))
        written_cmds += 1

    print(f"skills: wrote {written_skills}, skipped existing {skipped_skills}")
    print(f"commands: wrote {written_cmds}, skipped existing {skipped_cmds}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
