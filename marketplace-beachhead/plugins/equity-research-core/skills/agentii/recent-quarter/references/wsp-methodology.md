# recent-quarter -- 10-K Deep-Read and Financial Statement Protocol

Institutional buy-side workflow for extracting maximum analytical signal from SEC filings. Applied to quarterly earnings review, annual report analysis, and financial statement diligence.

## Protocol

### 10-K Deep-Read Sequence

The buy-side reads the 10-K in a specific, non-negotiable order. Each section is read with a distinct objective before the next begins, preventing quantitative data from coloring qualitative interpretation.

**Step 1 -- Business Overview (Item 1)**: Understand what the company sells, how it generates cash flow, and its segment structure. Read for structural understanding before any financial data enters the frame.

**Step 2 -- Risk Factors (Item 1A)**: Categorize each risk as genuine (thesis-impairing) or boilerplate. Flag risks that map to financial statement line items (wage inflation to margin, supply pressure to occupancy) for later cross-reference.

**Step 3 -- MD&A (Item 7)**: Management's narrative of results. Read for segment-level revenue and margin commentary, year-over-year driver explanations (volume versus price versus mix), forward-looking guidance, and what management chooses not to discuss. Silence on a deteriorating metric is as informative as commentary.

**Step 4 -- Financial Statements**: Only now, after absorbing qualitative context, examine the numbers. Build common-size statements (line items as percentage of revenue for the income statement; percentage of total assets for the balance sheet). Include both annual and quarterly data to capture inflection points that annual smoothing obscures.

**Step 5 -- Footnotes**: Read with targeted priorities. Not all footnotes are equal.

### Footnote Analysis Priorities

Rank-ordered by analytical yield:

1. **Revenue recognition**: Segment disaggregation, performance obligations, timing of recognition.
2. **Income taxes and EPS**: Tax rate reconciliation, deferred tax composition, valuation allowance sustainability. A company reporting GAAP losses while generating tax benefits requires scrutiny. EPS footnote provides authoritative diluted share count.
3. **PP&E and depreciation**: For asset-intensive businesses and serial acquirers, examine whether depreciation methodology or useful-life assumptions have changed over time. Benchmark against industry peers; demand explanation for divergence.
4. **Debt and capital structure**: Maturity schedule, interest rates, seniority, security, covenant compliance. Build a capital structure table with columns for instrument, maturity, senior/subordinated status, secured/unsecured, interest rate, principal outstanding.
5. **Leases and off-balance-sheet obligations**: Extract future operating lease commitments, discount to present value, add to reported debt. Recalculate all credit ratios with and without capitalized leases (Net Debt/EBITDA, Total Debt/EBITDA, Net Debt/(EBITDA - CapEx)). Lease capitalization can shift leverage by a full turn or more.
6. **Segment reporting**: Drill into segment-level revenue, operating income, and identifiable assets. Flag segments with insufficient cost-component disclosure as black-box risks.
7. **Commitments and contingencies**: Size each contingent liability against the balance sheet and cash flow capacity.

### Income Statement Analysis

**Common-size and trend**: For every line item: improving, deteriorating, or stable? Does the trend match management's narrative? Rank-order expenses by magnitude. For labor-intensive businesses, estimate minimum-wage sensitivity. When cost-component detail is undisclosed, flag for IR inquiry.

**Segment drill-down**: Identify key drivers per segment (e.g., occupancy, pricing) from the 10-K MD&A or industry reports. Track drivers individually across periods. Non-core segments require separate driver frameworks.

**Non-recurring audit**: Flag any charge appearing in every fiscal year. Recurring impairment is structural, not non-recurring.

### Balance Sheet and Cash Flow Analysis

**Common-size balance sheet**: Goodwill as percentage of assets requires write-down risk sizing. Debt trending upward signals deteriorating flexibility.

**Cash flow quality**: CFFO must derive from operations, not asset sales. Bridge net income to CFFO via non-cash charges.

**Sustainability test**: Compare CFFO to capex. Decompose capex into mandatory versus discretionary to size the structural shortfall.

### Earnings Analysis Workflow

1. Wait until after the earnings call to finalize valuation, or acknowledge pre-call numbers are stale.
2. After the call: update projections for occupancy, pricing, margin, and capex assumptions. Test sensitivity to revised estimates.
3. Cross-reference management's call commentary against the filed 10-Q/10-K: `search_documents(ticker={T}, form_type="earnings_call_transcript")` → `read_source_outline` → `read_source_pages` on the guidance/forward-looking pages (session_title=section_type, labels carry guidance/forward_looking). Divergences in emphasis between spoken and written record are analytically significant.
4. For opaque cost lines, initiate IR contact. Even without C-suite access, IR can often provide clarifying detail.

## Financial Report Deep-Read Supplement

Advanced institutional methodology for extracting maximum analytical signal from SEC filings, extending the base 10-K protocol with forensic techniques.

## Protocol

### MD&A Decomposition: Management Narrative vs. Financial Statement Reality

The MD&A is the only section where management speaks in its own voice about results. It operates simultaneously as a data source, a guidance mechanism, and a spin document. The analytical task is to isolate factual claims from interpretive framing.

