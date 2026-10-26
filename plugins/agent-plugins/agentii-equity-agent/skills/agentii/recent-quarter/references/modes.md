# recent-quarter — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: consolidated-p-and-l (essentials)

**Display name**: Consolidated P&L Progression

**Objective**: Extract and present the most recent quarter's consolidated P&L — revenue, gross profit, operating income, net income, diluted EPS — with sequential (QoQ) and year-over-year (YoY) growth rates.

**Tool calls**: `resolve_period(ticker, "last quarter", as_of?)` → fiscal `period_id`; `get_company_financials(ticker, fiscal_year=<resolved year>, fiscal_period=<resolved period>)`; `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss"], period_id=<period_id>)`

**Output**: Consolidated P&L table with QoQ and YoY growth rates. Citation format: `{ticker} {citation_id} page<N>`.

### Mode: margin-analysis (essentials)

**Display name**: Margin Analysis

**Objective**: Track gross margin, operating margin, and net margin across the most recent 4 quarters. Identify trends, inflection points, and drivers (pricing power, cost structure changes, operating leverage).

**Tool calls**: `resolve_period(ticker, "last quarter", as_of?)` and the prior three quarters → fiscal `period_id`s; `batch_search` with one `search_xbrl_facts(ticker, concept=[...], period_id=<id>)` per period. No widen fallback.

**Output**: Margin trend table with QoQ deltas. Commentary on margin drivers.

### Mode: earnings-vs-consensus

**Display name**: Earnings vs. Consensus

**Objective**: Compare actual EPS against consensus estimates for the most recent quarter. Present surprise %, beat/miss track record (trailing 4 quarters), and guidance accuracy.

**Tool calls**: `resolve_period(ticker, "last quarter", as_of?)` → resolved fiscal year; `search_earnings_calendar(ticker, fiscal_year=<resolved year>)`; read `date_basis`/`fiscal_source`, never a fiscal boundary.

**Output**: EPS actual vs. estimated table with surprise % and beat/miss streak.

### Mode: sequential-growth

**Display name**: Sequential Growth Analysis

**Objective**: Compute quarter-over-quarter growth rates for revenue, gross profit, operating income, and EPS across the trailing 4 quarters. Highlight accelerating or decelerating trends.

**Tool calls**: `resolve_period(ticker, "last quarter", as_of?)` and the prior three quarters → fiscal `period_id`s; `batch_search` with one `search_xbrl_facts(ticker, concept=[...], period_id=<id>)` per period.

**Output**: Sequential growth rate table with trend arrows and inflection detection.

### Mode: forward-outlook

**Display name**: Forward Outlook & Guidance

**Objective**: Extract management guidance for the upcoming quarter, upcoming earnings date, consensus estimates for next quarter, and key catalysts (product launches, regulatory events, earnings announcements).

**Tool calls**: `search_earnings_calendar(ticker, upcoming=true)`, `get_company_financials/{ticker}` (for guidance narrative)

**Output**: Forward outlook summary with guidance, consensus, upcoming catalysts, and earnings date.
