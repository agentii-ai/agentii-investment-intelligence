# Changelog

## 0.1.0 — 2026-10-20

- Initial 24-skill beachhead: `equity-research-core` (9) + `bio-pharm` (15).
- Claude marketplace manifest `.claude-plugin/marketplace.json`.
- Codex marketplace manifest `.agents/plugins/marketplace.json`.
- MCP configuration inherited from the canonical plugins.
- Apache-2.0 license, README, security policy.
- Validated: `claude plugin validate` passes with symlink warnings; both plugins install in isolated
  Claude and Codex homes.
- Known gaps: skill execution/trial-lock not yet tested; ERC plugin description says 8 skills (root says 9).
