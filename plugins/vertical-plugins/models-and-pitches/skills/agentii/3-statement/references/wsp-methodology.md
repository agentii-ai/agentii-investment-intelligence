# 3-Statement Financial Model: Build Protocol and Methodology

## Protocol

1. **Input Historical Data**: Populate three years of actuals (IS, BS, CF) from SEC filings. Source line items from the 10-K: income statement from Item 8, balance sheet from Item 8, supplemental data (capex, depreciation related to PP&E, dividends, repurchases, weighted-average interest rates) from footnotes and MD&A. Cross-reference the statement of shareholders' equity for dividend and repurchase activity.

2. **Forecast the Income Statement**: Begin forecasting with revenue growth as the primary driver. Project revenue using `previous year revenue x (1 + revenue growth rate)`. Derive gross profit as `revenue x gross margin assumption`. Project R&D and SG&A as percentages of revenue. Interest income and interest expense are referenced from debt/cash schedules (do not hardcode). Tax expense equals `pretax profit x tax rate assumption`. Depreciation & amortization references the D&A schedule. EBITDA is calculated as `EBIT + D&A`; adjusted EBITDA adds stock-based compensation, which is grown in line with revenue.

3. **Forecast the Balance Sheet**: Forecast current assets and liabilities using income-statement-linked drivers. Accounts receivable, other current assets, deferred revenue, and other current/non-current liabilities grow in line with revenue growth. Inventories and accounts payable grow in line with cost of sales growth. Property, plant & equipment references the PP&E schedule. Cash references the net change in cash from the cash flow statement. Long-term debt is held constant (straight-line assumption). Common stock increases by stock-based compensation. Retained earnings references the retained earnings schedule. Other comprehensive income is held constant.

4. **Derive the Cash Flow Statement**: Use the indirect method. Start with net income. Add back D&A and stock-based compensation. Adjust for working capital changes: subtract increases in working capital assets (AR, inventory, prepaids), add increases in working capital liabilities (AP, accrued expenses, deferred revenue). For other non-current assets, reference the supporting schedule and include only additions as an outflow. Capital expenditures reference the PP&E schedule. Financing activities include long-term debt issuance/repayment, revolver draws/paydowns, share repurchases, and dividends.

5. **Address Circular Reference Issues**: Interest income depends on average cash balances; interest expense depends on average debt balances; cash and debt balances depend on net income, which depends on interest. Enable iterative calculation in Excel (Alt+T+O > Formulas > Enable iterative calculation). Insert a circularity breaker toggle: a cell switch (1=off, 0=on) with `=IF(toggle=1, AVERAGE(BOP, EOP) x rate, 0)` wrapping all circular interest calculations. Use `=IF($D$7=1, AVERAGE(F45,G45)*G155, 0)` for interest income and an analogous structure for interest expense.

6. **Scenarios and Sensitivity Analysis**: Build data tables for key output metrics (EPS, EBITDA, levered free cash flow) against input drivers (revenue growth, margin assumptions, tax rate). Use Excel's Data Table functionality (Alt+D+T). Implement scenario-switching via a dropdown selector that swaps entire assumption blocks.

## Key Formulas

**Revenue Build (Price x Volume)**:
- Revenue per product = Units x Average Selling Price
- Revenue growth rate = (Current Year / Prior Year) - 1
- For non-hardware segments (Services, Other): analyst estimates through year T+2, then straight-line growth rate

**Income Statement**:
- Revenue_t = Revenue_{t-1} x (1 + GrowthRate_t)
- Gross Profit = Revenue x GrossMargin_t
- Cost of Sales = Revenue - GrossProfit (plug; not independently forecast)
- R&D_t = Revenue_t x R&DPercent_t
- SG&A_t = Revenue_t x SG&APercent_t
- EBIT = GrossProfit - R&D - SG&A
- Pretax Profit = EBIT + InterestIncome - InterestExpense - OtherExpense
- Tax = PretaxProfit x TaxRate_t
- Net Income = PretaxProfit - Tax
- EBITDA = EBIT + D&A
- Adjusted EBITDA = EBITDA + StockBasedCompensation
- StockBasedCompensation_t = StockBasedCompensation_{t-1} x (1 + RevenueGrowth_t)

