---
description: "Generate a 4-6 slide earnings preview presentation with consensus estimates, historical surprises, and forward catalysts"
argument-hint: "<TICKER> [--quarter=<Q>] [--year=<YYYY>]"
---

## Workflow

1. Delegate to `earnings-preview-deck` skill in models-and-pitches vertical
2. Skill retrieves earnings calendar, XBRL facts, company profile, and peer data
3. Skill constructs `pptx_spec` and builds presentation via available office backend
4. Output: `.pptx` file with 4-6 slides (Title, Company Overview, Consensus Estimates, Historical Surprises, Peer Comparison, Catalysts & Outlook)

The default invocation retrieves the most recent quarter's data. Specify `--quarter=Q3 --year=2025` to target a specific fiscal period.

> See [Mode syntax](../../../docs/commands/MODE_SYNTAX.md) for `--mode=` / `--modes=` / `--peers=` invocation rules.
