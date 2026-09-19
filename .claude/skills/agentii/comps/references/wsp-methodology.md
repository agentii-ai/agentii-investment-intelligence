# Trading Comps Methodology -- Institutional Best Practices

## Protocol

**Peer Selection.** Identify 5-10 publicly traded comparables using a dual-path approach: sector classification (industry, product mix, end-market exposure) combined with fundamentals screening (size, growth trajectory, margins, capital intensity). Business life cycle filtering is critical -- early-stage, growth, mature, and declining companies should not be mixed without explicit adjustment. The target company must be included in its own peer group; the intuition is that the market prices the sector correctly on average but can misprice individual names.

**Multiple Selection.** Compute multiples across three time horizons -- LTM (trailing), Year 1 Forward, and Year 2 Forward. Enterprise value multiples (EV/Revenue, EV/EBITDA, EV/EBIT) are analyzed alongside equity multiples (P/E, PEG). Use median for groups of five or more to limit outlier distortion; mean is acceptable for smaller groups without outliers. Weighting between LTM and forward multiples is context-dependent: forward multiples carry more weight when LTM contains material nonrecurring items or significant margin and growth rate shifts are expected. LTM serves as the baseline when results are clean and the company is in steady state.

**Calendarization.** All companies are normalized to a December 31 calendar year end before multiples are compared. The adjustment uses pro-rata allocation: calendar-year metric equals (months of FY1 falling in CY / 12 x FY1 consensus) plus (months of FY2 falling in CY / 12 x FY2 consensus). Without calendarization, cross-company comparisons across different fiscal year endings are meaningless.

## Key Formulas

```
Enterprise Value = Equity Value + Net Debt
Net Debt = Gross Debt + Noncontrolling Interests + Preferred Stock
           - Cash & Equivalents - Marketable Securities

Implied EV = Peer Median Multiple x Target Operating Metric
Implied Share Price = (Implied EV - Target Net Debt) / Diluted Shares Outstanding

LTM = Latest FY + Latest Interim Period - Prior Year Equivalent Interim Period
PEG = P/E Ratio / Long-Term EPS Growth Rate (%)

Diluted Shares (Treasury Stock Method):
  Net Dilution = Gross Options - (Gross Proceeds / Current Share Price)
  Only in-the-money options are included (exercise price < market price).

Normalized Operating Income = GAAP Op Income + Excluded Operating Expenses
Normalized Net Income = GAAP Net Income + Pre-Tax Adjustments - Tax Effect
Tax Effect = Sum of Taxable Adjustments x Marginal Tax Rate
```

## Practitioner Standards

**Non-GAAP Comparability Adjustments.** Three categories of items require exclusion before multiples are computed:

1. **Stock-Based Compensation.** Treated as a non-cash expense analogous to depreciation. In heavy-SBC industries (technology, biotech), it is universally excluded. The associated tax benefit must also be removed -- eliminating the expense is equivalent to pretending it never occurred.

2. **Nonrecurring Items.** Restructuring charges, severance, litigation settlements, gains/losses on asset sales, inventory write-downs, one-time CEO transition costs, acquisition and integration costs, purchase accounting adjustments, and amortization of acquired intangibles are stripped out. These are typically embedded within COGS, SG&A, or non-operating income on the GAAP income statement and disclosed only in footnotes or press release reconciliation tables.

3. **Industry-Specific Exclusions.** Oil and gas companies use EBITDAX to neutralize full-cost vs. successful-efforts exploration accounting. REITs use FFO/AFFO to add back D&A and gains on sale. Technology companies frequently exclude amortization of acquired intangibles and capitalized software development costs.

**Entry Convention.** Excluded operating expenses are entered as positive numbers; excluded income as negative. The tax effect is a separate line netting the tax shield impact of all taxable adjustments.

**Source Hierarchy.** Non-GAAP reconciliation is most reliably found in earnings press releases and conference call transcripts (retrieve via `search_documents(ticker={T}, form_type="earnings_call_transcript")` → `read_source_pages`; citation prefix `ect<N>`). SEC filings (10-K, 10-Q) embed adjustments within major expense categories with details only in footnotes.

**Statistical Output.** Report High, Low, Median, Mean, and Mean-excluding-target for every multiple across every time period. The Mean-excluding-target row detects when the target's own multiple skews the peer average.

**Valuation Matrix.** Implied share prices are calculated for Median, High, and Low scenarios across all multiples and time periods. Results feed into a football field floating bar chart where the "Lower Value" and "Column Value" segments use invisible fills and upper value labels are placed at "Inside Base" alignment. The Y-axis must be hardcoded to a fixed maximum.

## Data Integration

