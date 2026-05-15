# agentii-investment-intelligence

**Institutional-grade equity research skills for AI agents.** 25 Claude-type skills, 24 slash commands, and a managed-agent cookbook that produce citation-backed financial analysis, Excel models, and PowerPoint presentations — all powered by agentii.ai's agent-use-ready SEC filing data plane.

[![Apache 2.0 License](https://img.shields.io/badge/license-Apache--2.0-blue)](./LICENSE)

> **Design pattern**: This repository mirrors the architecture of [`anthropics/financial-services`](https://github.com/anthropics/financial-services) — marketplace plugin system, vertical skill decomposition, agent-plugin bundling, and managed-agent cookbook deployment. The key difference: instead of pointing skills at 11 external data providers (FactSet, S&P Global, Daloopa, …), all skills point at a single `agentii` MCP server backed by agentii.ai's own data plane. agentii.ai becomes the data provider — analogous to FactSet, Daloopa, or S&P Global — delivering SEC EDGAR filings, XBRL financials, earnings calendars, and company profiles as agent-use-ready data for US-public-equity investment intelligence.

> [!IMPORTANT]
> Nothing in this repository constitutes investment, legal, tax, or accounting advice. These skills draft analyst work product — research notes, financial models, presentation decks — for review by a qualified professional. They do not make investment recommendations, execute transactions, or bind risk. Every output is staged for human sign-off. You are responsible for verifying outputs and for compliance with the laws and regulations that apply to your firm.

## What's in the repo

- **[Skills](#skills)** — 25 Claude-type skills across 4 verticals, each driven by the same retrieval+analysis loop but with vertical-specific methodology, defaults, and validation gates. Skills auto-activate when their trigger phrases match.
- **[Agent Plugin](#agent-plugin)** — `agentii-equity-agent`: a single self-contained plugin bundling all 25 skills, 24 slash commands, and the full agent system prompt. One install gives you everything.
- **[Managed Agent Cookbook](#managed-agent-cookbook)** — headless / server-side / Claude-for-M365 deployment via the Claude Managed Agents API. 4 capability-isolated subagents (retrieval → analytical → bi → visualization).
- **[Commands](#slash-commands)** — 24 slash commands (`/agentii:dcf`, `/agentii:earnings-sentiment`, `/agentii:peer-bench`, …) with mode-addressability (`--mode=<slug>`, `--peers=<T1>,<T2>`).

## Get an API Key

All data-plane tools authenticate with a single `AGENTII_API_KEY` issued by **[agentii.ai](https://agentii.ai)**.

1. Visit [agentii.ai](https://agentii.ai) and create an account
2. Navigate to **API Keys** in the dashboard
3. Generate a key — 7-day free trial with 1,000 credits, no credit card required
4. Set the environment variable:

```bash
export AGENTII_API_KEY=agnt-...
```

The key authenticates both the `agentii` data-plane MCP (SEC filings, XBRL, earnings, companies) and the `agentii-office` MCP (Excel/PPT generation). Skills probe both MCP health endpoints at startup and surface actionable errors if the key is missing or expired.

## Quick Install

### Claude Code

```bash
claude plugin marketplace add agentii-ai/agentii-investment-intelligence
claude plugin install agentii-equity-agent      # One-shot: all 25 skills + 24 commands + system prompt
```

Or install individual verticals:

```bash
claude plugin install equity-research-core      # 8 dimension skills, 8 commands
claude plugin install business-intelligence     # 5 BI skills, 5 commands
claude plugin install industry-analysis         # 4 industry skills, 4 commands
claude plugin install models-and-pitches        # 8 modeling skills, 9 commands (Excel/PPT)
```

### OpenCode / Codex / Goose / OpenClaw

Each vertical is independently installable via the Agent Skills standard. Clone or symlink the vertical's directory into your agent's skills path:

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

The `agentii` MCP entry is replicated byte-identically in each vertical's `.mcp.json` from `contracts/mcp-canonical.json`. Host CLIs deduplicate MCP servers by name, so installing multiple verticals carries no overhead.

### Verify

Restart your agent, then invoke any slash command:

```
/agentii:recent-quarter LLY
```

Expected: a structured, citation-backed report covering revenue, margins, EPS, and management guidance for Eli Lilly's most recent quarter.

## Skills

Skills are the central abstraction — each is a `SKILL.md` file with YAML frontmatter and markdown methodology. The agent's function-calling router loads them on-demand when trigger phrases match (progressive disclosure, ~100 tokens at scan time).

### equity-research-core (8 skills, 48 sub-prompt modes)

Core equity research dimensions. Each skill supports mode-addressable sub-prompts (`--mode=<slug>`).

| Skill | Command | Modes | Description |
|-------|---------|-------|-------------|
| `dim-recent-quarter-performance` | `/agentii:recent-quarter` | 5 | Revenue breakdown, margin drivers, EPS, guidance, sequential momentum |
| `dim-competitive-landscape` | `/agentii:competitive` | 8 | Peer positioning, market-share dynamics, moat assessment, pricing power |
| `dim-growth-strategy` | `/agentii:growth-strategy` | 5 | Organic/inorganic growth decomposition, pipeline analysis, execution tracking |
| `dim-secular-tech-trends` | `/agentii:secular-trends` | 8 | Technology adoption cycles, disruption risk, strategic positioning |
| `dim-turnaround-stagnation` | `/agentii:turnaround` | 9 | Performance inflection detection, operational metrics, leadership impact |
| `dim-risk-analysis` | `/agentii:risk` | 4 | Regulatory, competitive, macro, and technology risk assessment |
| `dim-earnings-sentiment` | `/agentii:earnings-sentiment` | 6 | Analyst estimates vs. guidance, sentiment trends, surprise history |
| `dim-valuation-methods` | `/agentii:valuation-methods` | 3 | Multiples, DCF inputs, and valuation assumption extraction |

### business-intelligence (5 skills)

| Skill | Command | Description |
|-------|---------|-------------|
| `business-model-analysis` | `/agentii:business-model` | Revenue model classification, customer concentration, unit economics extraction |
| `revenue-decomposition` | `/agentii:revenue-decomp` | Segment breakdown, geographic split, product-line waterfall |
| `unit-economics` | `/agentii:unit-economics` | CAC/LTV estimation, churn inference, gross margin per unit |
| `what-if-scenario` | `/agentii:what-if` | Scenario tree construction (base/bull/bear), sensitivity to macro variables |
| `operational-kpi-tracker` | `/agentii:operational-kpi` | Headcount trends, utilization rates, backlog/book-to-bill |

### industry-analysis (4 skills)

| Skill | Command | Description |
|-------|---------|-------------|
| `peer-benchmarking` | `/agentii:peer-bench` | Multi-ticker financial comparison, growth/value matrix, composite z-score ranking |
| `sector-overview` | `/agentii:sector-overview` | TAM estimation, competitive concentration (HHI), regulatory landscape |
| `competitive-positioning` | `/agentii:competitive-positioning` | Strategic group mapping, differentiation analysis, competitive advantage assessment |
| `supply-chain-map` | `/agentii:supply-chain` | Supplier/customer dependency analysis, geographic concentration, bottleneck identification |

### models-and-pitches (8 skills)

Excel financial models and PowerPoint deliverables. These skills require an office backend — see [Office Backends](#office-backends).

| Skill | Command | Description |
|-------|---------|-------------|
| `dcf-model` | `/agentii:dcf` | DCF valuation with live formulas, WACC decomposition, sensitivity tables |
| `comps-analysis` | `/agentii:comps` | Trading comps with statistical benchmarking (mean/median/high/low) |
| `3-statement-model` | `/agentii:3-statement` | Integrated IS/BS/CF with cross-statement balancing checks |
| `lbo-model` | `/agentii:lbo` | LBO with sources & uses, debt schedule, returns waterfall |
| `audit-xls` | `/agentii:audit-xls` | Workbook auditor: formula errors, hardcodes, cross-sheet refs, citation checks |
| `xlsx-author` | — | Custom Excel workbook generation via Python/openpyxl scripts |
| `pitch-deck` | `/agentii:pitch-deck` | 12–16 slide investment thesis presentation with sourced footers |
| `earnings-preview-deck` | `/agentii:earnings-preview` | 4–6 slide earnings preview with consensus estimates, surprises, catalysts |

## Agent Plugin

`agentii-equity-agent` bundles all 25 skills, 24 slash commands, and the full agent system prompt into a single installable unit. The system prompt ports the well-tested `system_v2_7.py` retrieval+analysis loop with 7 named blocks (role, retrieval strategy, three-layer protocol, fiscal period conventions, reasoning instructions, financial analysis standard, citation).

**One install, everything included.** The agent plugin is the recommended install path for new users.

## Managed Agent Cookbook

For headless / server-side / Claude-for-M365 deployment, [`managed-agent-cookbooks/agentii-equity-agent/`](./managed-agent-cookbooks/agentii-equity-agent/) contains:

- **`agent.yaml`** — orchestrator manifest with model selection, MCP bindings, and `callable_agents` decomposition
- **4 capability-isolated subagents**: `retrieval` (data gathering, no Write, no office), `analytical` (reasoning + spec construction, no office execution), `bi` (scenario analysis), `visualization` (office-plane execution, no independent retrieval)
- **`steering-examples.json`** — 10+ canonical task examples
- **`contracts/`** — frozen-at-v1.0 evidence-pack schema, failure policy, subagent handoff contract

The cookbook uses the same system prompt as the agent plugin — one source, two deployment paths.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
scripts/deploy-managed-agent.sh agentii-equity-agent
```

## Slash Commands

All 24 slash commands accept the v1.0 mode-addressability syntax:

```bash
/agentii:recent-quarter LLY                           # Runs the default essentials_modes subset
/agentii:recent-quarter LLY --mode=revenue-composition # Single named mode
/agentii:recent-quarter LLY --modes=revenue,margin     # Multi-mode (comma-separated)
/agentii:recent-quarter LLY --mode=all                 # Full dimension (all sub-prompts)
/agentii:peer-bench NVDA --peers=AMD,AVGO,INTC         # Explicit peer set (max 10)
```

See [`docs/commands/MODE_SYNTAX.md`](./docs/commands/MODE_SYNTAX.md) for the complete invocation contract.

## MCP Tools

The `agentii` data-plane MCP at `https://mcp.agentii.ai/mcp` exposes 20+ tools backed by 10 years of SEC filings across 165+ US-public-equity tickers. Each tool name equals its API endpoint under `/v1/`.

### Tier 1 — Always Available (Neon PostgreSQL, 100% success rate)

| Tool | Purpose | Key Parameters |
|------|---------|---------------|
| `search_xbrl_facts` | Query XBRL financial facts (Revenue, EPS, Assets, …) | `ticker`, `concept`, `fiscal_year`, `fiscal_period` |
| `list_xbrl_concepts` | Discover canonical XBRL concept names before querying | `namespace`, `search` |
| `search_sec_filings` | Standardized SEC filing metadata (10-K, 10-Q, 20-F) | `ticker`, `form_type`, `date_from`, `date_to` |
| `search_documents` | 8-K/6-K page-content documents with pre-computed labels | `ticker`, `form_type`, `keyword` |
| `search_companies` | Company registry search (165 tickers) | `ticker`, `name`, `exchange` |
| `search_earnings_calendar` | Earnings calendar events by ticker and fiscal year | `ticker`, `fiscal_year` |
| `list_upcoming_earnings` | Upcoming earnings dates within N days | `tickers`, `days` |
| `list_sources` | Discover available document sources for a ticker | `ticker`, `year`, `source_type` |
| `list_coverage` | Per-source ticker coverage with record counts and freshness tiers | `ticker`, `source_type` |
| `list_domains` | Available knowledge domains | (none) |
| `search_keyword_in_source` | Full-text keyword search within a known document | `source_id`, `keyword` |

### Tier 2 — Use With Fallback

These tools forward to endpoints not yet deployed at `api.agentii.ai`. Skills automatically fall back to Tier 1 equivalents.

| Tool | Fallback |
|------|----------|
| `get_company_financials` | Use `search_xbrl_facts` with concept filter |
| `get_company_profile` | Use `search_companies` |
| `get_company_fiscal_calendar` | Use `search_earnings_calendar` + manual format inference |
| `get_ticker_coverage` | Use `list_coverage` (same data) |
| `read_source_outline` | Use `list_sources` |
| `read_source_pages` | Use `search_keyword_in_source` + `search_sec_filings` |
| `search_unified` | Use parallel `search_xbrl_facts` + `search_documents` |
| `batch_search` | Use sequential individual calls |

### Office Plane (`agentii-office`)

The `agentii-office` MCP at `https://mcp.agentii.ai/office/mcp` exposes 9 tools for Excel/PPT generation. Declared only in `models-and-pitches/.mcp.json`. Skills also support local fallback — see below.

## Office Backends

`models-and-pitches` skills support a 3-tier office backend chain, probed in order at runtime:

| Tier | Backend | Requirements |
|------|---------|-------------|
| 1 | `agentii-office` MCP (recommended) | `AGENTII_API_KEY` with office quota |
| 2 | Python + LibreOffice | `pip install openpyxl python-pptx` + `brew install libreoffice` |
| 3 | OfficeCLI | `curl -fsSL https://officecli.ai/install.sh \| bash` (single ~50MB binary, zero deps) |

If ANY backend is available, skills proceed. If ALL are unavailable, skills surface `AGENTII_OFFICE_UNREACHABLE` with resolution paths. See [`docs/install/office-backends.md`](./docs/install/office-backends.md) for per-platform instructions.

## Retrieval Architecture

Every skill follows the **three-layer agent-use-ready retrieval protocol** when searching unstructured documents at scale:

| Layer | Tool | Purpose |
|-------|------|---------|
| **1 — Document Discovery** | `search_documents` / `search_sec_filings` | Find candidate filings without reading content (pre-computed `secondary_labels` classify 8-K disclosure types) |
| **2 — Page Map** | `read_source_outline` | Scan ALL pages' `description` + `keywords` without loading `page_content` — pinpoint 3–5 relevant pages |
| **2.5 — Keyword Filter** | `search_keyword_in_source` | Optional narrowing for large documents (>50 pages) |
| **3 — Deep Read** | `read_source_pages` | Load full `page_content` with `[[Table{idx}]]` markers for ONLY selected pages |

For multi-period analysis (2+ fiscal quarters), skills use `search_cross_period` — server-side parallel dispatch with one `period-search-subagent` per fiscal period, each independently executing the three-layer protocol. ~99% token efficiency vs. naive page-by-page loading.

For structured financial metrics (Revenue, EPS, margins), skills use `search_xbrl_facts` — a single SQL call covers all requested periods with no document retrieval needed.

## Repository Layout

```
├── .claude-plugin/marketplace.json     ← Master plugin registry
├── plugins/
│   ├── agent-plugins/
│   │   └── agentii-equity-agent/       ← ONE agent: all 25 skills + system prompt
│   ├── vertical-plugins/
│   │   ├── equity-research-core/       ← 8 dimension skills, 8 commands
│   │   ├── business-intelligence/      ← 5 BI skills, 5 commands
│   │   ├── industry-analysis/          ← 4 industry skills, 4 commands
│   │   └── models-and-pitches/         ← 8 modeling skills, 9 commands (Excel/PPT)
│   └── partner-built/                  ← Reserved for v1.1 partner plugins
├── managed-agent-cookbooks/
│   └── agentii-equity-agent/           ← CMA deployment (agent.yaml + 4 subagents)
├── contracts/                          ← Shared contracts, schemas, tool-name-map
├── scripts/                            ← check.py, validate-*.py, port-*.py, sync-*.py
├── docs/                               ← Install guides, architecture docs, MODE_SYNTAX
├── LICENSE                             ← Apache 2.0
└── NOTICE                              ← Upstream attribution
```

## Making It Yours

- **Bring your templates** — teach skills your firm's branded PowerPoint layouts and Excel formatting standards
- **Adjust methodology** — edit `## Defaults` tables and `references/institutional-defaults.md` to match your firm's conventions (projection horizon, terminal growth, peer selection criteria)
- **Add firm context** — drop your sector taxonomy, terminology, and disclaimers into skill bodies
- **Chain skills** — `dcf-model → pitch-deck → xlsx_convert(pdf)` for end-to-end institutional workflows
- **Add your own** — copy the structure under `plugins/vertical-plugins/<vertical>/skills/` for workflows not yet covered

## Contributing

Everything is markdown, YAML, and Python. Fork, edit, PR.

- **Edit skills** in `vertical-plugins/`, then run `python3 scripts/sync-agent-skills.py` to propagate to the agent bundle
- **Run `python3 scripts/check.py`** before pushing — 25 checks across all manifests, frontmatter, references, and cross-file consistency
- Skills follow the open Agent Skills standard (agentskills.io), supported by Claude Code, OpenCode, Codex, OpenClaw, Goose, and Claude Cowork

## License

Apache License 2.0 © agentii-ai. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

This package includes skills ported and optimized from [`anthropics/financial-services`](https://github.com/anthropics/financial-services) (Apache 2.0). Methodology bodies stay byte-stable from upstream; data-source blocks and tool calls are replaced with agentii-native equivalents. See per-skill `.upstream-fingerprint` files and `contracts/tool-name-map.json` for the canonical port mapping.