**PP&E Schedule (Roll-Forward)**:
- PP&E_EOP = PP&E_BOP + Capex - Depreciation
- PP&E_BOP_t = PP&E_EOP_{t-1}
- Depreciation_{PP&E} comes from the depreciation waterfall, not a simple ratio
- D&A_NotPP&E = Revenue x D&APercentOfRevenue (straight-lined at last historical year percent)

**Depreciation Waterfall (Vintage Method)**:
- Dep from Existing PP&E: `=DDB(NetPP&E_excl_land, salvage, useful_life, period, [factor])` with declining balance
- Dep from Capex Vintage Y: `=MidyearAdj x Capex_Y / UsefulLife`
- Midyear adjustment factor: 0.5 (assets purchased mid-year earn half-year depreciation in year 1)
- Typical useful life assumption: 8.0 years
- Net PP&E (excl. land) = Gross PP&E - Non-depreciable PP&E (land) - Accumulated Depreciation
- Total D&A = Sum of depreciation from existing PP&E plus each capex vintage
- Capex-to-Depreciation ratio: >1 for high-growth companies; converges to ~1 for mature businesses

**Interest Calculations (Circularity-Aware)**:
- InterestExpense_Revolver = WtdAvgRate_CP x AVERAGE(Revolver_BOP, Revolver_EOP)
- InterestExpense_LTD = WtdAvgRate_LTD x AVERAGE(LTD_BOP, LTD_EOP)
- InterestIncome = WtdAvgRate_Cash x AVERAGE(Cash_BOP, Cash_EOP)
- Total Interest Expense = InterestExpense_Revolver + InterestExpense_LTD
- All wrapped in circularity breaker: `=IF(CircBreak=1, AVERAGE(BOP,EOP) x Rate, 0)`

**Revolver (Model Plug)**:
- Cash Available (Needed) = Cash_BOP - MinCashBalance + CurrentPeriodCFs_excl_Revolver
- CurrentPeriodCFs_excl_Revolver = CFO + CFI + CFF excluding revolver activity
- MinCashBalance: set to $50,000 or approximately 2% of revenue
- Draw / (Paydown) = `=MIN(BOP_Balance, Cash_Available)` for surplus; draws equal the deficit amount
- Additional Discretionary Draw: user-input assumption (hardcoded, e.g., $12,000)
- Revolver_EOP = Revolver_BOP + Draw/(Paydown) + DiscretionaryDraw
- Surplus waterfall: first pay down revolver, then accumulate excess as cash
- Deficit path: borrow from revolver, reflected as CFF inflow

**Balance Sheet Line Drivers**:
- Accounts Receivable_t = AR_{t-1} x (1 + RevenueGrowth_t)
- Inventory_t = Inventory_{t-1} x (1 + COGS_Growth_t)
- AP_t = AP_{t-1} x (1 + COGS_Growth_t)
- Cash_EOP = Cash_BOP + NetChangeInCash (from CF statement)
- Balance Check: `=ROUND(TotalAssets - TotalLiabilities - TotalEquity, 3)` must equal zero

**Retained Earnings (Roll-Forward)**:
- RE_EOP = RE_BOP + NetIncome - Dividends - Repurchases
- Dividends: straight-lined at last historical year dividend amount
- Repurchases: straight-lined at last historical year repurchase amount
- Common Stock_EOP = Common Stock_BOP + StockBasedCompensation

**Working Capital Schedules (Roll-Forward)**:
- AR_EOP = AR_BOP + CreditSales - CashCollections
- DSO = AR / (Revenue / 365)
- Inventory_EOP = Inventory_BOP + Purchases - COGS
- AP_EOP = AP_BOP + Purchases - CashPaid
- DPO = AP / (COGS / 365)

**Cash Flow Statement (Indirect Method)**:
- CFO = NetIncome + D&A + SBC - IncreaseInWCAssets + IncreaseInWCLiabilities + OtherAdjustments
- CFI = -Capex (referencing PP&E schedule)
- CFF = LTD_Change + Revolver_Change - Repurchases - Dividends
- Net Change in Cash = CFO + CFI + CFF

**Operating Metrics**:
- Net Operating Cycle (Cash Conversion Cycle) = DSO + DIO - DPO

## Practitioner Standards

