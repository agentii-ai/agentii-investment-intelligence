# Advanced Accounting Methodology for DCF

## Protocol

### Step 1: Treat Deferred Taxes Correctly in UFCF
Unlevered Free Cash Flow must reflect the actual tax obligation, not the GAAP tax expense. Deferred tax assets (DTA) and liabilities (DTL) arise from temporary timing differences between book and tax accounting -- primarily from depreciation (straight-line for GAAP vs. MACRS for IRS), revenue recognition, and loss treatment. The DTL at any period equals (book basis minus tax basis of the asset) multiplied by the tax rate. These differences are temporary: both bases start and end at the same value, diverging only in interim periods.

For UFCF: an increase in DTL means the GAAP tax expense overstates the real tax obligation -- add it back to net income in the CFO section. Conversely, an increase in DTA means GAAP tax expense understates the real obligation -- subtract it. When projecting UFCF, forecast the tax basis separately from book depreciation and compute the period-by-period DTL/DTA change to derive cash taxes. Do not simply apply the effective tax rate to EBIT -- this embeds deferred tax distortions into your FCF.

### Step 2: Treat SBC as a Real Economic Cost
Stock-based compensation is a non-cash expense on the income statement, added back to arrive at CFO just like depreciation. However, for DCF purposes, SBC represents a real economic cost to existing shareholders through dilution. Most analysts in high-SBC industries exclude SBC from adjusted earnings. When doing so, also exclude the tax benefit from SBC (the reduced GAAP tax expense attributable to the SBC deduction). In the DCF, project future share count using the treasury stock method and discount to equity value per share.

### Step 3: Distinguish Equity Method from Consolidation
Ownership percentage dictates accounting method: 0-20% uses cost/market method (investments in securities), 20-50% uses the equity method, and 50%+ uses consolidation. Under the equity method, the investment is recorded as a single asset ("equity investment in affiliates") initially at acquisition price. The investor recognizes its proportional share of the investee's net income, increasing the investment asset. Dividends received reduce it. For consolidation: each target asset and liability is combined line-by-line into the acquirer's balance sheet. Non-controlling interest (NCI) is created as a separate equity line representing the portion not owned. In DCF, if modeling equity-method income, ensure it flows through the income statement but is not double-counted in operating projections.

### Step 4: Model OID/OIP Debt Correctly
Bonds issued below redemption price carry original issue discount (OID). Accrual accounting requires recognizing annual amortization expense (within interest expense on the I/S) over the life of the borrowing, with the offset increasing the carrying value of the debt. Amortization is calculated using the implicit discount rate. For zero-coupon bonds, the entire return to bondholders is this non-cash accrual. Bonds issued above redemption price (original issue premium, OIP) generate negative amortization that offsets cash interest expense. In the DCF, project the debt schedule using the effective interest method: interest expense equals carrying value times implicit rate, and the difference between this and the coupon payment adjusts the debt balance.

### Step 5: Apply Lease Accounting Standards (IFRS vs. GAAP)
Under US GAAP (ASC 842), leases are classified as finance or operating. IFRS 16 mandates a single finance-lease model. For both types, the lessee recognizes a right-of-use (ROU) asset and a lease liability (PV of future lease payments) on the balance sheet. Finance leases split the payment: amortization expense (operating) and interest expense (non-operating) on the I/S; CFO receives the interest portion while CFF receives the principal portion. Operating leases recognize straight-line rent expense entirely within CFO. In DCF, finance lease obligations are treated as debt; operating lease commitments should be capitalized and treated as debt-like obligations for enterprise value calculations.

