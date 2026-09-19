# Rate Cycle Analysis: WACC and Cost of Capital Methodology

## Protocol

### WACC Component Selection Methodology

The weighted average cost of capital discounts unlevered free cash flows -- cash flows available to all capital providers before debt service. The formula weights after-tax cost of debt and cost of equity by their market-value proportions:

```
WACC = [r_debt * (1 - T) * D/(D+E)] + [r_equity * E/(D+E)]
```

For public companies, equity weight uses market capitalization (diluted shares x share price). For private companies, the DCF-derived equity value creates circularity -- enable Excel iterations and insert a circuit breaker. Debt weight uses book value as a market-value proxy unless interest rates have changed materially since issuance. In that case, discount each bond's contractual cash flows at the YTM of comparably-rated debt to derive market value. An unlevered DCF assumes constant WACC, which implies a stable debt-to-equity ratio throughout the projection period. Substantial capital structure changes require period-by-period WACC adjustments or a switch to the Adjusted Present Value (APV) framework.

### Risk-Free Rate: 10Y Treasury and Its Limitations

The theoretical ideal matches the risk-free instrument's maturity to each cash flow's duration. In practice, the 10-year U.S. Treasury yield serves as the universal proxy. Liquidity considerations drive this choice -- long-dated Treasuries (20Y, 30Y) trade with wider bid-ask spreads and less consistent pricing, introducing noise rather than precision. The 10Y German Eurobond serves the equivalent function for European companies. Despite the 2011 S&P downgrade of U.S. sovereign debt, Treasuries retain risk-free proxy status because the U.S. controls its currency and faces no practical borrowing constraint. Bloomberg is the standard source for current yields. When yield curve inversion creates material differences between short and long rates, the 10Y remains the convention; practitioners do not interpolate between maturities.

### Cost of Debt: YTM vs. Synthetic Rating

The cost of debt is the current yield-to-maturity on the company's outstanding long-term debt, not the coupon rate. The coupon reflects historical issuance conditions; YTM reflects current market borrowing costs. For publicly traded bonds, extract YTM via Excel's XIRR function using market price, coupon schedule, and maturity date. The tax shield adjusts this to an after-tax rate: $1 of interest expense reduces earnings by $1 x (1 - T), not by $1. Use the marginal tax rate. The shield assumes the company has sufficient pre-tax income to absorb the deduction -- a valid assumption for going-concern models but requiring validation in distressed scenarios.

For private companies or firms without observable bond yields, use the synthetic rating approach: compute interest coverage ratio (EBIT / interest expense), map to a credit rating using agency-published tables (Moody's, S&P), then apply the corresponding yield spread over Treasuries for that rating. The cost of debt increases with leverage because higher debt ratios elevate default risk. This feedback loop between capital structure and cost of debt creates the U-shaped WACC curve central to capital structure optimization.

### Equity Risk Premium: Method Selection

The ERP represents the excess return investors demand for bearing equity market risk over the risk-free rate. Three estimation approaches exist, each with distinct applications:

1. **Historical excess returns** (favored approach): Compare long-run S&P 500 total returns against 10Y Treasury yields. Sources: Ibbotson/Morningstar, Damodaran, Duff & Phelps. Produces ERP estimates of 5-7%. Most common in practice due to objectivity and reproducibility. Limitation: backward-looking; may misprice during structural regime changes.

2. **Survey-based**: Poll institutional investors and academics on expected ERP. Forward-looking but subject to anchoring and recency bias. Useful as a cross-check when survey data is current.

3. **Implied ERP**: Back-solve from current market levels and consensus earnings forecasts using a dividend discount or residual income model. Most theoretically sound for current market conditions but highly sensitive to growth rate assumptions. Preferred during periods of market dislocation when historical averages are unreliable.

Standard practice uses the historical ERP (typically 6%) as the base case with survey and implied estimates as sensitivity checks. The ERP is common to all companies in CAPM; company-specific risk enters through beta.

### Beta Unlevering and Relevering

Historical beta is computed by regressing a company's stock returns against the S&P 500 over 60 months. This produces imprecise estimates -- standard errors of 20-30% are common. Bloomberg's adjusted beta (weighting raw beta at 67% and 1.0 at 33%) partially mitigates this but does not solve it. For private companies without observable prices, and for public companies with high standard errors, the industry beta approach provides superior estimates: collect observed betas for a peer group, unlever each to remove capital structure distortion, take the median unlevered beta, then relever at the target company's capital structure.

The Hamada unlevering formula:

```
beta_unlevered = beta_observed / [1 + (1 - T) * (D/E)]
```

The relevering formula reverses this:

```
beta_levered = beta_unlevered * [1 + (1 - T) * (D/E)]
```

When leverage is removed, beta always decreases -- debt amplifies equity cash flow volatility. This methodology assumes debt beta is zero (debt is risk-free), which holds for investment-grade companies but requires adjustment for highly leveraged firms where debt carries material default risk.

### Capital Structure Optimization

The value driver formula reveals the optimization objective:

```
Value = NOPAT_{t+1} * [1 - g/ROIC] / (WACC - g)
```

Reducing WACC always increases value. In a worked example, lowering WACC from 10% to 9% increases enterprise value by 25% ($210K to $262.5K). The optimal capital structure minimizes WACC: initially, replacing expensive equity with tax-advantaged debt reduces WACC. As leverage increases, default risk raises both r_debt and r_equity (via higher levered beta), eventually overwhelming the tax benefit. The point where WACC reaches its minimum defines the optimal debt ratio. Additional debt beyond this point destroys value. For companies with ROIC substantially above WACC, aggressive reinvestment creates more value than WACC minimization -- the growth engine dominates the financing engine.

### NPV/IRR Decision Rules

NPV: Present value of all project cash flows minus the initial investment, discounted at the cost of capital. Accept if NPV > 0. IRR: The discount rate that produces NPV = 0. Accept if IRR > cost of capital. When these rules conflict (non-conventional cash flows producing multiple IRRs, or mutually exclusive projects with different scales), NPV is the theoretically correct decision rule. IRR's reinvestment assumption -- that interim cash flows can be reinvested at the IRR itself -- is "impossible" as a practical matter. Only zero-coupon instruments are exempt from this limitation. The payback period method is categorically rejected as it ignores post-payback cash flows entirely. The discounted payback period corrects for risk within the payback window but retains the same fatal flaw.

### Yield-to-Worst in Cost of Debt

When bonds carry embedded options (calls, puts), the cost of debt must reflect the most conservative outcome. Call provisions favor the issuer: exercised when rates fall, allowing refinancing at lower rates. Put provisions favor the bondholder: exercised when rates rise or credit deteriorates. Compute YTM, YTC at each call date, and YTP at each put date, then take the minimum -- Yield to Worst. For a premium bond with a 5.50% coupon: NY = 5.50%, CY = 5.24%, YTM = 5.16%, YTC1 = 4.95%, YTC2 = 5.44%, YTP = 4.31%. YTW = 4.31% (the put yield), the appropriate rate for a conservative WACC build.

### Duration and Convexity

Duration measures percentage price change per unit yield change, enabling comparison of interest rate risk across securities with different coupons, maturities, and credit quality. Longer maturity, lower coupon, and lower yield all increase duration. Convexity captures the non-linearity of the price-yield relationship: prices rise faster when yields fall than they decline when yields rise (positive convexity). When used with duration, convexity provides more precise bond price sensitivity measurement. For cost of capital applications, monitoring duration informs how WACC responds to interest rate regime shifts -- material for long-dated DCF models where WACC stability is embedded as an assumption.
