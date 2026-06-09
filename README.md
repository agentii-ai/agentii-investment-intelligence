# agentii-investment-intelligence

<p align="center">
  <img src="./demo.gif" alt="Claude Code using agentii.ai to search LLY 10-K and receiving real SEC filing data" width="720">
</p>

<p align="center">
  <strong>The financial data layer for AI agents.</strong><br>
  Open-source alternative to FactSet / Daloopa / S&P Global for AI agents.<br>
  506 US equities with full SEC filing history. 25+ Claude-type skills. 20+ MCP tools.<br>
  One API key. Zero infrastructure.
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence"><img src="https://img.shields.io/github/stars/agentii-ai/agentii-investment-intelligence" alt="Stars"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence/discussions"><img src="https://img.shields.io/github/discussions/agentii-ai/agentii-investment-intelligence" alt="Discussions"></a>
</p>

---

## Why agentii

Wall Street pays $30K+/seat/year for FactSet, Bloomberg, and S&P Global. Those platforms were built for humans clicking through terminals. AI agents need **agent-use-ready data** — structured, citation-backed, page-addressable, API-delivered.

agentii.ai ingests every SEC filing (10-K, 10-Q, 8-K, 20-F, 6-K) into a Neon PostgreSQL data plane with 4.17M XBRL facts, 15K+ source documents, and 243K+ parsed pages. A Hono REST API exposes 20+ MCP tools that Claude Code, OpenCode, Goose, Codex, and OpenClaw consume natively.