### Step 6: Apply Stock vs. Asset Sale Tax Treatment (338(h)(10))
In an asset sale, the acquirer receives a step-up in tax basis on acquired assets, generating future tax deductions through higher depreciation. In a stock sale, assets remain at historical book value -- no step-up. The 338(h)(10) election allows a stock sale to be treated as an asset sale for tax purposes, preserving the step-up benefit while avoiding the legal complexity of transferring individual assets. Requirements: target must be a subsidiary or S-corporation, buyer must be a C-corp, election must be joint before deal close, and greater than 80% of stock must be purchased within 12 months. When building a DCF for an M&A scenario, model the PV of tax benefits from the basis step-up and adjust the purchase price allocation accordingly. Asset sales impose double taxation on C-corp sellers (corporate-level gain plus shareholder-level dividend tax), while stock sales tax only the shareholder gain. The acquirer's tax savings from step-up rarely fully compensate the seller for this double-tax burden.

## Key Formulas

- **DTL at any year**: (Book Basis - Tax Basis) x Tax Rate
- **OID Annual Amortization**: Implicit Rate x Carrying Value (effective interest method)
- **Basis Step-Up Value (Asset Sale)**: PP&E = Original BV + Allocated Excess; Intangibles/GW = Original BV + Remaining Excess
- **338(h)(10) Seller Proceeds (C-Corp)**: Stock Sale proceeds = $140M - 20% x ($140M - $100M outside basis) = $132M; Asset Sale proceeds = $140M - corporate tax on $60M gain at 40% = $116M - shareholder tax on $16M at 20% = $112.8M

## Practitioner Standards

- Always derive cash taxes from the tax books, not from GAAP tax expense. The gap between GAAP tax and cash tax is the change in net DTL/DTA.
- Treat SBC as dilution to existing shareholders in per-share valuation, even if added back in adjusted EBITDA.
- When consolidating for a DCF, eliminate intercompany transactions and the parent's investment account against the subsidiary's equity.
- For lease-intensive businesses, capitalize operating leases as debt equivalents to avoid understating leverage.
- In M&A DCF, explicitly model the 338(h)(10) tax savings as a separate PV benefit stream rather than embedding it in the discount rate.

## Data Integration

This methodology leverages:
- **SEC Filings**: Use `get_statement()` + footnotes for deferred tax breakdowns and lease disclosures
- **XBRL Facts**: Use `search_xbrl_facts()` for DTA/DTL balances, SBC expense, NCI balances
- **Footnotes**: Critical for lease maturity schedules, OID/OIP terms, and 338(h)(10) structuring details
- **Knowledge Base**: `search_investment_strategies()` for M&A tax structuring precedents

## Core DCF Methodology Supplement

### UFCF Derivation Build Sequence

The standard unlevered DCF values the enterprise (all capital providers) using Unlevered Free Cash Flow discounted at WACC. The build order from financial statements is:

```
Revenue
  - Cost of Sales (plug: Revenue - Gross Profit, where GP = Revenue x GP Margin)
  - R&D, SG&A (driven by % of revenue from consensus)
  = EBIT (Operating Income, sourced from income statement)
  x (1 - Marginal Tax Rate)  &lt;-- NOT the GAAP effective rate. Use statutory marginal rate.
  = NOPAT (EBIAT)            &lt;-- Tax-affected EBIT, deliberately ignoring interest tax shield
  + Depreciation & Amortization (from cash flow statement, first add-back)
  + Changes in Net Working Capital (Prior Year NWC - Current Year NWC; NWC = WC Assets - WC Liabilities)
  - Capital Expenditures (from cash flow statement, investing section)
  = Unlevered Free Cash Flow
```

Critical rule: **start from EBIT, not Net Income.** Net income is levered -- it includes interest income/expense, which distorts operating profitability. The interest tax shield is captured in the WACC discount rate via the (1 - t) adjustment on cost of debt, not in the cash flows. NWC balance should be held as a constant % of revenue across forecast years; the year-over-year change is what enters UFCF. CapEx should decline as a % of revenue toward maturity.

### Mid-Year Convention Mechanics

Standard end-of-period discounting assumes 100% of annual cash flows arrive on the last day of the fiscal year -- a conservative distortion. The mid-year convention assumes cash flows arrive evenly throughout the year, effectively discounting from the midpoint.