**Model Structure**: Use many shorter, modular worksheets rather than one long sheet. Dedicated tabs for each schedule: IS inputs, BS, CF, PP&E, working capital, debt/interest, retained earnings, revolver. Cluster all assumptions together in a dedicated input section at the top of the model; never scatter hardcoded values through formulas.

**Formatting Conventions**: Blue font or blue shading for input/hardcoded cells. Black font for formulas. Green text for validation checks (e.g., "OK" indicators). Red text or parentheses for negative values. Bold for subtotals and totals. All values in thousands except per-share data.

**Time Periods**: Investment banking models use annual periods; equity research models use quarterly. Fiscal years must match the company's reporting calendar (e.g., Apple's fiscal year ends the last Saturday of September). Always label columns with both fiscal year designation (e.g., "2019P") and exact period-end date.

**Assumption Sourcing**: Rely on sell-side consensus estimates for near-term forecasts (years T+1 through T+2 or T+3), then straight-line the terminal assumption. Revenue build uses consensus estimates through year T+2, then straight-line units and ASP thereafter. Tax rate uses analyst estimates through year T+2, then straight-line. The D&A-to-PP&E percentage uses a step-function increase toward a terminal rate (e.g., +2.0% per year toward ~80%).

**Validation**: Every period must pass `Total Assets = Total Liabilities + Total Equity` to within rounding tolerance. Debt balance row must show "OK" for all periods. Depreciation waterfall must reconcile to total D&A on the income statement. Retained earnings schedule must match the balance sheet line. The balance check formula `=ROUND(TotalAssets - TotalLiabilities - TotalEquity, 3)` must show zero.

**Circularity Management**: Always include a circ breaker toggle. Models must run with iterations disabled (circ breaker off) for faster audit and debugging, then enable for final outputs. Never ship a model that depends on iterative calculation to converge without a tested manual breaker.

**Data Sources from Filings**: Gross PP&E, non-depreciable PP&E (land), and accumulated depreciation from the PP&E footnote (typically 10-K Item 8, Note for property, plant and equipment). Dividends and repurchases from the statement of shareholders' equity. Weighted-average interest rates on commercial paper from the debt footnote; on cash from the Other Income/Expense disclosure in MD&A.

**Error Proofing**: Save frequently and maintain versioned copies. After completing each section, check that the balance sheet balances before proceeding. Build a visible balance check row. Use the `ROUND(..., 3)` function to avoid floating-point false positives that cause phantom imbalances.

**Model Usability**: Build models that are usable in the builder's absence. Document every formula in an adjacent comments column. Keep logic transparent; do not bury complex logic in nested IF statements without annotation. Even if no revolver currently exists, always build the revolver mechanism into the model to handle possible future cash shortfalls.

## Data Integration

The model integrates data from multiple sources along a staged pipeline:

**Historical Actuals**: Direct extraction from 10-K filings. Income statement line items from the audited financial statements. Balance sheet from the consolidated balance sheet. Supplemental data (capex, depreciation specifically from PP&E, dividends, repurchases) from the footnotes and statement of shareholders' equity. Weighted-average interest rates on commercial paper from the debt footnote; on cash from the Other Income/Expense disclosure.

**Consensus Estimates**: Near-term revenue growth, margin assumptions, and unit forecasts from sell-side research. These cover years T+1 through T+2 (or T+3). Beyond that window, all assumptions straight-line at the terminal year value.

**Scenario Inputs**: A scenario selector (Base / Bull / Bear) that toggles between alternative assumption blocks. Revenue growth, gross margin, R&D%, SG&A%, and tax rate are sourced from the selected scenario. All other assumptions remain common across scenarios.

**Integration Points with Schedules**: Revenue from a separate revenue build (Price x Volume analysis) feeds the income statement top line. PP&E and depreciation from the PP&E waterfall schedule feed both the balance sheet and income statement. Interest schedules draw from revolver and long-term debt balances. The revolver schedule draws from the cash flow statement and feeds back to the balance sheet. Retained earnings flows from the income statement through to the balance sheet equity section.

## Output Structure

The model produces a fully linked, five-year projection across the three core statements and supporting schedules:

**Sheet 1 - Income Statement**: Revenue through adjusted EBITDA, with growth rates and margins table directly below showing assumption drivers. A comments column documents every formula.

**Sheet 2 - Balance Sheet**: Assets, liabilities, and equity with a visible balance check row (`Total Assets - Total Liabilities - Total Equity = 0`). Each line item references its driver schedule.

