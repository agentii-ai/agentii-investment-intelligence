# Xlsx Author — Validation Checklist

Expanded version of `## Validation Gates` with per-gate remediation steps.

1. **output integrity**: .xlsx opens without corruption
   - *Remediation*: If corrupted: refuse delivery, debug script.
2. **named ranges**: all resolve
   - *Remediation*: If unresolved: refuse delivery.
3. **script execution**: no Python exception
   - *Remediation*: If fails: return stderr to user.