Excel implementation for mid-year dates (full forecast years):
```
=AVERAGE(Prior_Year_End, Current_Year_End)
```

Discounting formula (universal):
```
PV = Cash_Flow / (1 + WACC)^((Cash_Flow_Date - Valuation_Date) / 365)
```

The exponent uses actual-day count divided by 365, not YEARFRAC. A mid-year toggle (cell containing IF statement switching between end-of-year and mid-year dates) enables rapid before/after comparison. The mid-year adjustment increases stage 1 PV by approximately 4%. For the stub year, the mid-year concept does not apply in the same way -- the stub itself is already a partial year; discount to the stub year-end, not the stub midpoint.

When to use: always in sell-side/buy-side institutional models. The end-of-period assumption is considered a pedagogical simplification, not a professional standard.

### Terminal Value: Perpetuity Growth Method vs Exit Multiple

**Perpetuity Growth Method (Gordon Growth Model):**
```
TV_t = FCF_t * (1 + g) / (WACC - g)
```

Use when: intrinsic valuation is the primary objective; the company is mature with stable, predictable growth; the analyst wants to avoid "infecting" the DCF with market-based pricing. The growth rate (g) cannot exceed the long-term nominal GDP growth rate (2-4%). Every company effectively converges to approximately 3%. Cross-check the result by calculating the implied exit EBITDA multiple = TV / Terminal Year EBITDA.

**Exit Multiple Method:**
```
TV_t = Terminal_Year_EBITDA * Selected_Multiple
```

Use when: the analysis supports a transaction or LBO context; PE/IB professionals think in entry/exit multiple terms; comparables provide a defensible multiple anchor. Select the peer median, not the target's current multiple (target converges to peer levels at maturity). Cross-check by backsolving the implied perpetuity growth rate:
```
Implied g = (WACC - FCF_terminal/TV) / (1 + FCF_terminal/TV)
```

If implied g exceeds 4-5%, the exit multiple assumption is too aggressive relative to long-term economic growth constraints.

**Critical diagnostic:** Terminal value typically represents 77-78% of total enterprise value in a 5-year DCF. Values exceeding 85% warrant extending the explicit forecast period or re-examining terminal assumptions.

### WACC Component Selection

**Risk-Free Rate:** 10-year government bond yield (US Treasury for USD-denominated, German Bund for EUR, JGB for JPY). The 10-year is the standard proxy despite DCF cash flows extending in perpetuity. The 20-year or 30-year is theoretically more aligned with equity duration but is less liquid and less standard in practice.

**Equity Risk Premium:** 5-8% range for developed-market public companies. Sourced from Ibbotson/Morningstar (leading provider) or Duff & Phelps. Calculated as the historical spread between S&P 500 returns and 10-year Treasury yields, typically over an 80-year lookback window. Add a small-cap premium for companies below $4B market cap (0.5% for $800M-$4B, 1.0% for $200M-$800M, 2.5% below $200M). Add a country risk premium (Damodaran data) for non-US operating exposure. Neither SCP nor CRP is multiplied by beta -- they are additive premiums above the risk-free rate.

**Beta -- Unlevered/Relevered:**
```
Step A (Delever observed peer betas): beta_U = beta_L / (1 + (1 - t) * (Net_Debt / Market_Cap))
Step B (Average unlevered betas across peer set)
Step C (Relever at target capital structure): beta_L = beta_U_avg * (1 + (1 - t_target) * (D_target / E_target))
```