**Sheet 3 - Cash Flow Statement**: Operating, investing, and financing sections in indirect format. Net change in cash ties to the balance sheet cash line. CFO sums reference individual line items: `=CFO_line1 + CFO_line2 + ...`

**Sheet 4 - PP&E Schedule**: Roll-forward with depreciation waterfall. Input data from 10-K footnotes (gross PP&E, land, accumulated depreciation). Depreciation calculated by vintage using DDB for existing assets and straight-line with midyear convention (factor 0.5) for new capex. D&A not related to PP&E is broken out and driven by revenue.

**Sheet 5 - Working Capital Schedules**: AR, inventory, and AP roll-forwards with DSO, DIO, DPO, cash conversion cycle, current ratio, and quick ratio metrics.

**Sheet 6 - Retained Earnings Schedule**: BOP + Net Income - Dividends - Repurchases = EOP. Links to balance sheet equity section.

**Sheet 7 - Debt and Interest Schedules**: Revolver needs analysis, commercial paper/revolver schedule, long-term debt schedule, cash/interest income schedule. All interest calculations use average of beginning and ending balances with circularity breaker wrapping.

**Sheet 8 - Revenue Build (optional)**: Price x Volume decomposition by product segment. Units forecast x ASP forecast per product line. Non-hardware segments projected via growth rates. Feeds revenue growth rate into the income statement.

**Sheet 9 - Scenarios and EPS**: EPS calculation (Net Income / Diluted Shares Outstanding). Sensitivity data tables. Scenario selector dropdown and assumption matrix.

## Advanced Accounting Supplements

### Protocol Bridge: From Advanced Accounting to the 3-Statement Model

### Step A1: Integrate Deferred Tax Accounting into the Model
The tax expense on the GAAP income statement comprises two components: cash taxes paid to tax authorities and deferred tax assets/liabilities from temporary book-tax timing differences. When constructing the 3-statement model, the income statement records the total GAAP tax provision, but the cash flow statement must isolate the cash component. An increase in DTL means GAAP tax expense exceeds the real cash obligation -- add the change back in CFO. An increase in DTA means the opposite -- subtract it from CFO. The balance sheet carries DTA and DTL as separate line items (not netted), requiring the model to track both individually. For projections, forecast the tax-basis depreciation schedule separately from book depreciation and compute the period-by-period DTL/DTA balances. Link these to the CFS via the year-over-year change.

### Step A2: Handle SBC in All Three Statements
Stock-based compensation is recognized on the income statement as a non-cash compensation expense. On the cash flow statement, SBC is added back to net income in the operating section (like depreciation). On the balance sheet, the offsetting entry increases additional paid-in capital within shareholders' equity. When the model projects SBC, grow it with headcount or as a percentage of revenue. Ensure the CFS add-back ties to the I/S expense, and the balance sheet APIC increase matches the I/S expense plus any option exercise proceeds. If the model uses a non-GAAP income statement that excludes SBC, do NOT add SBC back again in the CFS -- that constitutes double-counting and will cause the balance sheet to not balance.

### Step A3: Model Equity Method Investments Correctly
For 20-50% owned investments, the equity method applies: the investment is recorded as a single asset on the balance sheet. The investor's proportionate share of the investee's net income flows through the income statement (often as "equity in earnings of affiliates"), and the investment asset increases. Dividends received from the investee reduce the investment asset and appear as cash inflows in CFI or CFO. In the 3-statement model, if the investee's earnings are included in operating income, ensure dividends received are not also counted in revenue. The deferred tax liability on undistributed earnings of equity-method investees must be tracked on the balance sheet.

### Step A4: Consolidate Majority-Owned Subsidiaries
When ownership exceeds 50%, the consolidation method replaces the equity method. Every line item of the subsidiary's balance sheet and income statement is combined with the parent's. Non-controlling interest (NCI) is created in the equity section, representing the minority shareholders' claim. On the income statement, net income is split between "Net income attributable to parent" and "Net income attributable to NCI." In the model, build a separate consolidation schedule that eliminates the parent's investment account against the subsidiary's equity, records the excess as goodwill or a bargain purchase gain, and computes NCI as (1 - ownership %) x subsidiary equity at each period-end.

