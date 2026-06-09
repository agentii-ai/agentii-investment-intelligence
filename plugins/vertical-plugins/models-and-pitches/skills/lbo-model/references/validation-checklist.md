# Lbo Model — Validation Checklist

Expanded version of `## Validation Gates` with per-gate remediation steps.

1. **sources vs uses**: sources = uses within 0.1%
 - *Remediation*: If unbalanced: refuse delivery.
2. **sponsor IRR**: >= 20% at exit
 - *Remediation*: If < 20%: flag in assumptions.
3. **debt schedule**: mandatory repayments present for each tranche
 - *Remediation*: If missing: refuse delivery.
