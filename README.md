# agentii-investment-intelligence

<p align="center">
  <img src="./demo.gif" alt="Claude Code using agentii.ai to search LLY 10-K and receiving real SEC filing data" width="720">
</p>

<p align="center">
  <strong>The financial data layer for AI agents.</strong><br>
  Open-source alternative to FactSet / Daloopa / S&P Global for AI agents.<br>
  1,146+ US equities with full SEC filing history. 48 Claude-type skills. 20+ MCP tools.<br>
  One API key. Zero infrastructure. Single entrance: <code>/agentii:skill-name</code>.
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence"><img src="https://img.shields.io/github/stars/agentii-ai/agentii-investment-intelligence" alt="Stars"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence/discussions"><img src="https://img.shields.io/github/discussions/agentii-ai/agentii-investment-intelligence" alt="Discussions"></a>
  <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/version-2.3.1-green" alt="Version"></a>
</p>

---

## Why agentii

Wall Street pays $30K+/seat/year for FactSet, Bloomberg, and S&P Global. Those platforms were built for humans clicking through terminals. AI agents need **agent-use-ready data** — structured, citation-backed, page-addressable, API-delivered.

agentii.ai ingests every SEC filing (10-K, 10-Q, 8-K, 20-F, 6-K) and 15K+ earnings call transcripts (2022+) into a Neon PostgreSQL data plane with 15.99M XBRL facts, 51K+ source documents, and 1.34M+ parsed pages. A single `agentii` MCP server at `mcp.agentii.ai` exposes 30+ tools (incl. institutional ownership + insider activity) that Claude Code, OpenCode, Goose, Codex, OpenClaw, and Claude Cowork consume natively.