Always use **adjusted beta** (Bloomberg's mean-reverted forward beta) over raw historical beta. Standard lookback: 5-year monthly. Industry beta is preferable even for public companies because it cancels uncorrelated company-specific noise across peers. Net debt in the formula = gross debt minus cash.

**Cost of Debt:** For public companies with traded debt: use the **yield-to-maturity** on the longest-dated, actively traded bond (~10 years). Do NOT use the coupon rate -- it reflects historical issuance conditions, not current marginal borrowing cost. For private companies or those without traded debt: use the risk-free rate plus a credit spread corresponding to the company's synthetic rating (from rating agency yield-spread tables). The after-tax cost of debt = pre-tax cost of debt x (1 - marginal tax rate). Use the marginal rate, not the effective rate.

**WACC Formula:**
```
WACC = (E/V) * r_e + (D/V) * r_d * (1 - t)
```
Where E = market value of equity (diluted shares x share price), D = market value of debt (use book value as proxy unless interest rates have changed substantially since issuance). The WACC assumes a constant capital structure throughout the projection period. If capital structure changes materially period-by-period, use Adjusted Present Value (APV) instead.

**Negative Net Debt Weights:** When cash exceeds debt, equity weight mathematically exceeds 100% and debt weight is negative. This is correct -- the weights still sum to 100%. Provide a target-capital-structure override for manual adjustment.

### DCF-to-3-Statement Model Circularity Resolution

In an integrated DCF, each UFCF line item is linked directly to the corresponding cell in the 3-statement model rather than using standalone drivers. This creates circular references when the DCF-derived equity value feeds back into WACC capital weights.

Resolution: enable iterative calculation in Excel (File > Options > Formulas; Max Iterations = 100, Maximum Change = 0.001). Set calculation mode to "Automatic except for data tables" to prevent data tables from recalculating on every cell change. Insert a **circularity breaker toggle** in all interest formulas:
```
=IF(CircBreak=1, AVERAGE(BOP, EOP) * Rate, 0)
```
Models must run with the breaker on for debugging (circularity disabled) and off for final output.

For private companies, the DCF equity value itself determines the equity weight in WACC. This requires iterative calculation plus an explicit circuit breaker; failure to enable iteration will produce a circular reference error.

### Sensitivity Analysis

**Data Tables:** Excel Data Table with `{=TABLE(row_input_cell, column_input_cell)}` array formula. Row input = WACC, column input = long-term growth rate (perpetuity method) or exit EBITDA multiple (exit multiple method). Tighten step increments for client presentation (0.5% steps for growth rate). Center base-case assumptions in the middle of the sensitivity variable range.

**Primary tables:** (1) Equity value per share vs WACC and long-term growth rate; (2) Equity value per share vs WACC and exit EBITDA multiple; (3) Implied year-1 EV/EBITDA multiple vs WACC and growth rate. For the perpetuity approach, the exit multiple does not affect the output; for the exit multiple approach, the growth rate does not affect the output. Do not cross-wire the wrong sensitivity variable to each method.

### Common Errors

1. **Double-counting the interest tax shield:** Using actual GAAP taxes in UFCF then also applying the (1-t) adjustment to cost of debt in WACC. Fix: always calculate unlevered taxes as EBIT x marginal tax rate.

2. **Forecasting change in NWC directly:** Growing the year-over-year change in NWC by revenue instead of holding NWC balance as a % of revenue and computing the delta. The year-over-year change should narrow toward zero as the company matures.

3. **Using coupon rate instead of YTM for cost of debt:** The coupon rate is historical. YTM reflects current market conditions and the company's true marginal borrowing cost.

4. **Inconsistent period timing in discounting exponents:** Mixing end-of-year and mid-year dates within the same DCF without a consistent toggle. Every cash flow date must use the same convention.

5. **Terminal value overweight:** Accepting TV >85% of TEV without investigation. Extend the explicit forecast period or normalize the terminal year FCF (converge CapEx/D&A to ~1.0, remove unsustainable working capital swings).

6. **Not normalizing terminal year FCF:** If terminal year CapEx substantially exceeds D&A (growth company still in investment mode at year 5), the terminal FCF is artificially depressed. Normalize by converging CapEx/D&A to approximately 1.0, representing steady-state maintenance capex plus a modest growth premium.

7. **Using raw beta without unlevering/relevering:** Peer companies have different capital structures. A highly levered peer's observed beta applied directly to a low-leverage target overstates the cost of equity. Always delever and relever.
