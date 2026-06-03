# agentii-investment-intelligence

<p align="center">
  <img src="./demo.gif" alt="Claude Code using agentii.ai to search LLY 10-K and receiving real SEC filing data" width="720">
</p>

**The financial data layer for AI agents.** Open source alternative to FactSet/Daloopa for AI agents — agent-use-ready SEC filings + XBRL financials via 20 MCP tools. 25 Claude-type skills, 24 slash commands, and a managed-agent cookbook that produce citation-backed financial analysis, Excel models, and PowerPoint presentations.

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence/releases"><img src="https://img.shields.io/github/v/release/agentii-ai/agentii-investment-intelligence" alt="Release"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence/discussions"><img src="https://img.shields.io/github/discussions/agentii-ai/agentii-investment-intelligence" alt="Discussions"></a>
</p>

This repository mirrors the architecture of [`anthropics/financial-services`](https://github.com/anthropics/financial-services) — marketplace plugin system, vertical skill decomposition, agent-plugin bundling, and managed-agent cookbook deployment. The key difference: instead of pointing skills at 11 external data providers, all skills point at a single `agentii` MCP server backed by agentii.ai's own data plane.

> [!IMPORTANT]
> Nothing in this repository constitutes investment, legal, tax, or accounting advice. These skills draft analyst work product for review by a qualified professional. Every output is staged for human sign-off.

---

## Quick Install

### Path A — Global MCP (Recommended)

One command. Tools load on **every** Claude Code session, from **any** directory.

```bash
export AGENTII_API_KEY=sk_live_YOUR_KEY_HERE
claude mcp add-json --scope global agentii \
  '{"type":"http","url":"https://mcp.agentii.ai/mcp","headers":{"Authorization":"Bearer ${AGENTII_API_KEY}"}}'
```

Writes to `~/.claude.json`. Restart Claude Code — 20 tools auto-discover. [Full setup guide →](./docs/install/global-mcp-setup.md)

### Path B — Per-Project `.mcp.json`

For CI/CD or containerized environments, copy this into your project root:

```json
{
  "mcpServers": {
    "agentii": {
      "type": "http",
      "url": "https://mcp.agentii.ai/mcp",
      "headers": { "Authorization": "Bearer ${AGENTII_API_KEY}" }
    }
  }
}
```

> **API Key**: Get yours at [agentii.ai/api-keys](https://agentii.ai/api-keys) — 7-day free trial, 2,000 credits, no credit card required.

### Install Skills & Commands

MCP tools give you raw data access. Skills give you optimized system prompts, the three-layer retrieval protocol, and 24 slash commands with `agentii:` namespace.

```bash
# Add the marketplace
claude plugin marketplace add agentii-ai/agentii-investment-intelligence

# Install the managed agent + all 4 vertical skill plugins
claude plugin install agentii-equity-agent
claude plugin install equity-research-core
claude plugin install business-intelligence
claude plugin install industry-analysis
claude plugin install models-and-pitches
```

> **Known issue**: Claude Code v2.1.143 has a [plugin bug](https://github.com/anthropics/claude-code/issues/15178) where `claude plugin install` may not inject skills. Workaround: `bash scripts/copy-skills-local.sh` then restart Claude Code. Skills register as `/agentii:<name>` commands.

### Verify

```
/agentii:recent-quarter LLY
```

Expected: a structured, citation-backed report with real SEC filing data and `agentii://source/...` watermarks.

---

## What's in the Repo

| Component | Contents |
|-----------|----------|
| **Skills** | 25 Claude-type skills across 4 verticals with trigger-phrase auto-activation |
| **Slash Commands** | 24 commands (`/agentii:dcf`, `/agentii:recent-quarter`, `/agentii:peer-bench`, …) with `--mode=` addressability |
| **Agent Plugin** | `agentii-equity-agent` — one install bundles all 25 skills + 24 commands + system prompt |
| **Managed Agent Cookbook** | Headless/server-side deployment via Claude Managed Agents API with 4 capability-isolated subagents |
| **MCP Tools** | 20 tools proxied through `mcp.agentii.ai/mcp` to the agentii data plane |

---

## Skills

Skills auto-activate when their trigger phrases match. Each is a `skills/agentii/<name>/SKILL.md` file with YAML frontmatter and markdown methodology.

### equity-research-core (8 skills)

| Command | Description |
|---------|-------------|
| `/agentii:recent-quarter` | Revenue breakdown, margin drivers, EPS, guidance, sequential momentum |
| `/agentii:competitive` | Peer positioning, market-share dynamics, moat assessment, pricing power |
| `/agentii:growth-strategy` | Organic/inorganic growth decomposition, pipeline analysis, execution tracking |
| `/agentii:secular-trends` | Technology adoption cycles, disruption risk, strategic positioning |
| `/agentii:turnaround` | Performance inflection detection, operational metrics, leadership impact |
| `/agentii:risk` | Regulatory, competitive, macro, and technology risk assessment |
| `/agentii:earnings-sentiment` | Analyst estimates vs. guidance, sentiment trends, surprise history |
| `/agentii:valuation-methods` | Multiples, DCF inputs, and valuation assumption extraction |

### business-intelligence (5 skills)

| Command | Description |
|---------|-------------|
| `/agentii:business-model` | Revenue model classification, customer concentration, unit economics |
| `/agentii:revenue-decomp` | Segment breakdown, geographic split, product-line waterfall |
| `/agentii:unit-economics` | CAC/LTV estimation, churn inference, gross margin per unit |
| `/agentii:what-if` | Scenario tree construction (base/bull/bear), sensitivity to macro variables |
| `/agentii:operational-kpi` | Headcount trends, utilization rates, backlog/book-to-bill |

### industry-analysis (4 skills)

| Command | Description |
|---------|-------------|
| `/agentii:peer-bench` | Multi-ticker financial comparison, growth/value matrix, z-score ranking |
| `/agentii:sector-overview` | TAM estimation, competitive concentration (HHI), regulatory landscape |
| `/agentii:competitive-positioning` | Strategic group mapping, differentiation analysis, competitive advantage |
| `/agentii:supply-chain` | Supplier/customer dependency, geographic concentration, bottleneck ID |

### models-and-pitches (7 skills)

| Command | Description |
|---------|-------------|
| `/agentii:dcf` | DCF valuation with live formulas, WACC decomposition, sensitivity tables |
| `/agentii:comps` | Trading comps with statistical benchmarking (mean/median/high/low) |
| `/agentii:3-statement` | Integrated IS/BS/CF with cross-statement balancing checks |
| `/agentii:lbo` | LBO with sources & uses, debt schedule, returns waterfall |
| `/agentii:audit-xls` | Workbook auditor: formula errors, hardcodes, cross-sheet refs |
| `/agentii:pitch-deck` | 12–16 slide investment thesis presentation with sourced footers |
| `/agentii:earnings-preview` | 4–6 slide earnings preview with consensus estimates and catalysts |

---

## Pricing

| Plan | Monthly | Annual (20% off) | Credits/mo | Overage |
|------|---------|-------------------|------------|---------|
| **Starter** | $19.90/mo | ~$15.92/mo | 2,000 | $5/1,000 credits |
| **Pro** | $39.90/mo | ~$31.92/mo | 10,000 | $5/1,000 credits |
| **Enterprise** | Custom | Custom | 500,000+ | Custom |

7-day free trial, 2,000 credits, no credit card required. Early adopter pricing locks in — your rate stays the same as coverage expands from 200 to 1,000 stocks. [Full pricing →](https://agentii.ai/pricing)

## Coverage

200 US stocks at launch, growing to 600–1,000. Full SEC filing history (10-K, 10-Q, 8-K, 20-F, 6-K) with page-level provenance via citation watermarks (`agentii://source/...`). Data freshness tiers: ≤6h (fresh), ≤48h (stale), >48h (missing).

| Sector | Count | Example Tickers |
|--------|-------|-----------------|
| Technology | ~50 | NVDA, AMD, AVGO, INTC, MSFT, AAPL |
| Healthcare / Biotech | ~40 | LLY, ABBV, JNJ, PFE, MRK, BMY |
| Financials | ~30 | JPM, BAC, GS, MS, V, MA |
| Consumer | ~25 | AMZN, WMT, COST, HD, NKE |
| Energy / Industrials | ~30 | XOM, CVX, CAT, GE, BA |
| Other | ~25 | SPY, QQQ, IWM |

[Full coverage →](https://agentii.ai/coverage) | [Request a ticker →](https://agentii.ai/request-data)

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

---

## Making It Yours

- **Bring your templates** — teach skills your firm's branded PowerPoint layouts and Excel formatting
- **Adjust methodology** — edit `## Defaults` tables and `references/institutional-defaults.md`
- **Add firm context** — drop your sector taxonomy, terminology, and disclaimers into skill bodies
- **Chain skills** — `dcf-model → pitch-deck → xlsx_convert(pdf)` for end-to-end workflows

## Contributing

Everything is markdown, YAML, and Python. Fork, edit, PR.

- **Edit skills** in `plugins/vertical-plugins/`, then run `python3 scripts/sync-agent-skills.py`
- **Run `python3 scripts/check.py`** before pushing — validates all manifests, frontmatter, and cross-file consistency
- Skills follow the open Agent Skills standard, supported by Claude Code, OpenCode, Codex, OpenClaw, Goose, and Claude Cowork

## License

Apache License 2.0 © agentii-ai. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

This package includes skills ported and optimized from [`anthropics/financial-services`](https://github.com/anthropics/financial-services) (Apache 2.0). Methodology bodies stay byte-stable from upstream; data-source blocks and tool calls are replaced with agentii-native equivalents.
