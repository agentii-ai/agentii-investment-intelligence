# Non-GAAP Methodology for Valuation

## Protocol

### Step 1: Identify and Classify Non-GAAP Adjustments
Non-GAAP disclosures split broadly into two categories: non-recurring items and non-cash items. Non-recurring items under GAAP must meet the "unusual or infrequent" threshold, but most items appearing in non-GAAP reconciliations (restructuring expenses, asset impairments, gains/losses on sale, transaction fees, severance costs) do not formally qualify. The non-GAAP label gives companies substantial leeway beyond GAAP to present what they consider non-recurring. As a result, analyst scrutiny is essential.

For each non-GAAP adjustment disclosed, classify it as: (1) truly non-recurring and removable, (2) recurring but non-cash and requiring different treatment, or (3) a recurring operating item that should NOT be excluded. Restructuring charges appearing every year are not non-recurring -- they represent normal operating costs of a business undergoing continuous change. Companies that habitually identify non-recurring expenses signal low earnings quality and typically trade at compressed multiples, since analysts question the integrity of the denominator (EBIT, EBITDA, EPS).

### Step 2: Normalize EBITDA with the Top-Down Approach
Two methods exist for deriving normalized EBITDA. The bottom-up approach starts with GAAP net income and adds back individually identified non-GAAP items plus D&A. This is simpler but embeds GAAP line-item distortions and can misalign add-backs. The preferred top-down approach strips all non-GAAP items and D&A from each individual expense category (COGS, S&M, R&D, G&A) before summing to EBITDA. This forecasts EBITDA directly rather than via add-backs, reducing forecasting error. The cost: expense allocation assumptions are required when the company does not disclose which operating line contains each non-GAAP item. When forced to allocate, document the assumption (e.g., "unallocated depreciation assumed entirely in R&D") and test sensitivity.

### Step 3: Quantify SBC Dilutive Impact for Valuation
The debate on SBC treatment centers on whether it constitutes a genuine economic cost. The argument against adding back SBC holds that it represents a real transfer of value from existing shareholders to employees -- ignoring it overstates sustainable earnings. The argument for adding it back treats SBC as a non-cash expense analogous to D&A. Regardless of the income statement treatment, the dilutive impact on per-share metrics must be quantified: outstanding options and RSUs increase the fully diluted share count via the treasury stock method. When capitalizing SBC (e.g., for software development), the amortization of previously capitalized SBC flows through the I/S as a non-cash charge that must also be normalized. For valuation, present both GAAP EPS and adjusted EPS, clearly reconciling the share count and tax impacts.

### Step 4: Compute Non-GAAP Diluted Shares Correctly
Non-GAAP diluted shares typically equal GAAP diluted shares, but diverge in one critical scenario: when a net loss exists under GAAP but net income exists on a non-GAAP basis. Under GAAP, a net loss means diluted shares equal basic shares because including dilutive securities would be anti-dilutive (a loss divided by more shares produces a better result). However, if non-GAAP adjustments turn the loss into income, dilutive securities must be accounted for: non-GAAP diluted shares will exceed GAAP diluted shares.

A second divergence arises from convertible note hedging strategies. When a company issues convertible notes and simultaneously enters call option hedges, GAAP requires reflecting the dilution from the convertible feature without recognizing offsetting hedge shares until exercised. Companies may present non-GAAP diluted shares that net the hedge benefit, producing a lower share count than GAAP. Analysts should independently verify the hedge economics and determine which share count best reflects economic reality.

### Step 5: Treat Tax Impacts Consistently with Non-GAAP Adjustments
Each non-GAAP adjustment carries a tax effect. When excluding a pre-tax expense, also exclude the associated tax shield. The tax impact equals the non-GAAP item multiplied by the marginal tax rate. Companies with volatile effective tax rates often present a normalized tax rate reconciliation alongside non-GAAP earnings. When projecting non-GAAP earnings forward, apply a steady-state marginal rate rather than the historical volatile GAAP rate. Ensure the bridge from non-GAAP net income to GAAP net income explicitly shows: non-GAAP items (subtracted), plus the tax impact of those items (added back as a tax shield reversal).

### Step 6: Anchor Valuation Multiples to Normalized Metrics
Non-GAAP adjustments directly affect valuation multiples. If a company carries chronic "non-recurring" charges, normalized EBITDA will be lower than reported adjusted EBITDA, producing a higher effective multiple. Price the company on the normalized metric, not the management-adjusted figure. For companies with significant SBC, compute both EV/EBITDA (which ignores SBC dilution) and price-to-earnings on fully diluted, SBC-expensed EPS. The gap between the two signals how much value transfer is occurring through equity compensation. A wide gap warrants a discount to peer multiples.

## Key Formulas

- **Adjusted EBITDA (Top-Down)**: Revenue - COGS(ex-Non-GAAP, ex-D&A) - S&M(ex-Non-GAAP) - R&D(ex-Non-GAAP, ex-D&A) - G&A(ex-Non-GAAP)
- **Tax Impact of Non-GAAP Items**: Non-GAAP Pre-Tax Adjustment x Marginal Tax Rate (subtract from GAAP tax to get normalized tax)
- **Non-GAAP Diluted Shares (Loss-to-Income Case)**: Basic shares + dilutive securities (treasury stock method) -- GAAP diluted would equal basic shares
- **Normalized Net Income Bridge**: Non-GAAP NI - SBC - Amortization of Purchased Intangibles - Restructuring + Tax Shield on Excluded Items = GAAP NI

## Practitioner Standards

- Apply consistent exclusion criteria across periods. Cherry-picking only negative items while retaining positive non-recurring gains creates an upward bias in adjusted earnings.
- When non-recurring charges appear in 3+ consecutive years, reclassify them as recurring operating expenses regardless of management's characterization.
- Always compute the effective tax rate on non-GAAP pre-tax income using the normalized rate, not the GAAP rate distorted by valuation allowances and NOL adjustments.
- For the treasury stock method, use the average share price during the period, not the period-end price.
- Never double-count add-backs: if the income statement already excludes SBC and amortization (non-GAAP I/S), the CFS must not add them back again, or the model will not balance.
- Prefer the top-down EBITDA approach when company disclosures allow allocation; otherwise, use bottom-up but flag the uncertainty.

## Data Integration

This methodology leverages:
- **SEC Filings**: Earnings press releases (8-K Item 2.02) for non-GAAP reconciliations; 10-K footnotes for SBC valuation assumptions, lease commitments, and restructuring details
- **XBRL Facts**: `search_xbrl_facts()` for GAAP vs. non-GAAP line items; share count disclosures for diluted EPS calculation
- **Market Data**: Current share price for treasury stock method; peer multiples for earnings-quality discount assessment
- **Knowledge Base**: `search_investment_cases()` for precedent non-GAAP adjustment patterns by sector
