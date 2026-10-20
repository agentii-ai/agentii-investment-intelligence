# recent-quarter — Analyst Mode Definitions

Extracted from SKILL.md for progressive disclosure (US5). The skill body keeps a pointer under `## Methodology → Analyst Modes`.

### Mode: consolidated-p-and-l (essentials)

**Display name**: Consolidated P&L Progression

**Objective**: Extract and present the most recent quarter's consolidated P&L — revenue, gross profit, operating income, net income, diluted EPS — with sequential (QoQ) and year-over-year (YoY) growth rates.

**Tool calls**: `get_company_financials/{ticker}`, `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss"], fiscal_year=[latest], fiscal_period=[latest])`

**Output**: Consolidated P&L table with QoQ and YoY growth rates. Citation format: `{ticker} {citation_id} page<N>`.

### Mode: margin-analysis (essentials)

**Display name**: Margin Analysis

**Objective**: Track gross margin, operating margin, and net margin across the most recent 4 quarters. Identify trends, inflection points, and drivers (pricing power, cost structure changes, operating leverage).

**Tool calls**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","NetIncomeLoss"], fiscal_year=[latest, latest-1])`

**Output**: Margin trend table with QoQ deltas. Commentary on margin drivers.

### Mode: earnings-vs-consensus

**Display name**: Earnings vs. Consensus

**Objective**: Compare actual EPS against consensus estimates for the most recent quarter. Present surprise %, beat/miss track record (trailing 4 quarters), and guidance accuracy.

**Tool calls**: `search_earnings_calendar(ticker, fiscal_year=[latest, latest-1])`

**Output**: EPS actual vs. estimated table with surprise % and beat/miss streak.

### Mode: sequential-growth

**Display name**: Sequential Growth Analysis

**Objective**: Compute quarter-over-quarter growth rates for revenue, gross profit, operating income, and EPS across the trailing 4 quarters. Highlight accelerating or decelerating trends.

**Tool calls**: `search_xbrl_facts(ticker, concept=["Revenues","GrossProfit","OperatingIncomeLoss","EarningsPerShareDiluted"], fiscal_year=[latest, latest-1])`

**Output**: Sequential growth rate table with trend arrows and inflection detection.

### Mode: forward-outlook

**Display name**: Forward Outlook & Guidance

**Objective**: Extract management guidance for the upcoming quarter, upcoming earnings date, consensus estimates for next quarter, and key catalysts (product launches, regulatory events, earnings announcements).

**Tool calls**: `search_earnings_calendar(ticker, upcoming=true)`, `get_company_financials/{ticker}` (for guidance narrative)

**Output**: Forward outlook summary with guidance, consensus, upcoming catalysts, and earnings date.
