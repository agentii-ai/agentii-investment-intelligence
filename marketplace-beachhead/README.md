# Agentii Research Beachhead

**Version**: 0.1.0
**Publisher**: Agentii.ai (Agentii Singapore entity)
**License**: Apache-2.0 (see `LICENSE`)

24 analyst-grade skills for SEC filings, earnings, and biotech catalysts, backed by the Agentii MCP server.

---

## What is included

| Plugin | Skills | What it covers |
|---|---:|---|
| `equity-research-core` | 9 | Recent quarter, business model, competitive, growth strategy, secular trends, turnaround, risk, earnings sentiment, valuation methods |
| `bio-pharm` | 15 | FDA catalysts (devices/medicines/vaccines), pipelines, trial readout, market share, market sizing, event takeaways, CT status diff, med-adapted sector/peer/earnings/recent-quarter |

Total: **24 skills**.

## Install — Claude

```bash
claude plugin marketplace add <this-repo-or-path>
claude plugin install equity-research-core@agentii-research-beachhead
claude plugin install bio-pharm@agentii-research-beachhead
```

In Claude Cowork: Customize → Browse plugins → Add marketplace from GitHub/path.

## Install — Codex

```bash
codex plugin marketplace add <this-repo-or-path>
codex plugin add equity-research-core@agentii-research-beachhead
codex plugin add bio-pharm@agentii-research-beachhead
```

## Authentication, trial, and pricing

- The bundle is **free to install**.
- Authentication uses the Agentii API (`AGENTII_API_KEY` or OAuth). No key is embedded in this repository.
- New users receive a **7-day free trial**.
- **After the trial, the account is locked until a paid API/plan is selected.** Past artifacts remain
  accessible; new skill runs are blocked until upgrade.

## Data coverage

SEC filings, XBRL facts, earnings transcripts/calendar for roughly 2,000 US stocks; clinical trials,
drug pipelines, FAERS, AdCom, and PDUFA for biotech/pharma. The temporal-authority universe is 1,146
pipeline tickers; broader coverage is source-specific.

## Limitations

- Not a trading bot, investment recommendation, or replacement for professional judgment.
- 36/56 non-ERC skills lack output contracts; 15/15 bio-pharm skills lack artifact contracts.
- 3,795 drug-knowledge rows have null mechanism/indication columns; the surface declares
  `source_not_loaded`.
- Temporal Phase 2B and the validation layer are design-only.
- Refresh cadence varies by source; not real-time for every dataset.

## Security

See `SECURITY.md`. Do not report vulnerabilities in public issues.

## Source

Canonical package: `agentii-investment-intelligence` (v3.3.0). This beachhead is a packaging subset; it
does not modify skill bodies.