This repository mirrors [`anthropics/financial-services`](https://github.com/anthropics/financial-services) — marketplace plugin system, vertical skill decomposition, agent-plugin bundling. The difference: all skills point at a **single `agentii` MCP server** backed by agentii.ai's own data plane. There is no second MCP — office output uses the same **code-mode** approach (Python + LibreOffice, invoked via `Bash`) that Anthropic's package uses.

> [!IMPORTANT]
> Nothing in this repository constitutes investment, legal, tax, or accounting advice. These skills produce analyst work product for review by a qualified professional. Every output is staged for human sign-off.

---

## Quick Install

### 1. Get an API Key

[agentii.ai/api-keys](https://agentii.ai/api-keys) — 7-day free trial, 2,000 credits, no credit card.

### 2. Global MCP Setup

```bash
export AGENTII_API_KEY=sk_live_YOUR_KEY_HERE
claude mcp add-json --scope user agentii \
  '{"type":"http","url":"https://mcp.agentii.ai/mcp","headers":{"Authorization":"Bearer <YOUR_KEY>"}}'
```

Writes to `~/.claude.json`. Restart Claude Code — 30+ tools auto-discover on every session from any directory.

### 3. Install Skills (Primary: Local Copy)

```bash
bash scripts/copy-skills-local.sh   # Copies all 48 skills + commands to ~/.claude/
```

Restart Claude Code — all 48 skills register under a **single unified namespace, `/agentii:skill-name`** (skills land in `~/.claude/skills/agentii/`, commands in `~/.claude/commands/agentii/`). This is the **recommended install method** — one namespace, no per-vertical prefixes, and it works reliably on all Claude Code versions.

> **Single namespace by design**: the local-copy path exposes *only* `/agentii:*`. There is no `/equity-research-core:*` or `/models-and-pitches:*` surface — every skill is reached the same way regardless of which vertical authored it.

<details>
<summary>Advanced (not recommended): per-vertical plugin installs</summary>

Installing the vertical plugins individually creates **additional** `/vertical:skill` namespaces (e.g. `/equity-research-core:risk`) alongside `/agentii:*`. Prefer the local-copy path above for a clean single namespace.

```bash
claude plugin marketplace add agentii-ai/agentii-investment-intelligence
claude plugin install models-and-pitches     # adds /models-and-pitches:* namespace
# ... etc for other verticals
```

> **Future path**: `claude plugin install agentii@agentii-investment-intelligence` for the unified meta-plugin (single `/agentii:*` namespace). Currently blocked by [Claude Code issue #15178](https://github.com/anthropics/claude-code/issues/15178); use `bash scripts/copy-skills-local.sh` until the plugin bug is fixed.

</details>

### 4. Verify

```
/agentii:recent-quarter LLY
```

Expected: structured, citation-backed report with real SEC filing data and clickable citations like `[📄 LLY 10-K p.42](https://agentii.ai/v/LLY/sec129/42)` — every material fact is immediately followed by its source link. The closing TUI reply includes a **Key Citations** block of clickable URLs so you can cmd+click straight to the exact SEC page.

---

## What's Inside

| Component | Description |
|-----------|-------------|
| **Skills** | 48 Claude-type skills across 12 verticals — trigger-phrase auto-activation + `/agentii:skill-name` single entrance |
| **Meta-Plugin** | `plugins/agentii-plugin/` — unified install bundles all 48 skills under `/agentii:*` namespace (symlinked from verticals) |
| **Agent Plugin** | `agentii-equity-agent` — managed agent with the `system_v2_7`-ported system prompt, three-layer retrieval protocol, and citation discipline |
| **MCP Tools** | 30+ tools at `mcp.agentii.ai/mcp` — SEC filings, XBRL financials, entity search, earnings calendar, two-tier page outline, real-time quotes |
| **Office Output** | Code-mode: `openpyxl` (Excel .xlsx), `python-pptx` (PowerPoint .pptx), `python-docx` (Word .docx) + LibreOffice headless recalc — no office MCP server |
| **Citations** | Every fact links to `agentii.ai/v/{ticker}/{citation_id}/{page}` — clickable, verifiable, inline-after-fact + TUI Key Citations block |
| **Workspace Memory** | `agentii.md` index, per-ticker outputs with YAML frontmatter, `snapshots/` thesis synthesis with `[FACT]`/`[DEDUCTED]`/`[VIEW]` taxonomy, `sessions/` archive |
| **Contracts** | 21 shared contracts in `contracts/` — single source of truth for retrieval protocol, citations, office tooling, preflight, memory, and tracing |
| **Instant Data** (spec 039) | `data-tools/` — zero-key-first macro/market/earnings tools behind `~~category` placeholders, AGENT_CONTRACT envelope, file cache + failover; opt-in `setup_credentials.py` wizard for free API keys |
| **Enrichment & Quality** (spec 039) | `skill-registry.yaml` + `scripts/enhance-skill.py` (YAML workflow presets) + `scripts/quality-scan.py` (5-dimension 0–10 score, CI gate) |
| **Packaging** (spec 039) | `packaging/export.py` emits codex/cowork/generic-cli variants from canonical SKILL.md (diff-clean, placeholders preserved) |

---

## Skills

Skills auto-activate when trigger phrases match. Each is a `skills/agentii/<name>/SKILL.md` file with YAML frontmatter and markdown methodology — the single canonical artifact across all 6 CLI hosts (Claude Code, OpenCode, Codex, OpenClaw, Goose, Claude Cowork). Thin `commands/*.md` wrappers are also shipped per vertical for explicit `/agentii:skill-name` slash-command invocation.

Deep methodology and output structure live in per-skill `references/` directories (progressive disclosure) — the SKILL.md body stays lean (~700–900 words), and depth loads on demand. [Full methodology →](./contracts/skill-methodology-template.md)

### equity-research-core (9 skills)

| Command | Description |
|---------|-------------|
| `/agentii:recent-quarter` | Quarterly P&L progression, margin drivers, EPS vs consensus, sequential momentum |
| `/agentii:business-model` | Revenue model classification, product-line decomposition, distribution channels, customer segments |
| `/agentii:competitive` | Peer positioning, market-share dynamics, moat assessment, pricing power |
| `/agentii:growth-strategy` | Organic/inorganic growth decomposition, pipeline analysis, execution tracking |
| `/agentii:secular-trends` | Technology adoption cycles, disruption risk, strategic positioning |
| `/agentii:turnaround` | Performance inflection detection, operational metrics, leadership impact |
| `/agentii:risk` | Regulatory, competitive, macro, and technology risk assessment |
| `/agentii:earnings-sentiment` | Analyst estimates vs. guidance, sentiment trends, surprise history |
| `/agentii:valuation-methods` | Multiples, DCF inputs, PEG integration, valuation assumption extraction |

### models-and-pitches (9 skills)

| Command | Description |
|---------|-------------|
| `/agentii:dcf` | DCF valuation with live formulas, WACC decomposition, sensitivity tables → `.xlsx` |
| `/agentii:comps` | Trading comps with statistical benchmarking (mean/median/high/low) → `.xlsx` |
| `/agentii:3-statement` | Integrated IS/BS/CF with cross-statement balancing via XBRL calculation arcs → `.xlsx` |
| `/agentii:lbo` | LBO with sources & uses, debt schedule, returns waterfall → `.xlsx` |
| `/agentii:sotp-valuation` | Sum-of-the-parts valuation with segment-level multiples |
| `/agentii:audit-xls` | Workbook auditor: formula errors, hardcoded cells, calculation arc cross-validation |
| `/agentii:xlsx-financials` | XBRL-to-Excel with number formatting, frozen headers, named ranges, Checks tab → `.xlsx` |
| `/agentii:pitch-deck` | 12–16 slide investment thesis presentation → `.pptx` (`.md` fallback) |
| `/agentii:earnings-preview` | 4–6 slide earnings preview with consensus estimates, surprises, catalysts → `.pptx` (`.md` fallback) |

### quantitative-analysis (5 skills)

| Command | Description |
|---------|-------------|
| `/agentii:ratio-analysis` | 24 financial ratios across 6 categories with cross-company comparison |
| `/agentii:peg-valuation` | PEG = P/E ÷ Growth Rate with Peter Lynch thresholds and sector benchmarks |
| `/agentii:reverse-dcf` | Solve for implied growth rate/margins from current price |
| `/agentii:ddm-valuation` | Multi-stage Dividend Discount Model for mature dividend payers and financials |
| `/agentii:residual-income` | Book Value + PV of future economic profit — for banks, insurers, capital-intensive firms |

### business-intelligence (4 skills)

| Command | Description |
|---------|-------------|
| `/agentii:revenue-decomp` | Segment breakdown, geographic split, product-line waterfall |
| `/agentii:unit-economics` | CAC/LTV estimation, churn inference, gross margin per unit |
| `/agentii:what-if` | Scenario tree (bear/base/bull), probability-weighted EV, sensitivity matrix |
| `/agentii:operational-kpi` | Headcount trends, utilization rates, backlog/book-to-bill |

### industry-analysis (4 skills)

| Command | Description |
|---------|-------------|
| `/agentii:peer-bench` | Multi-ticker financial comparison, growth/value matrix, z-score ranking |
| `/agentii:sector-overview` | TAM estimation, competitive concentration (HHI), regulatory landscape |
| `/agentii:competitive-positioning` | Porter's Five Forces, strategic group mapping, differentiation analysis |
| `/agentii:supply-chain` | Supplier/customer dependency, geographic concentration, bottleneck identification |

All valuation skills support `--mode=scenario` for Bear/Base/Bull probability-weighted analysis.

---

## Office Output (Code-Mode + LibreOffice)

v2.3.1 adopts Anthropic's proven code-mode architecture — no office MCP server. The agent writes self-contained Python scripts and executes them via `Bash`. [Full contract →](./contracts/office-tooling.md)

| Format | Library | Primary | Degraded Fallback |
|--------|---------|---------|-------------------|
| **Excel** | `openpyxl` + LibreOffice recalc | `.xlsx` with live formulas, named ranges, Checks tab | `.md` with full data tables |
| **PowerPoint** | `python-pptx` + LibreOffice validation | `.pptx` with one idea/slide, sourced footers | `.md` slide specification |
| **Word** | `python-docx` (available, deferred) | `.docx` for memo/IC-note deliverables | `.md` (default until memo skill ships) |

**Conventions** (mirroring Anthropic `xlsx-author`): blue font = hardcoded input, black = formula, green = cross-sheet link. A `Checks` tab carries TRUE/FALSE validation ties. LibreOffice headless (`soffice --headless`) handles recalculation and PDF export. The formulas-over-hardcodes invariant (`hardcoded_count == 0` for projection/discount/PV cells) is mandatory per FR-020.

**Layered preflight (FR-043)**: skills probe for a live Office session (Cowork `mcp__office__*` tools) first, then fall back to Python + LibreOffice, then degrade to `.md` with the exact `pip install` remediation command. Never a silent failure.

---

## Workspace Memory

v2.3.1 introduces a file-first hybrid memory architecture that persists context across sessions. After running skills, your workspace looks like this:

```
workspace/
├── agentii.md                          # Project memory index (YAML frontmatter + markdown table)
├── style.md                            # Optional workspace overrides (currency, peers, verbosity)
├── NVDA/
│   ├── 2026-06-15_0930_recent-quarter_summary.md   # Tier 1: per-skill outputs with YAML frontmatter
│   └── 2026-06-15_1045_dcf_base.xlsx               # Office artifacts
├── snapshots/
│   └── NVDA/
│       └── 2026-06-15_thesis.md        # Tier 2: cross-skill synthesis (auto-triggered at ≥2 skills)
├── sessions/
│   ├── INDEX.md                         # Session index (auto-loaded)
│   └── 2026-06-15/                     # Full transcripts (on-demand only)
├── _cross/                              # Multi-ticker analyses (peer-bench, comps, competitive-positioning)
│   └── semis_2026-06-15_1400_peer-bench_nvda-amd-avgo.md
└── _sector/                             # Pure sector/thematic analyses
    └── tech.semiconductors/
        └── 2026-06-15_1500_sector-overview_summary.md
```

**Key conventions:**

- **`agentii.md`**: YAML frontmatter header (machine-parseable via `head -30`) + Markdown summary table (human-readable). Appended after every skill run.
- **`{ticker}/`**: Tier-1 per-skill outputs with structured YAML frontmatter (`key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`).
- **`snapshots/{ticker}/`**: Tier-2 thesis synthesis auto-triggered when ≥2 skills run on the same ticker in a session. Distills cross-skill conclusions with `[FACT]`/`[DEDUCTED]`/`[VIEW]` classification.
- **`_cross/`**: Multi-ticker outputs for peer comparisons and cross-company analyses.
- **`_sector/`**: Pure industry/thematic analyses with no primary ticker.
- **`sessions/`**: Full transcripts archived by date (not auto-loaded); `INDEX.md` lists all sessions.

---

## Citations: Page-Accurate Provenance

Every material fact, table row, and metric in a deliverable is immediately followed by its clickable source link — not deferred to a bottom appendix. **Inline-first placement** is the package's core UVP.

```
Revenue grew 22% YoY to $215.9B [📄 NVDA 10-K p.42](https://agentii.ai/v/NVDA/sec173/42)
```

The bottom `## Citations` section provides a non-duplicative roll-up index. The closing TUI reply includes a **Key Citations** block (0–10 clickable URLs) so you can cmd+click straight to the exact SEC page without opening the deliverable file.

**Citation format**: `https://agentii.ai/v/{ticker}/{citation_id}/{N}` — path-based, ~7 tokens, browser-redirects to the exact filing page. Non-SEC sources use `ref<N>` (PDF) / `fda<N>` (FDA) prefixes.

---

## Data-Source Priority

Every skill follows a mandatory data-source ordering (FR-075):

1. **XBRL facts FIRST** (grounding truth) — `search_xbrl_facts` with `view=detailed` for segment/product/channel breakdowns
2. **SEC filings SECOND** — 10-K (annual), 10-Q (quarterly), 20-F/6-K (foreign) via the three-layer retrieval protocol
3. **Web search LAST RESORT** — only when both XBRL and SEC filings are insufficient; flagged `web_search_used: true` in frontmatter; non-authoritative

---

## Three-Layer Retrieval Protocol

Skills that search unstructured documents at scale follow a mandatory protocol codified in `contracts/retrieval.md`:

| Layer | Tool | What It Returns |
|-------|------|-----------------|
| **1 — Document Discovery** | `search_documents`, `search_sec_filings` | Candidate filings by ticker, form_type, date, labels |
| **2 — Page Map** | `read_source_outline` (lightweight) → `read_source_deep_outline` (escalation) | Page descriptions + keywords; NULL = skip (cover/TOC/legal) |
| **3 — Deep Read** | `read_source_pages` | Full `page_content` with `[[Table{idx}]]` markers for the 3–5 selected pages only |

`search_cross_period` is the primary multi-period path for skills analyzing 4+ fiscal quarters.

---

## Coverage

**1,146+ US public companies** across med + tech + industrial + fin + consumer sectors, with full SEC filing history from 2022 onward (10-K, 10-Q, 8-K, 20-F, 6-K) and earnings call transcripts (2022+). Every data point carries a clickable citation watermark linking to the original filing page.

| Sector | Example Tickers |
|--------|-----------------|
| Technology / Semiconductors | NVDA, AMD, AVGO, MSFT, AAPL, CRM, ORCL, INTC |
| Healthcare / Biotech / Pharma | LLY, ABBV, JNJ, PFE, MRK, BMY, UNH |
| Financials | JPM, BAC, GS, MS, V, MA |
| Consumer / Retail | AMZN, WMT, COST, HD, NKE, TSLA |
| Industrials / Energy / Materials | GE, CAT, XOM, BA, RTX, LMT |
| Communication / Media | META, GOOG, NFLX, DIS, T, VZ |

**Data volume**: 15.99M XBRL facts, 51K+ source documents (SEC filings + earnings call transcripts), 1.34M+ parsed silver pages. XBRL facts updated daily via Dagster pipeline. SEC filings indexed within hours of EDGAR publication. [Full coverage →](https://agentii.ai/coverage) | [Request a ticker →](https://agentii.ai/request-data)

Skills surface a `data_freshness` warning for tickers with < 100% coverage and refuse to fabricate data outside the launch cohort.

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  AI Agent        │     │  MCP Server      │     │  REST API          │
│  (Claude Code,   │ ──► │  mcp.agentii.ai  │ ──► │  api.agentii.ai    │
│   OpenCode, etc) │     │  30+ tools       │     │  Hono + Vercel     │
└─────────────────┘     └──────────────────┘     └────────┬───────────┘
                                                          │
                          ┌───────────────────────────────┤
                          │                               │
                    ┌─────▼──────┐                  ┌─────▼──────┐
                    │  Neon      │                  │  Redis     │
                    │  PostgreSQL│                  │  (Upstash) │
                    │  4.17M     │                  │  tracing   │
                    │  XBRL facts│                  │  hot tier  │
                    └────────────┘                  └────────────┘
```

**Data plane**: Neon PostgreSQL (product data — XBRL facts, companies, filings, entity aliases). **Tracing plane**: Redis Upstash (hot, 7d TTL) + Supabase PostgreSQL (cold, audit). **Office**: code-mode Python + LibreOffice — no office MCP server.

One MCP server. One API key. Zero infrastructure.

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

All 48 skills use the open Agent Skills standard (`skills/agentii/<name>/SKILL.md`) — works identically across all 6 CLI hosts. The `agentii` MCP entry is replicated in each vertical's `.mcp.json` — host CLIs deduplicate by server name.

```bash
# Recommended: install the full agentii namespace
cp -r plugins/agentii-plugin/skills/agentii ~/.claude/skills/agentii/    # Claude Code
cp -r plugins/agentii-plugin/skills/agentii ~/.config/opencode/skills/   # OpenCode
cp -r plugins/agentii-plugin/skills/agentii ~/.codex/skills/             # Codex
cp -r plugins/agentii-plugin/skills/agentii ~/.config/goose/skills/      # Goose
openclaw add ./plugins/agentii-plugin                                      # OpenClaw

# Or: single vertical for lightweight installs
cp -r plugins/vertical-plugins/equity-research-core/skills/agentii ~/.config/opencode/skills/
```

See [`adapters/`](./adapters/) for per-CLI configuration files. All agents benefit from [`ai-agents.txt`](./ai-agents.txt) at the repo root.

---

## Making It Yours

- **Bring your templates** — mount firm-branded `.pptx` templates at `./templates/` for pitch-deck and earnings-preview
- **Adjust methodology** — edit `## Defaults` tables and `references/institutional-defaults.md`
- **Override via style.md** — per-workspace `style.md` overrides defaults for lookback quarters, reporting currency, peer universe, and output verbosity
- **Chain skills** — `dcf → pitch-deck` for end-to-end model-to-deck workflows; `xlsx-financials → audit-xls` for quality assurance
- **Edit skills** in `plugins/vertical-plugins/<vertical>/skills/agentii/<name>/SKILL.md` — the single canonical source
- **Sync changes**: `python3 scripts/sync-agent-skills.py` then `bash scripts/assemble-agentii-namespace.sh`
- **Run CI checks**: `python3 scripts/check.py` before pushing — validates manifests, frontmatter, CI gates, and cross-file consistency

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
| Ticker not found | Non-canonical ticker | Three-layer ticker resolution handles aliases (GOOGL → GOOG, BRK.B → BRK.A) |
| `.xlsx` not produced | `openpyxl` not installed | `pip install openpyxl` — skill produces `.md` fallback with exact command |
| `.pptx` not produced | `python-pptx` not installed | `pip install python-pptx` — skill produces `.md` slide spec with exact command |
| Old `dim-*` or `/equity-research-core:` commands missing | Legacy commands deleted (Phase 23) | All skills now at `/agentii:skill-name` — single entrance |

---

## Repository Structure

```
agentii-investment-intelligence/
├── plugins/
│   ├── agentii-plugin/                  # Meta-plugin: /agentii:* surface (48 symlinked skills)
│   ├── vertical-plugins/
│   │   ├── equity-research-core/        # 9 skills
│   │   ├── business-intelligence/       # 4 skills
│   │   ├── industry-analysis/           # 4 skills
│   │   ├── models-and-pitches/          # 9 skills
│   │   └── quantitative-analysis/       # 5 skills
│   └── agent-plugins/
│       └── agentii-equity-agent/        # Managed agent bundle
├── contracts/                           # 21 shared contracts (single source of truth)
├── scripts/                             # CI gates, sync, validation, assembly
├── docs/install/                        # Per-CLI install guides
├── style.md                             # Package-shipped formatting standard
├── README.md, LICENSE, NOTICE, CHANGELOG.md
└── SKILL.md                             # Root package manifest
```

---

## Contributing

Everything is markdown, YAML, and Python. Fork, edit, PR.

- **Edit skills** in `plugins/vertical-plugins/<vertical>/skills/agentii/<name>/SKILL.md` — the single canonical source
- **Sync changes**: `python3 scripts/sync-agent-skills.py` then `bash scripts/assemble-agentii-namespace.sh`
- **Run `python3 scripts/check.py`** before pushing — validates all manifests, frontmatter, CI gates, and cross-file consistency
- Skills follow the open Agent Skills standard, supported by Claude Code, OpenCode, Codex, OpenClaw, Goose, and Claude Cowork

---

## License

Apache License 2.0 © agentii-ai. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

This package includes skills ported and optimized from [`anthropics/financial-services`](https://github.com/anthropics/financial-services) (Apache 2.0). Methodology bodies stay byte-stable from upstream; data-source blocks and tool calls are replaced with agentii-native equivalents.