This repository mirrors [`anthropics/financial-services`](https://github.com/anthropics/financial-services) — marketplace plugin system, vertical skill decomposition, agent-plugin bundling, and managed-agent cookbook deployment. The difference: all skills point at a **single `agentii` MCP server** backed by agentii.ai's own data plane.

> [!IMPORTANT]
> Nothing in this repository constitutes investment, legal, tax, or accounting advice. These skills produce analyst work product for review by a qualified professional. Every output is staged for human sign-off.

---

## Quick Install

### 1. Get an API Key

[agentii.ai/api-keys](https://agentii.ai/api-keys) — 7-day free trial, 2,000 credits, no credit card.

### 2. Global MCP Setup

```bash
export AGENTII_API_KEY=sk_live_YOUR_KEY_HERE
claude mcp add-json --scope global agentii \
  '{"type":"http","url":"https://mcp.agentii.ai/mcp","headers":{"Authorization":"Bearer ${AGENTII_API_KEY}"}}'
```

Writes to `~/.claude.json`. Restart Claude Code — 20+ tools auto-discover on every session from any directory.

### 3. Install Skills

```bash
claude plugin marketplace add agentii-ai/agentii-investment-intelligence
claude plugin install agentii-equity-agent
claude plugin install equity-research-core
claude plugin install models-and-pitches
claude plugin install business-intelligence
claude plugin install industry-analysis
claude plugin install quantitative-analysis
```

> **Known issue**: Claude Code v2.1.143 has a [plugin bug](https://github.com/anthropics/claude-code/issues/15178) where `claude plugin install` may not inject skills. Workaround: `bash scripts/copy-skills-local.sh` then restart. Skills register as `/agentii:<name>`.

### 4. Verify

```
/agentii:recent-quarter LLY
```

Expected: structured, citation-backed report with real SEC filing data and `[📄 LLY 10-K p.42](https://agentii.ai/v/LLY/sec129/42)` clickable citations.

---

## What's Inside

| Component | Description |
|-----------|-------------|
| **Skills** | 25+ Claude-type skills across 5 verticals with trigger-phrase auto-activation |
| **Slash Commands** | 24+ commands (`/agentii:dcf`, `/agentii:peg-valuation`, `/agentii:peer-bench`) with `--mode=` addressability |
| **Agent Plugin** | `agentii-equity-agent` — one install bundles all skills, commands, and system prompt |
| **Managed Agent Cookbook** | Headless deployment via Claude Managed Agents API with capability-isolated subagents |
| **MCP Tools** | 20+ tools at `mcp.agentii.ai/mcp` — SEC filings, XBRL financials, entity search, earnings calendar |
| **Citation Portal** | Every fact links to `agentii.ai/v/{ticker}/{citation_id}/{page}` — clickable, verifiable source |

---

## Skills

Skills auto-activate when trigger phrases match. Each is a `skills/agentii/<name>/SKILL.md` file with YAML frontmatter and markdown methodology. [Full methodology →](./contracts/skill-methodology-template.md)

### equity-research-core (9 skills)

| Command | Description |
|---------|-------------|
| `/agentii:recent-quarter` | Revenue breakdown, margin drivers, EPS, guidance, sequential momentum |
| `/agentii:competitive` | Peer positioning, market-share dynamics, moat assessment, pricing power |
| `/agentii:growth-strategy` | Organic/inorganic growth decomposition, pipeline analysis, execution tracking |
| `/agentii:secular-trends` | Technology adoption cycles, disruption risk, strategic positioning |
| `/agentii:turnaround` | Performance inflection detection, operational metrics, leadership impact |
| `/agentii:risk` | Regulatory, competitive, macro, and technology risk assessment |
| `/agentii:earnings-sentiment` | Analyst estimates vs. guidance, sentiment trends, surprise history |
| `/agentii:valuation-methods` | Multiples, DCF inputs, PEG integration, valuation assumption extraction |
| `/agentii:business-model` | Revenue model classification, customer concentration, product-line decomposition |

### models-and-pitches (8 skills)

| Command | Description |
|---------|-------------|
| `/agentii:dcf` | DCF valuation with live formulas, WACC decomposition, sensitivity tables |
| `/agentii:comps` | Trading comps with statistical benchmarking (mean/median/high/low) |
| `/agentii:3-statement` | Integrated IS/BS/CF with cross-statement balancing via XBRL calculation arcs |
| `/agentii:lbo` | LBO with sources & uses, debt schedule, returns waterfall |
| `/agentii:sotp-valuation` | Sum-of-the-parts valuation with segment-level multiples |
| `/agentii:audit-xls` | Workbook auditor: formula errors, hardcoded cells, calculation arc cross-validation |
| `/agentii:pitch-deck` | 12–16 slide investment thesis presentation with sourced footers |
| `/agentii:xlsx-financials` | XBRL-to-Excel with proper number formatting, frozen headers, named ranges |

### quantitative-analysis (5 skills)

| Command | Description |
|---------|-------------|
| `/agentii:ratio-analysis` | 24 financial ratios across 6 categories (profitability, liquidity, leverage, efficiency, valuation, growth) with cross-company comparison |
| `/agentii:peg-valuation` | PEG = P/E ÷ Growth Rate with Peter Lynch thresholds and sector comparison |
| `/agentii:reverse-dcf` | Solve for implied growth rate/margins from current price — "what does the market already price in?" |
| `/agentii:ddm-valuation` | Multi-stage Dividend Discount Model for mature dividend payers and financials |
| `/agentii:residual-income` | Book Value + PV of future economic profit — specialist tool for banks and insurers |

### business-intelligence (4 skills)

| Command | Description |
|---------|-------------|
| `/agentii:revenue-decomp` | Segment breakdown, geographic split, product-line waterfall |
| `/agentii:unit-economics` | CAC/LTV estimation, churn inference, gross margin per unit |
| `/agentii:what-if` | Scenario tree construction (bear/base/bull), sensitivity to macro variables |
| `/agentii:operational-kpi` | Headcount trends, utilization rates, backlog/book-to-bill |

### industry-analysis (4 skills)

| Command | Description |
|---------|-------------|
| `/agentii:peer-bench` | Multi-ticker financial comparison, growth/value matrix, z-score ranking |
| `/agentii:sector-overview` | TAM estimation, competitive concentration (HHI), regulatory landscape |
| `/agentii:competitive-positioning` | Strategic group mapping, differentiation analysis, competitive advantage |
| `/agentii:supply-chain` | Supplier/customer dependency, geographic concentration, bottleneck identification |

All valuation skills support `--mode=scenario` for Bear/Base/Bull probability-weighted analysis.

---

## Coverage

**506 US public companies** across all 11 GICS sectors, with full SEC filing history from 2022 onward. Every data point carries a clickable citation watermark linking to the original filing page.

| Sector | Count | Example Tickers |
|--------|-------|-----------------|
| Technology | ~130 | NVDA, AMD, AVGO, MSFT, AAPL, CRM, ORCL |
| Healthcare / Biotech | ~120 | LLY, ABBV, JNJ, PFE, MRK, BMY, UNH |
| Financials | ~60 | JPM, BAC, GS, MS, V, MA, XYZ |
| Consumer | ~80 | AMZN, WMT, COST, HD, NKE, TSLA |
| Industrials / Energy / Materials | ~80 | GE, CAT, XOM, BA, RTX, LMT |
| Communication / Utilities / Real Estate | ~36 | META, GOOG, NFLX, DIS, T, VZ |

Data freshness: XBRL facts updated daily via Dagster pipeline. SEC filings indexed within hours of EDGAR publication. [Full coverage →](https://agentii.ai/coverage) | [Request a ticker →](https://agentii.ai/request-data)

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  AI Agent        │     │  MCP Server      │     │  REST API          │
│  (Claude Code,   │ ──► │  mcp.agentii.ai  │ ──► │  api.agentii.ai    │
│   OpenCode, etc) │     │  20+ tools       │     │  Hono + Vercel     │
└─────────────────┘     └──────────────────┘     └────────┬───────────┘
                                                          │
                          ┌───────────────────────────────┤
                          │                               │
                    ┌─────▼──────┐                  ┌─────▼──────┐
                    │  Neon      │                  │  Redis     │
                    │  PostgreSQL│                  │  (Upstash) │
                    │  4.17M     │                  │  calls     │
                    │  XBRL facts│                  │  tracing   │
                    └────────────┘                  └────────────┘
```

**Data plane**: Neon PostgreSQL (product data — XBRL facts, companies, filings, entity aliases). **Tracing plane**: Redis Upstash (hot, 7d TTL) + Supabase PostgreSQL (cold, long-term audit).  **Office plane**: `mcp.agentii.ai/office` for Excel/PPT generation.

See [`contracts/`](./contracts/) for the full API and MCP tool specifications. See [`docs/architecture/`](./docs/architecture/) for system design.

---

## Pricing

| Plan | Monthly | Credits/mo | Overage |
|------|---------|------------|---------|
| **Starter** | $19.90/mo | 2,000 | $5/1,000 credits |
| **Pro** | $39.90/mo | 10,000 | $5/1,000 credits |
| **Enterprise** | Custom | 500,000+ | Custom |

7-day free trial, 2,000 credits, no credit card required. Early adopter pricing — your rate stays as coverage grows. [Full pricing →](https://agentii.ai/pricing)

---

## For Other CLI Agents

### OpenCode / Codex / Goose / OpenClaw

Each vertical is independently installable. The `agentii` MCP entry is replicated in each vertical's `.mcp.json` — host CLIs deduplicate by server name.

```bash
# OpenCode
cp -r plugins/vertical-plugins/equity-research-core ~/.config/opencode/skills/

# Codex
cp -r plugins/vertical-plugins/equity-research-core ~/.codex/skills/

# Goose
cp -r plugins/vertical-plugins/equity-research-core ~/.config/goose/skills/

# OpenClaw
openclaw add ./plugins/vertical-plugins/equity-research-core
```

All agents benefit from `ai-agents.txt` at the repo root. See [`ai-agents.txt`](./ai-agents.txt).

---

## Making It Yours

- **Bring your templates** — teach skills your firm's branded PowerPoint layouts and Excel formatting
- **Adjust methodology** — edit `## Defaults` tables and `references/institutional-defaults.md`
- **Add firm context** — drop your sector taxonomy, terminology, and disclaimers into skill bodies
- **Chain skills** — `dcf-model → pitch-deck → xlsx_convert(pdf)` for end-to-end workflows
- **Override via style.md** — per-workspace `style.md` overrides defaults for lookback quarters, reporting currency, and output verbosity

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `/agentii:recent-quarter` shows "no command" | Claude Code v2.1.143 [plugin bug](https://github.com/anthropics/claude-code/issues/15178) | `bash scripts/copy-skills-local.sh` then restart |
| `tools/list` shows 0 tools | MCP server not configured | Run the global setup command in [Quick Install](#quick-install) |
| `${AGENTII_API_KEY}` not expanded | Env var set after Claude Code started | `export AGENTII_API_KEY=...` before launching `claude` |
| `✘ not authenticated` | Key expired or invalid | Check at [agentii.ai/api-keys](https://agentii.ai/api-keys) |
| `API_KEY_REQUIRED` | Key not sent | Verify `Authorization: Bearer` header in config |
| `AGENTII_CREDITS_EXHAUSTED` | Trial credits used | Regenerate key or upgrade at [agentii.ai](https://agentii.ai) |
| `list_xbrl_concepts` returns empty | Concept name mismatch | Try "Revenues" not "Revenue", "NetIncomeLoss" not "Net Income" |
| Ticker not found | Non-canonical ticker (GOOGL, FB, SQ) | Use primary ticker (GOOG, META, XYZ) — resolution layer handles aliases |

---

## Contributing

Everything is markdown, YAML, and Python. Fork, edit, PR.

- **Edit skills** in `plugins/vertical-plugins/`, then run `python3 scripts/sync-agent-skills.py`
- **Run `python3 scripts/check.py`** before pushing — validates all manifests, frontmatter, and cross-file consistency
- Skills follow the open Agent Skills standard, supported by Claude Code, OpenCode, Codex, OpenClaw, Goose, and Claude Cowork

---

## License

Apache License 2.0 © agentii-ai. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

This package includes skills ported and optimized from [`anthropics/financial-services`](https://github.com/anthropics/financial-services) (Apache 2.0). Methodology bodies stay byte-stable from upstream; data-source blocks and tool calls are replaced with agentii-native equivalents.
