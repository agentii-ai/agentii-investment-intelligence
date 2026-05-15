# Audit Xls — Validation Checklist

Expanded version of `## Validation Gates` with per-gate remediation steps.

1. **hardcoded_count**: reported for every tagged category
   - *Remediation*: If any category unreported: refuse delivery.
2. **formula_trace**: lists all cross-sheet references
   - *Remediation*: If trace empty but formulas exist: flag as gap.
3. **standard agentii citations**: checked on all cell comments
   - *Remediation*: If non-conforming: list violations.