**Input Data Requirements.** For each peer company: market data (ticker, quarter dates, FYE, stock price), shares data (basic shares, options by tranche with strike prices, convertible securities), GAAP financials (full income statement for latest FY and interim quarters), non-GAAP exclusions (operating, non-operating, tax effect), forward estimates (revenue, EBITDA, EBIT, EPS for Year 1 and Year 2, plus long-term growth rate), and balance sheet items (ST/LT debt, noncontrolling interests, preferred stock, cash).

**Dynamic Output Architecture.** The output sheet uses VLOOKUP nested with MATCH: `IF(ISBLANK($A9),"",VLOOKUP(B9,Input!$A$6:$L$300,MATCH($A9,Input!$B$6:$L$6,0)+1,FALSE))`. This enables dropdown-driven company selection that automatically repopulates all financials and multiples. The target company always occupies the first data row.

**Workbook Structure.** Five tabs: Cover, Input, Output, Valuation Matrix, Football Field.

## Output Structure

**Financial Metrics Table.** Columns by time period -- LTM, Year 1 Forecast, Year 2 Forecast -- each with Revenue, EBITDA, EBIT, EPS. Supplementary columns: Market Cap, Enterprise Value, LT Growth Rate, Net Debt, Diluted Shares Outstanding.

**Valuation Multiples Table.** Matching structure: EV/Revenue, EV/EBITDA, EV/EBIT, P/E for each period, plus PEG. Statistical summary rows: High, Low, Median, Mean, Mean(excl. target), Target.

**Valuation Matrix.** For each scenario (Median, High, Low) and each multiple/time-period combination: Multiple x Target Metric = Enterprise Value, less Net Debt = Equity Value, divided by Shares Outstanding = Implied Share Price.

**Football Field Chart.** Six floating bars (LTM EV/Revenue, LTM EV/EBITDA, LTM EV/EBIT, LTM P/E, Year 1 EV/EBITDA, PEG) bracket the Low-to-High implied share price range, with current share price overlaid as a reference line.

## Industry-Specific Multiples

| Sector | Primary Multiple | Rationale |
|---|---|---|
| Technology | EV/Revenue, EV/EBITDA | Negative earnings tolerance; growth-stage prevalence |
| Financial Institutions | P/B, P/Tangible Book | Marked-to-market equity; asset-based valuation |
| Oil & Gas | EV/DACF, EV/EBITDAX | Neutralizes full-cost vs. successful-efforts exploration accounting |
| REITs | Price/FFO, Price/AFFO | D&A distorts real estate profitability |
| Internet (Pre-Revenue) | EV/Subscribers, EV/Website Hits | User base as monetization proxy; use with extreme caution |
| Asset-Intensive/Capital Goods | P/B, EV/EBIT | Capital intensity comparability; D&A differences material |

## Transaction Comps Supplement

### Protocol

**Deal Screening Criteria.** Precedent transaction selection follows a layered filtration process distinct from trading comp screening. Primary filters are industry classification (SIC or NAICS code of the target), transaction size (enterprise value, revenue, EBITDA floors), and recency (six-to-seven-year maximum lookback; deal premiums and multiples are acutely sensitive to the prevailing M&A cycle and deals older than this window produce stale multiples). A nominal transaction value floor ($5M is customary in middle-market screens) eliminates micro-deals that lack institutional relevance regardless of industry fit. Deal type is restricted to acquisitions/mergers and majority stakes; minority investments and spin-offs are excluded from the initial screen. Transaction status includes completed, pending, and canceled deals -- pending deals retain their agreed multiples absent a material adverse change clause, and canceled deals preserve the originally negotiated multiple as a market-clearing data point.

Secondary filters sharpen relevance when the raw screen produces excessive results: industry position, seasonality, cyclicality, capital structure leverage, and growth trajectory. The most powerful secondary technique is screening by acquirer name from the target's trading comp peer group -- a peer's past acquisition target is structurally more likely to operate in the same line of business than a random industry-code match. A revenue filter serves dual purpose: it ensures size comparability and automatically eliminates private deals with no financial disclosures in the database.

Three discovery paths operate in parallel: (1) colleague and internal comp sets from prior pitches or deals; (2) database screening via CapIQ, FactSet, Bloomberg, Thompson, or industry-specific platforms (SNL for financial institutions); (3) fairness opinions filed in S-4s or proxy statements (DEF 14A) of comparable transactions. Fairness opinions contain investment bank-compiled precedent transaction lists that frequently surface deals missing from database screens. S-1 registration statements -- when a peer has recently gone public -- serve as an additional discovery source, as they routinely catalog landmark industry acquisitions. Database-screen data must be verified against source SEC filings; databases are optimized for screening breadth, not data accuracy, and errors in deal terms or financials are common.