### Step A5: Handle OID/OIP in the Debt Schedule
Original issue discount debt requires the effective interest method in the debt schedule. Each period, interest expense equals the carrying value times the implicit rate at issuance. The difference between this calculated interest and the actual coupon payment (if any) adjusts the debt carrying value on the balance sheet. For OID (zero-coupon or below-par issuance), carrying value increases each period until it reaches par at maturity. For OIP (above-par issuance), carrying value decreases. On the CFS, the non-cash amortization portion is a non-cash add-back; only the coupon payment (if any) affects cash. The deferred tax implications of OID/OIP must also be modeled: the tax deduction often follows the coupon payment schedule, while book interest follows the effective interest method, creating temporary differences.

### Step A6: Incorporate Lease Accounting (ASC 842 / IFRS 16)
Under current standards, all long-term leases create a right-of-use asset and a lease liability on the balance sheet. For operating leases: straight-line rent expense on the I/S, with all cash flows in CFO. The ROU asset amortizes by the difference between straight-line rent and imputed interest. For finance leases: amortization expense (operating) plus interest expense (non-operating) on the I/S; the interest portion in CFO and the principal portion in CFF. In the 3-statement model, build a lease schedule that tracks the ROU asset amortization and lease liability reduction separately. Link the I/S rent/amortization plus interest to the schedule, the CFS add-backs to the non-cash components, and the balance sheet ROU/liability balances to the schedule's ending balances. When forecasting new leases, capitalize the PV of committed future payments using the incremental borrowing rate.

## Key Formulas (Advanced Accounting)

- **DTL at any year**: (Book Basis - Tax Basis) x Tax Rate
- **CFO Adjustment for Deferred Taxes**: +(Increase in DTL) - (Increase in DTA)
- **Equity Method Investment, End**: Investment_BOP + Proportional Net Income - Dividends Received
- **OID Carrying Value**: Carrying Value_BOP + (Implicit Rate x Carrying Value_BOP) - Coupon Payment
- **NCI**: (1 - Ownership %) x Subsidiary Equity
- **ROU Asset Amortization (Operating Lease)**: Straight-Line Rent Expense - Imputed Interest on Lease Liability

## Accounting Foundation Supplement

### Protocol: Debit/Credit Framework in Model Construction

The double-entry system is not merely a bookkeeping convention -- it is the structural integrity mechanism that keeps the 3-statement model internally consistent. Every transaction records both a source of funds (credit) and a use of funds (debit). In modeling terms: credits increase liabilities, equity, and revenue; debits increase assets and expenses. This source-use equivalence is what guarantees Assets = Liabilities + Equity. When building a model, tracing each line item through its debit/credit impact reveals inter-statement linkages: revenue recognition (credit retained earnings, debit AR or cash), inventory procurement (debit inventory, credit AP or cash), depreciation (debit retained earnings via expense, credit accumulated depreciation), and debt issuance (debit cash, credit long-term debt). The working capital roll-forward -- AR (BOP + credit sales - cash collections), inventory (BOP + purchases - COGS), AP (BOP + purchases - cash paid) -- is a direct expression of the debit/credit flow through balance sheet accounts. A model that balances is a model where total debits equal total credits in every period; an imbalance signals a missing entry.

### Revenue Recognition: Model-Build Implications

Two advanced recognition patterns directly affect model architecture. First, the percentage-of-completion method for long-term contracts: revenue is recognized proportionally to work completed, requiring the model to track cumulative costs incurred against total estimated costs, with period revenue as `(costs incurred / total estimated costs) x contract value - prior period recognized revenue`. The balance sheet carries an asset (costs in excess of billings) or liability (billings in excess of costs). Second, multiple-element arrangements: bundled products require allocation of total consideration to each deliverable based on standalone selling price. Apple's iPhone sale allocates $25 of the $499 price to unspecified software upgrade rights, deferring that $25 as a deferred revenue liability recognized ratably over the service period. In the model, split each sale into immediate-recognition revenue and deferred revenue, build a deferred revenue roll-forward schedule (BOP + new deferrals - recognized revenue = EOP), and project the recognition pattern over the expected service life. Revenue manipulation risk concentrates at the recognition boundary -- channel stuffing (accelerating shipments before period-end), bill-and-hold arrangements, and side agreements that alter standalone selling price allocations.

### Inventory Costing: Projection Impact of Method Choice

