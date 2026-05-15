# 3 Statement Model — Validation Checklist

Expanded version of `## Validation Gates` with per-gate remediation steps.

1. **balance sheet balance**: Assets = Liabilities + Equity within 1%
   - *Remediation*: If unbalanced > 1%: refuse delivery, report imbalance amount.
2. **cash flow tie-out**: CF ending cash = BS cash
   - *Remediation*: If mismatched: refuse delivery, report discrepancy.
3. **forecast years**: exactly 5 historical + 5 forecast years
   - *Remediation*: If < 5+5: flag in Coverage Gaps, proceed with available data.