**Premium Analysis.** The control premium is calculated against the target's unaffected share price at three intervals: one day, one week, and one month prior to announcement. The one-day price is most commonly cited but is frequently contaminated by rumor-driven volume spikes; cross-referencing across all three horizons and monitoring trading volume for anomalous surges is essential. Control premiums typically range from 25% to 50%+ above standalone market value, with the distribution sensitive to credit cycles, equity market conditions, and competitive bidder dynamics. Strategic acquirers systematically pay higher premiums than financial buyers due to anticipated synergy extraction. Historical share prices for delisted targets are retained in paid databases (Bloomberg, FactSet) but are absent from free sources. When all databases fail, fairness opinions themselves frequently disclose the historical prices used in the premium calculation.

**Synergy Exclusion.** Transaction multiples embed the present value of expected synergies that strategic acquirers can extract -- cost reductions, revenue cross-sell, and tax benefits -- which is why transaction multiples structurally exceed trading multiples. Announced synergies are found not in the merger agreement itself but in the deal announcement conference call transcript (retrieve via `search_documents(form_type="earnings_call_transcript")`; CapIQ/FactSet if unavailable), press releases quoting management, or sell-side research reports. The presence of material synergy expectations directly inflates observed deal multiples; all else equal, comps with announced synergies must be contextualized against those without. Transaction multiples are therefore upper-bound valuation references, not intrinsic value indicators.

**Deal Structure and Transaction Value.** Form of consideration (all-cash, all-stock, or mixed) affects the observed multiple independently of target quality; stock consideration embeds the acquirer's own valuation and creates circularity in the multiple. Transaction value (TV) equals offer value plus assumed net debt, where net debt calculation requires explicit scrutiny of intercompany and affiliate balances -- affiliate debt that will be eliminated at closing must be excluded from net debt, as the acquirer neither assumes the liability nor receives the corresponding asset. Failure to identify intercompany eliminations produces material TV overstatement. Offer price per share and diluted share count are frequently undisclosed for private targets; in such cases, the disclosed aggregate offer value is entered directly via the override mechanism, and equity multiples (P/E) cannot be computed.

**Calendarization.** LTM financials = latest fiscal year + latest interim (stub) period - prior-year equivalent interim period. For public targets, the stub is the most recent 10-Q; for private targets, financials are embedded in the acquirer's 8-K filing (filed 4-12 months post-close) and the reporting date may not align perfectly with the announcement date -- the closest available period is used as a practical approximation. Fiscal-year forecasts (Year 1, Year 2) are sourced from equity research for public targets, from the proxy statement or fairness opinion projections when available, and are frequently unavailable for private targets, producing incomplete comps with only LTM multiples.

**Non-GAAP Normalization in Transaction Context.** Transaction comps demand consistent treatment of non-GAAP exclusions across all deals in the set. The technology sector convention of excluding stock-based compensation and amortization of purchased intangibles from EBIT creates a specific hazard: the D&A add-back to reach EBITDA must exclude the already-eliminated amortization component, or a double-count error occurs. For private targets without press-release reconciliation tables, the analyst must infer appropriate exclusions from industry convention and any footnote disclosures embedded in the acquirer's 8-K filing. The cross-check is arithmetic: the sum of individual D&A components from footnote disclosures must reconcile to the aggregate D&A figure on the cash flow statement.

**Handling Outliers.** Deals with extreme profitability divergence (targets with near-breakeven or negative margins versus profitable peers) produce multiples that are not directly comparable. The Enterasys transaction (0.5x LTM revenue, 6.8x LTM EBITDA versus peer medians of 2.0x and 9.8x) illustrates how low-margin targets trade at substantially compressed multiples that distort the mean. Such outliers should be flagged, excluded from headline statistics, and discussed separately as "related but not identical" comps. Median is the preferred central tendency measure; mean is reported but de-emphasized when dispersion is wide.

### Practitioner Standards

**Output Structure.** Comparable transaction analysis output aggregates target metrics (revenue, EBITDA, EBIT, EPS), transaction value, offer value, premiums paid, and computed multiples (TV/Revenue, TV/EBITDA, TV/EBIT, Offer Price/EPS) across LTM, Year 1 Forward, and Year 2 Forward periods. Statistical summary rows report High, Low, Median, Mean, and Mean-excluding-outlier for every multiple. A dropdown-driven output tab enables dynamic inclusion/exclusion of individual comps, allowing real-time assessment of each transaction's impact on the central tendency.

**Data Verification Protocol.** Every deal term and financial figure extracted from a database must be confirmed against the source SEC filing: announcement 8-K (deal terms), target 10-K/10-Q (historical financials), proxy statement or S-4 (forecasts and fairness opinion), and closing 8-K (finalized terms, which may differ from announcement terms). The announcement conference call transcript is the primary source for synergy expectations (`search_documents(ticker={T}, form_type="earnings_call_transcript")` → `read_source_pages` on the qa pages where management fields synergy questions). Deal status verification requires either a closing press release 8-K or confirmation in a subsequent 10-K/10-Q.