In rising input-price environments, method choice produces divergent P&L and balance sheet outcomes. LIFO: higher COGS, lower gross profit, lower taxable income, and lower ending inventory (valued at oldest costs). FIFO: lower COGS, higher gross profit, higher taxes, and higher ending inventory (valued at newest costs). The LIFO Reserve -- disclosed in footnotes -- bridges the two: `LIFO Inventory + LIFO Reserve = FIFO Inventory`, and `FIFO COGS + Change in LIFO Reserve = LIFO COGS`. For cross-company comparability, LIFO-company COGS must be adjusted downward by the reserve change. In projections, if modeling a LIFO company, forecast the LIFO reserve as a function of inventory growth and input price inflation, then convert to FIFO-equivalent metrics for peer benchmarking. IFRS prohibits LIFO, so US-IFRS comparisons require explicit LIFO-to-FIFO conversion. The lower-of-cost-or-market rule creates asymmetry: inventory write-downs flow through COGS immediately, but upward reversals are prohibited under GAAP (allowed under IFRS up to original cost). A model should incorporate a write-down trigger tied to market price thresholds.

### Depreciation Methods: Advanced Modeling

Beyond the ubiquitous straight-line method (`(cost - salvage) / useful life`), three accelerated methods alter both the expense timing profile and the deferred tax computation. Double-declining balance: annual depreciation = `(2 / useful life) x net book value at BOP`, ignoring salvage until the final year when depreciation is capped at `NBV - salvage`. This front-loads expense relative to straight-line, reducing early-period taxable income and creating DTL. Sum-of-years-digits: depreciation fraction in year Y = `(remaining life) / [n(n+1)/2]`, where n is total useful life. Units-of-production: `(cost - salvage) x (actual units produced / total estimated units)`, matching expense directly to asset utilization. For model construction, the vintage depreciation waterfall (covered in the main Protocol) builds the most accurate picture: DDB on existing net PP&E, straight-line with midyear convention (0.5 factor) on each new capex vintage. The model must separately track book depreciation (for GAAP I/S) and tax depreciation (MACRS in the US) to compute period-by-period DTL creation and reversal.

### Working Capital Flow-Through Mechanics

Each working capital account serves a specific operational function, and its projection driver must match. Accounts receivable represents credit extended to customers; project via DSO (`AR / (Revenue/365)`) or as a percentage of revenue growth. Inventory represents goods awaiting sale; project via DIO (`Inventory / (COGS/365)`) or inventory turns. Prepaid expenses represent cash paid before benefit receipt; project as percentage of SG&A. Accounts payable represents trade credit from suppliers; project via DPO (`AP / (COGS/365)`). Accrued expenses represent obligations incurred but not yet settled -- wages, taxes, interest, litigation reserves; project as percentage of the associated expense line. Deferred revenue represents cash collected before service delivery; project as a function of new contract bookings and recognition rates, requiring a separate roll-forward schedule. The cash conversion cycle (`DSO + DIO - DPO`) translates operational efficiency directly into cash trapped or released. A model must capture the feedback loop: accelerating revenue growth increases AR, consuming cash; stretching payables releases cash but may signal supplier distress.

### Deferred Tax Mechanics in Model Builds

Book-tax temporary differences create deferred tax assets (DTA) and deferred tax liabilities (DTL) that must be individually tracked through the model. The primary driver is depreciation: tax depreciation (typically accelerated MACRS) exceeds book depreciation in early years, creating DTL equal to `(tax depreciation - book depreciation) x tax rate`. DTL reverses when book depreciation exceeds tax depreciation in later years. Other temporary differences: warranty reserves (DTA -- book expense before tax deduction), bad debt reserves (DTA), prepaid expenses (DTL -- tax deduction before book expense), and revenue recognition timing (DTA/DTL depending on direction). In the model, build a deferred tax schedule: forecast book depreciation and tax depreciation separately, compute the period difference, track the cumulative DTL/DTA balance, and feed the year-over-year change into the cash flow statement (`CFO adjustment = +increase in DTL - increase in DTA`). A valuation allowance must be assessed against DTA if future taxable income is insufficient to realize the benefit. The effective tax rate reconciliation (`GAAP rate vs. cash rate`) provides a diagnostic: persistent effective rates below statutory rates signal aggressive DTL creation that will eventually reverse.
