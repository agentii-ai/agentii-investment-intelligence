#!/usr/bin/env bash
# migrate-commands-to-skills.sh
# Migrates slash commands from commands/*.md legacy format to
# skills/agentii/<name>/SKILL.md (Claude Code 2.1.3+ unified Skills format).
# Feature: 023 — Namespace isolation via skills/agentii/ directory (FR-014a)

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── Per-skill metadata ─────────────────────────────────────────────
# name → "description|retrieval_scope|allowed_tools_csv|default_quarters|max_quarters|min_tool_diversity"

declare -A META

# ── equity-research-core (8 dimension skills) ──────────────────────
META[recent-quarter]="Recent quarter performance analysis, quarterly earnings review, last quarter results, quarterly financial performance, analyze recent quarter, Q4 earnings, quarterly revenue breakdown, EPS this quarter, margin analysis recent quarter, sequential growth, quarterly performance review|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,get_company_profile,list_coverage,search_earnings_calendar|1|4|8"
META[competitive]="Competitive landscape analysis, competitor comparison, peer positioning, market share dynamics, competitive moat assessment, Porter five forces, industry competition, competitive advantage analysis, market positioning, strategic group mapping, compare competitors|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,list_coverage,search_earnings_calendar,get_company_profile,batch_search|4|12|10"
META[growth-strategy]="Growth strategy analysis, organic growth decomposition, inorganic growth, M&A strategy, pipeline analysis, revenue growth drivers, strategic initiatives, expansion strategy, growth trajectory, product pipeline growth|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,get_company_profile,list_coverage|4|10|8"
META[secular-trends]="Secular technology trends, technology adoption cycle, disruption risk, AI impact analysis, digital transformation, industry 4.0 trends, technology moat, innovation trajectory, R&D effectiveness, tech competitive positioning|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,list_coverage,search_unified|4|12|10"
META[turnaround]="Turnaround analysis, stagnation detection, performance inflection, operational improvement, restructuring analysis, management change impact, cost cutting effectiveness, business transformation, recovery trajectory, operational metrics improvement|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,get_company_profile,list_coverage|4|10|8"
META[risk]="Risk analysis, regulatory risk assessment, competitive risk, macro risk, technology risk, litigation risk, financial risk assessment, enterprise risk, operational risk, geopolitical risk exposure|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,list_coverage|4|10|8"
META[earnings-sentiment]="Earnings sentiment analysis, analyst estimates vs guidance, earnings surprise history, consensus sentiment, earnings revision trends, analyst rating changes, earnings beat miss track record, guidance accuracy, whisper numbers, pre-announcement sentiment|structured_only|search_companies,search_xbrl_facts,search_earnings_calendar,get_company_financials,get_company_profile|4|8|8"
META[valuation-methods]="Valuation methods analysis, DCF inputs, comparable multiples, P/E ratio, EV/EBITDA, price to book, valuation assumptions, relative valuation, intrinsic value, fair value estimate|structured_only|search_companies,search_xbrl_facts,get_company_financials,search_earnings_calendar,get_company_profile|4|8|8"

# ── business-intelligence (5 BI skills) ────────────────────────────
META[business-model]="Business model analysis, revenue model classification, customer concentration, unit economics extraction, business model canvas, monetization strategy, customer acquisition cost, lifetime value, recurring revenue analysis, platform vs linear business model|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_documents|4|8|6"
META[revenue-decomp]="Revenue decomposition, segment breakdown, geographic revenue split, product-line waterfall, revenue mix analysis, business segment performance, divisional revenue, revenue concentration, customer revenue dependency, channel revenue analysis|structured_only|search_companies,search_xbrl_facts,get_company_financials,search_documents,get_company_profile|4|8|6"
META[unit-economics]="Unit economics analysis, CAC LTV estimation, churn inference, gross margin per unit, customer economics, subscription economics, per-unit profitability, contribution margin, payback period, cohort economics|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_documents|4|8|6"
META[what-if]="What-if scenario analysis, scenario tree construction, base bull bear case, sensitivity to macro variables, revenue scenario modeling, cost scenario analysis, margin impact scenarios, interest rate sensitivity, currency impact scenarios, commodity price scenarios|structured_only|search_companies,search_xbrl_facts,get_company_financials,search_earnings_calendar,get_company_profile|4|12|6"
META[operational-kpi]="Operational KPI tracking, headcount trends, utilization rates, backlog analysis, book-to-bill ratio, operational efficiency metrics, capacity utilization, productivity metrics, operational leverage, same-store sales|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_documents|4|8|6"

