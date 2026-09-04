# Cost of Capital — Institutional Estimation Methodology

Methodology synthesized from institutional investment research; all text is an original paraphrase.

---

## The Cost of Capital as Opportunity Cost

The weighted average cost of capital (WACC) is not a corporate finance abstraction — it is the opportunity cost of the next best alternative investment of equivalent risk. Every dollar of capital deployed must earn at least this rate to avoid destroying value. The estimation of WACC is therefore not a mechanical exercise but a judgment about the minimum acceptable return.

---

## WACC Formula

```
WACC = (E/V × Cost of Equity) + (D/V × Cost of Debt × (1 − Tax Rate)) + (P/V × Cost of Preferred)
```

Where E, D, P are the market values of equity, debt, and preferred stock, and V = E + D + P.

---

## Risk-Free Rate Selection

The risk-free rate is the foundation of the entire cost of capital estimation. An error here propagates through every subsequent calculation.

### Selection Logic

| Maturity | When to Use | Rationale |
|----------|------------|-----------|
| **10-Year Treasury** | Standard for most companies | Matches the typical duration of equity cash flows; most liquid benchmark |
| **20-Year Treasury** | Long-duration assets (infrastructure, utilities, real estate) | Better duration-matching for assets with very long cash flow streams |
| **Interpolated Rate** | When the company's asset duration falls between standard maturities | Custom duration match using the yield curve |

### Practical Guidance

- Use the current yield on actively traded on-the-run Treasuries, not historical averages
- The 10-year is the institutional default for equity valuation
- When the yield curve is inverted, the risk-free rate selection requires explicit justification — using the 10-year in an inverted environment may understate WACC for long-duration assets

---

## Equity Risk Premium (ERP)

The ERP is the single most impactful assumption in cost of capital estimation and the most difficult to estimate precisely. Institutional practice triangulates three approaches:

### Historical ERP
The arithmetic average of annual stock returns minus risk-free returns over the longest available period (typically 1928-present). Provides a long-horizon anchor.

Approximate value: 5.0-6.0% (arithmetic) depending on the measurement period and risk-free rate definition.

**Limitation**: Backward-looking. Does not reflect current market conditions or forward expectations.

### Implied ERP
Derived from current market prices by solving for the discount rate that equates the present value of expected future cash flows to the current index level. Forward-looking and market-consistent.

Calculated using a two-stage dividend discount model on the S&P 500:
```
Index Level = Σ[Expected Dividends_t / (1 + Rf + ERP)^t] + Terminal Value
```

Approximate value (late 2024): 4.0-5.0% depending on growth assumptions.

**Limitation**: Sensitive to growth rate and payout assumptions.

### Survey-Based ERP
Academic and practitioner surveys of CFOs, portfolio managers, and academics. Provides a consensus check.

Typical range: 4.5-5.5%.

### Triangulation
The institutional approach uses the average of historical and implied ERP as the base estimate, with the survey as a sanity check. If the three diverge significantly (>2 percentage points), the implied ERP is given the most weight because it reflects current market conditions.

---

## Beta Estimation

### Raw Beta
Calculate the slope coefficient from regressing the stock's excess returns against the market's excess returns over a 2-5 year period using monthly or weekly data. Weekly data is preferred as it reduces noise while maintaining sufficient observations.

### Adjusted Beta
The Bloomberg adjustment (and industry standard) shrinks the raw beta toward 1.0:
```
Adjusted Beta = (Raw Beta × 0.67) + (1.0 × 0.33)
```

This reflects the empirical tendency of betas to regress toward 1.0 over time (the "beta blume" effect). Companies with extreme raw betas will see the largest adjustments.

### De-levering and Re-levering Beta

**De-levering** (remove the effect of the company's current leverage):
```
Unlevered Beta = Levered Beta / [1 + (1 − Tax Rate) × (Debt / Equity)]
```

**Re-levering** (apply the target or industry-average capital structure):
```
Re-levered Beta = Unlevered Beta × [1 + (1 − Tax Rate) × (Target Debt / Equity)]
```

This is essential when the company's capital structure differs from the industry average, or when valuing a division using a different capital structure.

### Industry Betas

Industry average betas (de-levered to remove leverage effects) are more reliable than individual company betas because:
1. Industry averages have lower standard error (law of large numbers)
2. Individual company betas may be distorted by temporary factors (illiquidity, M&A speculation, share class effects)
3. The industry beta better represents the systematic risk of the business

| Industry | Average Unlevered Beta |
|----------|:---:|
| Software (Systems/Applications) | 1.05-1.25 |
| Biotechnology | 0.95-1.15 |
| Oil & Gas (Integrated) | 0.80-0.95 |
| Utilities (Regulated) | 0.40-0.55 |
| Banks (Regional) | 0.50-0.65 |
| Retail (Specialty) | 0.80-1.00 |

---

## Cost of Debt

### Yield-to-Maturity Approach (Preferred for Public Debt)
Use the YTM on the company's outstanding publicly traded bonds, weighted by market value and maturity. This is the most accurate measure of the company's current marginal borrowing cost.

### Rating-Based Approach (for Companies Without Public Debt)
1. Determine the company's synthetic credit rating based on interest coverage ratios:
   - EBIT / Interest > 8.5× → AAA/AA
   - 6.5-8.5× → A
   - 3.0-6.5× → BBB
   - 1.5-3.0× → BB
   - < 1.5× → B or below
2. Apply the current yield spread for that rating over Treasuries of equivalent maturity

### Synthetic Rating from Financial Ratios
When the company has no public debt and no analyst rating, estimate the cost of debt from financial statement ratios:
```
Pre-Tax Cost of Debt = Risk-Free Rate + Default Spread
```
Default spread is estimated from: Interest Coverage Ratio, Leverage (Debt/EBITDA), and Industry.

---

## Target Capital Structure Weights

Use MARKET values, not book values:
- **Equity Value**: Market Capitalization (current share price × diluted shares outstanding)
- **Debt Value**: Market value of debt (use book value as approximation if bonds are not publicly traded)
- **Preferred Stock Value**: Market value (or liquidation value if not traded)

The target weights should reflect the company's long-term target capital structure, which may differ from current weights due to temporary market movements. Use industry-average weights as a cross-check.

---

## Common Errors

1. **Using book value weights**: Book equity is an accounting residual, not an economic measure. Market values reflect the actual opportunity cost.
2. **Mismatching risk-free rate duration with cash flow duration**: Using 3-month T-bills to discount 20-year equity cash flows understates WACC.
3. **Using historical average risk-free rate**: The current risk-free rate is the opportunity cost today, not the historical average.
4. **Ignoring country risk**: For companies with significant emerging market exposure, add a country risk premium to the cost of equity.
5. **Double-counting risk**: If cash flows are already adjusted for risk (scenario-weighted), the discount rate should reflect systematic risk only.
