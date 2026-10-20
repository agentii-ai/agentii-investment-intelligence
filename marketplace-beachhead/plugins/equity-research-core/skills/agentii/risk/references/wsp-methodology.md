# risk -- Financial Report Risk Analysis Protocol

Institutional methodology for extracting risk signals from SEC filings. Applied to risk factor assessment, off-balance-sheet detection, covenant stress testing, pension analysis, contingency evaluation, and going concern assessment.

## Protocol

### Risk Factor Analysis: Signal vs. Boilerplate

Item 1A lists risks that are overwhelmingly generic--designed for SEC compliance and litigation protection, not investor insight. Apply three filters to each risk factor:

**Specificity test.** Does the risk cite company-specific metrics, contract terms, customer concentrations, or geographic exposures? If the same language could appear in any competitor's 10-K, classify as boilerplate.

**Financial statement mapping test.** Can the risk be traced to a specific FS line item? A raw materials cost risk must be matched against COGS composition in the footnotes. A foreign exchange risk must map to geographic revenue disclosure. Risks without a financial statement anchor are unactionable.

**Historical materialization test.** Has this risk produced actual financial impact in prior periods? Cross-reference the MD&A for evidence. A risk disclosed annually but never materializing is either effectively hedged or overstated.

Genuine risks passing all three filters demand quantified scenario analysis. Companies burying specific risks within boilerplate language signal reduced management transparency.

### Off-Balance-Sheet Liability Detection

Reported debt is only one portion of total obligations. Off-balance-sheet liabilities can exceed on-balance-sheet debt by a material multiple.

**Operating lease capitalization.** Extract future minimum lease payments from the lease footnote. Discount to present value using the company's incremental borrowing rate (approximated from the debt footnote's weighted-average interest rate). Add to reported debt. Recalculate all credit ratios with and without capitalized leases--the impact frequently exceeds one full turn of leverage; for retailers and airlines, three or more turns.

**Purchase commitments.** Aggregated supply-chain obligations (Apple disclosed $18.6B in manufacturing and component commitments) are not legal debt but represent fixed cash outflows that compete with debt service. Size total commitments against annual CFFO.

**Unconsolidated entities.** When companies consolidate subsidiaries differently for management reporting than GAAP, the Corporate segment reconciliation in the segment footnote reveals the magnitude of noncontrolling interest adjustments and entity-level obligations not reflected in consolidated debt.

### Debt Covenant and Default Risk Assessment

**Revolver borrowing base.** Calculate current headroom: maximum borrowing capacity (typically 85% of eligible receivables plus 85% of inventory liquidation value) minus drawn amount. Track quarterly--a declining borrowing base reduces liquidity even without incremental draws.

**Maturity wall identification.** Construct a year-by-year principal repayment timeline from the debt footnote. Flag any year where maturities exceed 50% of annual CFFO. A concentrated maturity wall exposes the company to refinancing risk external to its control.

**Weighted-average interest rate trajectory.** Track year-over-year against the risk-free rate. A rising weighted-average rate when benchmarks are flat signals deteriorating credit quality priced into new issuances.

**Covenant breach scenarios.** For each material covenant, calculate the EBITDA decline required to trigger breach. Compare that buffer to historical EBITDA volatility. A covenant with only 15-20% headroom against normal-cycle variance is a live risk.

### Pension Liability Analysis

**Funded status.** The pension footnote discloses PBO, plan assets, and funded status. An underfunded pension is debt-like: the company must contribute cash to close the gap. Size the shortfall against total debt and EBITDA.

**Assumptions sensitivity.** Test a 50-basis-point adverse move in the discount rate (increases PBO), expected return on plan assets (increases reported expense), and healthcare cost trend rate (increases OPEB obligation). Companies using aggressive assumptions--discount rates materially above AA corporate bond yields, or expected returns above long-term historical equity returns--are systematically understating pension burdens.

**OPEB.** Retiree healthcare obligations typically have no dedicated asset pool and are entirely unfunded, making them more debt-like than pension obligations. Aggregate pension underfunding plus OPEB for total retirement-related leverage.

### Contingency Disclosure Interpretation

GAAP classifies contingencies as probable/estimable (accrued), reasonably possible (disclosed only), or remote (not disclosed). Analytical value lies almost entirely in the "reasonably possible" category.

**Probability-weighted expected loss.** Construct: sum of (probability_i * loss_i). Compare expected value against cash balance and annual CFFO. A 20% probability of a $500M loss against $200M CFFO is thesis-level risk regardless of the most likely outcome.

**Management framing skepticism.** Disclosure is legally protected by safe harbor provisions, creating an incentive to present worst-case scenarios while arguing unlikelihood. Independently assess legal merits. Apple disclosed a $368M patent verdict without accrual, citing its belief in valid defenses--the analyst must evaluate the legal basis, not accept management's characterization.

**Pattern recognition.** New contingencies signal emerging risk. Contingencies growing in estimated magnitude over successive periods signal deteriorating prospects. Disappearing contingencies without resolution disclosure require investigation.

### Going Concern Evaluation

**Liquidity runway.** Divide total available liquidity (cash + undrawn revolver) by quarterly cash burn (CFFO minus maintenance capex minus mandatory debt service). Under four quarters requires imminent improvement or financing. Under two quarters is existential.

**Financing access.** Examine the cash flow statement for recent capital market access. Companies with declining-price equity issuances or rising-spread debt issuances face deteriorating conditions. A capital raise more than 12 months old may not be replicable.

**Consumption classification.** Distinguish growth investment cash consumption (capex exceeding D&A, working capital supporting revenue) from negative unit economics (gross margin insufficient to cover opex). The former is sustainable with financing; the latter is terminal without business model reset.

**Integrated stress scenario.** Combine covenant breach trigger, adverse contingency outcome, and pension contribution requirement into a single worst-plausible 12-month model. If survival requires external rescue, flag going concern risk.