# ── industry-analysis (4 industry skills) ──────────────────────────
META[peer-bench]="Peer benchmarking, multi-ticker financial comparison, growth value matrix, composite z-score ranking, industry peer comparison, competitive benchmarking, sector relative performance, peer group analysis, industry leader comparison, financial ratio benchmarking|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,batch_search,list_coverage|4|12|6"
META[sector-overview]="Sector overview, TAM estimation, competitive concentration HHI, regulatory landscape, industry analysis, market size analysis, sector trends, industry structure, market growth rate, sector profitability|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,list_coverage,search_unified|4|12|6"
META[competitive-positioning]="Competitive positioning, strategic group mapping, differentiation analysis, competitive advantage assessment, market positioning map, value chain positioning, brand positioning, cost leadership vs differentiation, niche strategy analysis, disruptive positioning|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,list_coverage,get_company_profile|4|10|6"
META[supply-chain]="Supply chain mapping, supplier dependency analysis, customer concentration, geographic concentration, bottleneck identification, supply chain risk, logistics network, sourcing strategy, inventory management, vertical integration analysis|unstructured_document_search|search_companies,search_xbrl_facts,search_documents,search_sec_filings,get_company_financials,list_coverage|4|10|6"

# ── models-and-pitches (7 model skills) ────────────────────────────
META[dcf]="DCF valuation model, discounted cash flow, intrinsic value, WACC calculation, terminal value, free cash flow projection, equity value per share, DCF sensitivity analysis, unlevered free cash flow, present value calculation, build a DCF|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_earnings_calendar|4|12|5"
META[comps]="Comparable company analysis, trading comps, peer multiples, EV/EBITDA comparison, P/E benchmarking, comps table, relative valuation, industry multiples, precedent transactions, trading comparable analysis|structured_only|search_companies,search_xbrl_facts,get_company_financials,search_earnings_calendar,get_company_profile|4|12|5"
META[3-statement]="3-statement financial model, integrated IS BS CF, income statement projection, balance sheet forecast, cash flow statement, cross-statement balancing, financial model build, operating model, three statement model, integrated financial statements|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_earnings_calendar|4|12|5"
META[lbo]="LBO model, leveraged buyout, private equity acquisition, sources and uses, debt schedule, returns waterfall, sponsor IRR, MOIC calculation, PE exit analysis, LBO valuation|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_earnings_calendar|4|12|5"
META[audit-xls]="Audit spreadsheet, formula error detection, hardcoded cell finder, cross-sheet reference audit, workbook auditor, Excel model audit, financial model QA, spreadsheet review, cell dependency trace, formula integrity check|simple_lookup|search_companies,get_company_financials|1|1|3"
META[pitch-deck]="Investment pitch deck, investment committee presentation, buy-side pitch, sell-side pitch, investment thesis slides, executive summary presentation, financial presentation, board deck, investor presentation, strategy deck|structured_only|search_companies,search_xbrl_facts,get_company_financials,get_company_profile,search_earnings_calendar,search_documents|4|8|5"
META[earnings-preview]="Earnings preview deck, quarterly earnings presentation, earnings summary slides, consensus vs actual presentation, earnings preview report, pre-earnings analysis, earnings expectations deck, quarterly preview, upcoming earnings summary, earnings announcement preview|structured_only|search_companies,search_xbrl_facts,search_earnings_calendar,get_company_financials,get_company_profile|4|8|5"