**Read the MD&A before the financial statements.** The sequence matters: absorb management's framing first, then pressure-test it against the audited numbers. This prevents the numbers from anchoring your interpretation of management's claims.

**Decompose every margin bridge management provides.** Companies that provide detailed gross margin walkdowns--decomposed into pricing, mix, volume, manufacturing costs, commodity inputs, and foreign exchange--are signaling transparency. Companies that provide only directional commentary ("margins improved due to operational efficiencies") are signaling opacity. The P&G model decomposition--where gross margin is quantified as "+70 bps pricing, +160 bps manufacturing savings, -160 bps negative mix, -X bps commodities"--is the analytical gold standard. Demand this level of granularity.

**Identify what management does not discuss.** When a deteriorating metric receives no MD&A commentary while improving metrics receive extensive narrative, the silence is analytically significant. Cross-reference: if a line item moves materially on the income statement but the MD&A is silent, the omission is deliberate and requires follow-up.

**Flag every non-GAAP adjustment individually.** The MD&A is often the only filing location containing the full GAAP-to-non-GAAP reconciliation. For each adjustment, ask: is this genuinely non-recurring, or is it a recurring charge that management prefers to exclude? Impairment charges appearing every fiscal year are structural, not episodic. A restructuring program spanning five years with "in excess of $3.5 billion in costs" is not a one-time event--it is a business model feature.

**Extract forward-looking guidance from MD&A narrative, not just the guidance section.** Companies typically embed quantitative guidance (gross margin ranges, capex budgets, tax rate expectations) within the operating narrative, not in a separate labeled section. Apple disclosed first-quarter gross margin guidance of 36.5-37.5% in the middle of the gross margin discussion paragraph.

### Revenue Recognition Red Flags

Revenue recognition is the highest-analytical-yield footnote and the most common locus of accounting manipulation. The accounting policy footnote (typically Note 1) discloses how and when revenue is recognized--read it before examining any revenue trends.

**Multiple-element arrangements.** When a single transaction bundles hardware, software, services, and future upgrade rights, GAAP requires allocation of the total price across performance obligations. Apple defers $5-$25 per iPhone and $20-$40 per Mac for software upgrade rights, recognized straight-line over two to four years. The analytical implication: reported revenue understates cash collected in the current period, and the deferred revenue liability on the balance sheet represents future revenue already sold but not yet recognized. Track deferred revenue as a leading indicator--declining deferred revenue balances signal that future-period revenue recognition is being pulled forward.

**Bill-and-hold indicators.** When a customer is billed but the product has not shipped, revenue may be recognized prematurely. Red flags: significant increases in accounts receivable relative to revenue growth, material finished goods inventory held at period-end with corresponding receivables, or sudden changes in revenue recognition policy language regarding delivery terms.

**Channel stuffing detection.** Compare revenue growth against unit volume growth and average selling price changes. When revenue rises materially but unit volume and ASP are flat or declining, channel stuffing or aggressive recognition is the likely explanation. Apple's MD&A provides unit sales data alongside revenue by product--this disclosure format is analytically ideal because it enables independent decomposition of revenue changes into volume and price components.

**Contractual obligations and performance guarantees.** When revenue recognition depends on subjective judgment about completion milestones (common in construction, software, and long-term service contracts), flag year-over-year changes in the percentage-of-completion assumptions or warranty accrual rates. A reduction in warranty reserves as a percentage of revenue, without operational explanation, signals potential earnings management.

### Cash Flow Sustainability Tests

The income statement is an opinion; the cash flow statement is fact. The analytical objective is to measure the distance between the two and determine whether reported earnings are converting to cash.

**Operating cash flow vs. net income divergence analysis.** For mature, stable companies, CFFO should approximate net income plus depreciation and stock-based compensation. Apple and P&G demonstrate this: in any given year, net income + D&A comes close to total CFFO, because working capital swings largely cancel. When this relationship breaks--when CFFO materially diverges from net income after adjusting for D&A--decompose the gap into its working capital components.

**Working capital as an early-warning system.** Rising receivables relative to revenue signals customers are taking longer to pay. Rising inventory relative to COGS signals production is outpacing demand. Declining payables relative to COGS signals suppliers are tightening terms. Each component is independently diagnostic. Tesla's cash flow statement illustrates the growth-company dynamic: net loss of $74M converted to $257M in positive CFFO through a $463M inventory build (negative signal for demand), offset by a $268M deferred revenue increase (positive signal for pre-sales).

**Capex sustainability test.** Decompose capex into maintenance (required to sustain current operations) and growth (discretionary expansion). Maintenance capex should be fully covered by CFFO in any sustainable business. When maintenance capex alone exceeds CFFO, the business requires continuous external financing to survive--this is a structural deficit, not a cyclical one. Subtract total capex from CFFO to calculate free cash flow. P&G's free cash flow productivity ratio (FCF / net earnings) of 95% in 2013 vs. 85% in 2012 is the correct metric for tracking conversion quality over time.

**Non-cash adjustments audit.** Stock-based compensation, while non-cash, is a real economic cost to shareholders through dilution. Treat SBC as an expense for analytical purposes regardless of GAAP presentation. Deferred tax adjustments that inflate CFFO relative to tax-basis earnings must be scrutinized: a company generating large deferred tax assets from operating losses may never realize them if profitability does not materialize.
