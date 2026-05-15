# Dcf Model — Validation Checklist

Expanded version of `## Validation Gates` with per-gate remediation steps.

1. **projection horizon**: >= 5 years (10 years for secular-trends analysis)
   - *Remediation*: If < 5 years: refuse delivery, report actual horizon.
2. **terminal growth rate**: < risk-free rate proxy (current 10Y UST)
   - *Remediation*: If terminal_g >= rf: flag in assumptions section, note conservatism violation.
3. **WACC components**: WACC = (E/V x Ke) + (D/V x Kd x (1-T)) with all components cited
   - *Remediation*: If components uncited: refuse delivery, list missing citations.
4. **hardcoded_count**: == 0 for projection|margin|discount_factor|pv|sensitivity per xlsx_audit
   - *Remediation*: If > 0: per the hardcode gate, refuse delivery. Bounce back ONCE with audit report.
