# Comps Analysis — Validation Checklist

Expanded version of `## Validation Gates` with per-gate remediation steps.

1. **peer count**: between 4 and 8
   - *Remediation*: If < 4: flag in Coverage Gaps. If > 8: trim to top 8 by sector proximity.
2. **trading multiples**: include EV/EBITDA + P/E at minimum
   - *Remediation*: If missing: flag which multiple is unavailable and why.
3. **comps statistics table**: present with mean, median, high, low
   - *Remediation*: If missing: refuse delivery.
