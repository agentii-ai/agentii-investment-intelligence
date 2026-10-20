# Company Life Cycle Classification — Institutional Methodology

Methodology synthesized from institutional investment research; all text is an original paraphrase.

---

## Cash Flow-Based Classification

Traditional life cycle classification relies on proxies: age (older = mature), size (bigger = mature), or profitability. These proxies are weak. Age and size have low correlation with where a company actually is in its life cycle. A better approach uses the three components of the cash flow statement.

### The Five Stages (3-Year Rolling Sign Patterns)

| Stage | Operating CF (CFO) | Investing CF (CFI) | Financing CF (CFF) | Description |
|:---:|:---:|:---:|:---:|------|
| **Birth** | − | − | + | Company is investing heavily and not yet generating positive operating cash flow. Raising external capital to fund growth. |
| **Growth** | + | − | + | Operating CF has turned positive. Still investing heavily. Still raising capital (debt or equity) to fund expansion. |
| **Mature** | + | − | − | Strong operating CF. Still investing (CFI negative). Now generating enough cash to pay down debt and return capital (CFF negative). |
| **Decline** | + | + | − | Operating CF still positive but company is divesting assets (CFI positive — selling more than investing). Paying down obligations. |
| **Turnaround** | Transitional | Transitional | Transitional | Signs changing. Company moving from one stage to another. The key is identifying the direction of transition. |

### Classification Methodology

Use a 3-year rolling window to smooth annual volatility:
1. For each of the last 3 fiscal years, classify CFO, CFI, CFF as positive or negative
2. If all 3 years show the same pattern → stable stage
3. If only 2 of 3 years match → transitional (flag reduced confidence)
4. If the pattern has shifted in the most recent year → potential stage transition — cross-reference with qualitative indicators

---

## Transition Probability Matrix (1990-2022 IPO Cohort)

Based on analysis of all US IPOs from 1990-2022, companies at each stage have the following 3-year transition probabilities:

| From \ To | Birth | Growth | Mature | Decline |
|-----------|:---:|:---:|:---:|:---:|
| **Birth** | 35% | 50% | 10% | 5% |
| **Growth** | 5% | 55% | 35% | 5% |
| **Mature** | 2% | 5% | 75% | 18% |
| **Decline** | 8% | 12% | 20% | 60% |

Key observations:
- Growth → Mature is the most common transition (35% probability over 3 years)
- Companies can move backward in the cycle (Mature → Growth if new product cycles or acquisitions shift the CF pattern)
- Birth companies have a 50% probability of reaching Growth within 3 years; those that don't typically fail or remain sub-scale
- Decline companies have a 40% probability of transitioning out of Decline within 3 years (Turnaround = 20%, back to Growth = 12%, Birth = 8%)

---

## TSR by Stage Transition

Historical total shareholder returns for companies transitioning between stages (1990-2022):

| Transition | 3-Year Median TSR | Interpretation |
|-----------|:---:|------|
| Birth → Growth | +35% | Highest return — operating leverage kicks in |
| Decline → Mature (Turnaround) | +28% | Successful restructuring reprices the stock |
| Growth → Growth (stay) | +18% | Steady compounder |
| Mature → Mature (stay) | +8% | Low growth, stable returns |
| Growth → Mature | +5% | Transition priced in; modest returns |
| Mature → Decline | −12% | Value destruction as business erodes |

---

## Integration with Turnaround Assessment

This CF-based classification complements the existing financial scorecard approach. Two perspectives:

1. **CF-based**: What does the cash flow pattern tell us about where the company IS in the life cycle?
2. **Scorecard-based**: What do the financial metrics tell us about whether this is a genuine turnaround or a value trap?

When both frameworks agree (CF-based says "Decline transitioning" + scorecard ≥ 7) → highest conviction. When they disagree → investigate the discrepancy. A company with strong turnaround scorecard metrics but CF pattern still firmly in Decline may be too early to enter.

---

## Limitations

- **CFO borderline**: Companies with near-zero operating CF may flip classifications year-to-year. Use 3-year rolling window.
- **Acquisition distortion**: Large acquisitions can temporarily shift CFI deeply negative, mimicking Growth stage in a Mature company. Adjust for M&A cash flows when significant.
- **Financial companies**: Banks and insurers have different CF statement structures. This classification is less reliable for financial sector companies.