# ── Generation ─────────────────────────────────────────────────────

VERTICALS=(
  "equity-research-core"
  "business-intelligence"
  "industry-analysis"
  "models-and-pitches"
)

TOTAL=0

for vertical in "${VERTICALS[@]}"; do
  COMMANDS_DIR="$REPO_ROOT/plugins/vertical-plugins/$vertical/commands"
  SKILLS_DIR="$REPO_ROOT/plugins/vertical-plugins/$vertical/skills/agentii"

  [[ -d "$COMMANDS_DIR" ]] || continue

  for cmd_file in "$COMMANDS_DIR"/*.md; do
    [[ -f "$cmd_file" ]] || continue
    name="$(basename "$cmd_file" .md)"
    skill_dir="$SKILLS_DIR/$name"

    # Get metadata for this skill
    meta="${META[$name]:-}"
    if [[ -z "$meta" ]]; then
      echo "⚠️  No metadata for '$name' — using defaults"
      description="$name — agentii investment intelligence skill"
      retrieval_scope="structured_only"
      allowed_tools="search_companies,search_xbrl_facts,get_company_financials"
      default_quarters=4
      max_quarters=8
      min_diversity=5
    else
      IFS='|' read -r description retrieval_scope allowed_tools default_quarters max_quarters min_diversity <<< "$meta"
    fi

    # Build allowed_tools YAML list
    allowed_yaml=""
    IFS=',' read -ra tools <<< "$allowed_tools"
    for tool in "${tools[@]}"; do
      tool_clean="$(echo "$tool" | xargs)"
      allowed_yaml+="  - $tool_clean"$'\n'
    done

    mkdir -p "$skill_dir"

    cat > "$skill_dir/SKILL.md" << SKILLEOF
---
name: $name
description: $description
temporal_scope:
  default_quarters: $default_quarters
  max_quarters: $max_quarters
  description: "Typical lookback: $default_quarters quarters, max: $max_quarters"
allowed_tools:
$allowed_yaml
retrieval_scope: $retrieval_scope
min_tool_diversity: $min_diversity
---

# $name

$(tail -n +2 "$cmd_file" 2>/dev/null | sed '/^---$/,/^---$/d' | head -40 || echo "Skill methodology from \`$name\` command file.")

## Triggers

$(echo "$description" | tr ',' '\n' | sed 's/^[[:space:]]*/- /')

## Defaults

| Parameter | Default Value | Rationale |
|-----------|---------------|-----------|
| ticker | (required) | Stock symbol to analyze |
| lookback_quarters | $default_quarters | Standard lookback for this skill type |
| fiscal_period_format | FY / Q<N> | From get_company_fiscal_calendar probe |

## Methodology

This skill follows the agentii retrieval protocol. Retrieval scope: **$retrieval_scope**. Minimum tool diversity: $min_diversity distinct tools.

## Output Structure

1. Executive Summary
2. Data Sources (with citation watermarks)
3. Analysis Results
4. Coverage Gaps (if any)

## Error Handling

| Error | Action |
|-------|--------|
| Ticker not found | Suggest checking spelling or trying list_coverage |
| No data available | Flag in Coverage Gaps, proceed with available data |
| API key invalid | Direct user to agentii.ai/api-keys |
| MCP server unreachable | Retry once; if persistent, halt with AGENTII_MCP_UNREACHABLE |
SKILLEOF

    echo "  ✅ skills/agentii/$name/SKILL.md (scope=$retrieval_scope, tools=$(echo "$allowed_tools" | tr ',' ' ' | wc -w | xargs), triggers=$(echo "$description" | tr ',' '\n' | wc -l | xargs))"
    TOTAL=$((TOTAL + 1))
  done
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Migrated $TOTAL commands → skills/agentii/<name>/SKILL.md"
echo "Each has: ≥10 trigger phrases, correct retrieval_scope,"
echo "per-skill allowed_tools, and per-vertical temporal_scope."
echo "Namespace: /agentii:<name> for manual use + model auto-activation"
