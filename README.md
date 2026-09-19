# agentii-investment-intelligence

<p align="center">
  <strong>The financial data layer for AI agents.</strong><br>
  Open-source alternative to FactSet / Daloopa / S&P Global for AI agents.<br>
  1,146+ US equities with full SEC filing history. 80 skills across 14 verticals. 30 MCP tools.<br>
  One API key. Zero infrastructure. Single entrance: <code>/agentii:skill-name</code>.
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="License"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence"><img src="https://img.shields.io/github/stars/agentii-ai/agentii-investment-intelligence" alt="Stars"></a>
  <a href="https://github.com/agentii-ai/agentii-investment-intelligence/discussions"><img src="https://img.shields.io/github/discussions/agentii-ai/agentii-investment-intelligence" alt="Discussions"></a>
  <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/version-3.3.0-green" alt="Version"></a>
</p>

> [!WARNING]
> **Not investment advice.** This repository is software. It produces analyst work
> product for review by a qualified professional — never a recommendation to trade.
> Read the full [Disclaimer](#disclaimer) before using anything here.

---

## Why agentii

Wall Street pays $30K+/seat/year for FactSet, Bloomberg, and S&P Global. Those platforms were built for humans clicking through terminals. AI agents need **agent-use-ready data** — structured, citation-backed, page-addressable, API-delivered.

agentii.ai ingests every SEC filing (10-K, 10-Q, 8-K, 20-F, 6-K) and 15K+ earnings call transcripts (2022+) into a Neon PostgreSQL data plane with 15.99M XBRL facts, 51K+ source documents, and 1.34M+ parsed pages. A single `agentii` MCP server at `mcp.agentii.ai` exposes 30 tools (incl. institutional ownership + insider activity) that Claude Code, OpenCode, Goose, Codex, OpenClaw, and Claude Cowork consume natively.

This repository mirrors [`anthropics/financial-services`](https://github.com/anthropics/financial-services) — marketplace plugin system, vertical skill decomposition, agent-plugin bundling. The difference: all skills point at a **single `agentii` MCP server** backed by agentii.ai's own data plane. There is no second MCP — office output uses the same **code-mode** approach (Python + LibreOffice, invoked via `Bash`) that Anthropic's package uses.

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

Writes to `~/.claude.json`. Restart Claude Code — all 30 tools auto-discover on every session from any directory.

### 3. Install Skills (Claude Code: Local Copy)

```bash
bash scripts/copy-skills-local.sh ~   # ~ = the target; skills land in ~/.claude/
```

> **The target argument is not optional in practice.** The script defaults to the
> *current directory*, so running it bare from the repo root installs into
> `<repo>/.claude/` instead of `~/.claude/`. Pass `~` unless you specifically want a
> project-local install.

Restart Claude Code — skills register under a **single unified namespace, `/agentii:skill-name`** (skills land in `~/.claude/skills/agentii/`, commands in `~/.claude/commands/agentii/`). This is the **recommended install method on Claude Code** — one namespace, no per-vertical prefixes, and it works reliably on all Claude Code versions.

The installer is idempotent and **prunes**: re-running it removes any installed skill that no longer exists upstream (a renamed or split skill, for example), and prints each one by name. Pass `--dry-run` to preview without writing.

> **Single namespace by design**: the local-copy path exposes *only* `/agentii:*`. There is no `/equity-research-core:*` or `/models-and-pitches:*` surface — every skill is reached the same way regardless of which vertical authored it.

> **Other hosts**: `copy-skills-local.sh` writes to `~/.claude/` only. For OpenCode, Codex, Goose, OpenClaw and Cowork, see [For Other CLI Agents](#for-other-cli-agents) — the skills are portable markdown, but the install path differs per host.

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
| **Skills** | **80** Claude-type skills across **14 verticals** — trigger-phrase auto-activation + `/agentii:skill-name` single entrance |
| **Meta-Plugin** | `plugins/agentii-plugin/` — unified install symlinks **70** skills under `/agentii:*` (10 `scenarios` kit skills are installed separately; see [Repository Structure](#repository-structure)) |
| **Agent Plugin** | `agentii-equity-agent` — managed agent with the `system_v2_7`-ported system prompt, three-layer retrieval protocol, and citation discipline |
| **MCP Tools** | **30** tools at `mcp.agentii.ai/mcp` — SEC filings, XBRL financials, entity search, earnings calendar, two-tier page outline, real-time quotes, institutional ownership, insider activity |
| **Governance** (spec 046) | `constitution.md` per workspace, thesis vs single-skill modes, mechanical gates, and a landing index that derives the spec's own status — see [Governance & Research Modes](#governance--research-modes) |
| **Report Pipeline** (spec 046) | `pack → author → assemble → render`: LLM-authored thesis reports with a render-and-optimize loop, a citation gate, and a template-owned disclaimer |
| **Office Output** | Code-mode: `openpyxl` (Excel .xlsx), `python-pptx` (PowerPoint .pptx), `python-docx` (Word .docx) + LibreOffice headless recalc — no office MCP server |
| **Citations** | Every fact links to `agentii.ai/v/{ticker}/{citation_id}/{page}` — clickable, verifiable, inline-after-fact + TUI Key Citations block |
| **Workspace Memory** | `agentii.md` index, per-ticker outputs with YAML frontmatter, `snapshots/` synthesis with a structured `claim_class` field, `sessions/` archive |
| **Contracts** | **34** shared contracts in `contracts/` — single source of truth for retrieval protocol, citations, office tooling, preflight, memory, and tracing |
| **Instant Data** (spec 039) | `data-tools/` — zero-key-first macro/market/earnings tools behind `~~category` placeholders, AGENT_CONTRACT envelope, file cache + failover; opt-in `setup_credentials.py` wizard for free API keys |
| **Enrichment & Quality** (spec 039) | `skill-registry.yaml` + `scripts/enhance-skill.py` (YAML workflow presets) + `scripts/quality-scan.py` (5-dimension 0–10 score, CI gate) |
| **Packaging** (spec 039) | `packaging/export.py` emits 4 host variants — claude-code, codex, cowork, generic-cli — from the canonical SKILL.md (diff-clean, placeholders preserved) |

---

## Skills

**80 skills across 14 verticals.** Each is a `skills/agentii/<name>/SKILL.md` file with YAML frontmatter and markdown methodology — the single canonical artifact across all hosts. Thin `commands/*.md` wrappers ship for explicit `/agentii:skill-name` slash-command invocation.

| Vertical | Skills | What it covers |
|----------|:---:|----------------|
| **equity-research-core** | 9 | Company-level dimensions — quarterly results, business model, competition, growth strategy, secular trends, turnaround, risk, earnings sentiment, valuation methods |
| **models-and-pitches** | 9 | DCF, trading comps, 3-statement, LBO, SOTP, workbook audit, XBRL→Excel, pitch-deck, earnings-preview |
| **bio-pharm** | 15 | FDA catalysts, clinical-trial status, pipelines, med-sector analysis (spec 052) |
| **scenarios** | 10 | The spec-046 research kit — constitution, specify, plan, tasks, clarify, implement, converge, challenge, synthesize, full-equity-research |
| **quantitative-analysis** | 5 | Ratio analysis, PEG valuation, reverse DCF, DDM, residual income |
| **idea-generation** | 5 | Qualitative/quantitative screening, consensus-disconnect analysis, catalyst mapping, trade templates |
| **options-derivatives** | 5 | Options foundations, income strategies, volatility trading, technical execution |
| **business-intelligence** | 4 | Revenue decomposition, unit economics, what-if scenarios, operational KPIs |
| **industry-analysis** | 4 | Peer benchmarking, sector overview, competitive positioning, supply-chain map |
| **macro-strategy** | 4 | Regime detection, rate cycles, currency analysis |
| **portfolio-strategy** | 4 | Long/short equity, position sizing, portfolio hedging |
| **technical-analysis** | 4 | Institutional price-action methodologies |
| **risk-and-psychology** | 1 | Trading risk management and psychology |
| **trading-as-business** | 1 | Trading infrastructure, review discipline, capital |

### Start here

| Command | Description |
|---------|-------------|
| `/agentii:recent-quarter` | Quarterly P&L progression, margin drivers, EPS vs consensus, sequential momentum |
| `/agentii:dcf` | DCF with live formulas, WACC decomposition, sensitivity tables → `.xlsx` |
| `/agentii:comps` | Trading comps with statistical benchmarking → `.xlsx` |
| `/agentii:3-statement` | Integrated IS/BS/CF with XBRL calculation-arc balancing → `.xlsx` |
| `/agentii:risk` | Regulatory, competitive, macro, and technology risk assessment |
| `/agentii:peer-bench` | Multi-ticker comparison, growth/value matrix, z-score ranking |
| `/agentii:pitch-deck` | 12–16 slide investment thesis presentation → `.pptx` |
| `/agentii:sector-overview` | TAM estimation, competitive concentration (HHI), regulatory landscape |
| `/agentii:constitution` | Scaffold a workspace's investment constitution (spec 046) |

All valuation skills support `--mode=scenario` for Bear/Base/Bull probability-weighted analysis.

> **Browse all 80**: the full registry with descriptions, modes and tool allow-lists is [`skill-registry.yaml`](./skill-registry.yaml). Methodology depth lives in per-skill `references/` directories (progressive disclosure) — the SKILL.md body stays lean (~700–900 words) and detail loads on demand. [Full methodology →](./contracts/skill-methodology-template.md)

---

## Governance & Research Modes

Spec 046 added the layer that makes the research *checkable* rather than merely generated. It is the largest recent body of work and it ships in the `scenarios` vertical.

### Two operating modes

| | **Thesis mode** | **Single-skill mode** |
|---|---|---|
| What it is | A governed research programme under `theses/{nnn}-{slug}/` | One skill against agentii.ai data, no thesis |
| Governance | `constitution.md` — or `agentii.md` where there is none | same |
| Work unit | the thesis | the skill run |
| Outputs | `artifacts/` | `{ticker}/{YYYY-MM-DD_HHMM}_{skill}_{affix}.md` |
| Memory | artifact frontmatter, **derived** | `agentii.md` (append-only index) |
| Sessions | `tasks.md` + `converge` | `sessions/INDEX.md` + transcripts |

**`agentii.md` has two roles, and the filesystem decides which.** With a `constitution.md` present it is a *chronicle* (a memory index, rotated per period). With none, **it is the constitution** — and rotating it would rotate away the project's principles. The detector reads the filesystem; it keeps no new state.

### The constitution

`/agentii:constitution` scaffolds a workspace's investment constitution: `constitution.md` (prose + SemVer amendment log), `constitution.yaml` (executable position/concentration constraints, budgets, regime drift triggers), plus `assumptions.yaml`, `value-checks.yaml` and `taxonomy.yaml`. Theses compile against a `constitution_pin`, so a stale pin is a hard failure rather than a silent drift.

### Gates, not vibes

Correctness is enforced by **dispatch preconditions and write-boundary gates**, not by the order in which an agent chooses to work:

- **G1 — deterministic**: pure script, millisecond, zero LLM. Citation integrity, numeric canonical form, `VACUOUS` reporting, evidence class.
- **G2 — judgement**: an independent-context validator sub-agent at phase boundaries.
- **G3 — human audit**: only the G1/G2 red items, via `theses/{nnn}-{slug}/checklists/*.md`.

A gate that did not run must **say so** (`mechanism_outcome: VACUOUS`) — an un-run gate that reports success is the failure mode the whole layer exists to prevent.

### Report pipeline

`pack → author → assemble → render`. Skills produce artifacts; the packer assembles them into a report input; the author writes `content.html` against a fixed outline; the assembler injects page furniture — headers, footers, page numbers, table of contents, and the **disclaimer page** — and the render step iterates on the rendered output rather than on the source.

---

## Office Output (Code-Mode + LibreOffice)

v3.3.0 continues Anthropic's proven code-mode architecture — no office MCP server. The agent writes self-contained Python scripts and executes them via `Bash`. [Full contract →](./contracts/office-tooling.md)

| Format | Library | Primary | Degraded Fallback |
|--------|---------|---------|-------------------|
| **Excel** | `openpyxl` + LibreOffice recalc | `.xlsx` with live formulas, named ranges, Checks tab | `.md` with full data tables |
| **PowerPoint** | `python-pptx` + LibreOffice validation | `.pptx` with one idea/slide, sourced footers | `.md` slide specification |
| **Word** | `python-docx` (available, deferred) | `.docx` for memo/IC-note deliverables | `.md` (default until memo skill ships) |

**Conventions** (mirroring Anthropic `xlsx-author`): blue font = hardcoded input, black = formula, green = cross-sheet link. A `Checks` tab carries TRUE/FALSE validation ties. LibreOffice headless (`soffice --headless`) handles recalculation and PDF export. The formulas-over-hardcodes invariant (`hardcoded_count == 0` for projection/discount/PV cells) is mandatory per FR-020.

**Layered preflight (FR-043)**: skills probe for a live Office session (Cowork `mcp__office__*` tools) first, then fall back to Python + LibreOffice, then degrade to `.md` with the exact `pip install` remediation command. Never a silent failure.

---

## Workspace Memory

A file-first hybrid memory architecture that persists context across sessions. After running skills, your workspace looks like this:

```
workspace/
├── constitution.md                     # Thesis-mode governance (spec 046); agentii.md where absent
├── agentii.md                          # Memory index — or THE constitution, if no constitution.md
├── style.md                            # Optional workspace overrides (currency, peers, verbosity)
├── NVDA/
│   ├── 2026-06-15_0930_recent-quarter_summary.md   # per-skill outputs, YAML frontmatter
│   └── 2026-06-15_1045_dcf_base.xlsx               # Office artifacts
├── snapshots/
│   └── NVDA/
│       └── 2026-06-15_thesis.md        # Point-in-time synthesis, restored on session start
├── sessions/
│   ├── INDEX.md                         # Session index (auto-loaded)
│   └── 2026-06-15/                     # Full transcripts (on-demand only)
├── _cross/                              # Multi-ticker analyses (peer-bench, comps, competitive-positioning)
│   └── semis_2026-06-15_1400_peer-bench_nvda-amd-avgo.md
└── _sector/                             # Pure sector/thematic analyses (names lowercase-hyphenated)
    └── tech-semiconductors/
        └── 2026-06-15_1500_sector-overview_summary.md
```

**Key conventions:**

- **`agentii.md`** — one file, **two roles**, decided by whether `constitution.md` exists: a *chronicle* (append-only memory index, rotated per period) or **the constitution itself** (principles, never rotated). Machine-parseable via `head -20`. Appended after every skill run; entries are never modified or deleted. [Schema →](./contracts/agentii-md-schema.md)
- **`{ticker}/`** — per-skill outputs. Frontmatter carries a **public core** required in both modes: `as_of` (the date the analysis is as-of), `skill`, `affix`, `key_metrics`, `conclusions`, `claims[]`, `mechanism_outcome`, plus `ticker` or `tickers`. [Schema →](./contracts/output-frontmatter-schema.md)
- **`snapshots/{ticker}/{YYYY-MM-DD}_{semantic-slug}.md`** — point-in-time synthesis (≤400 words) that states which prior conclusions are **confirmed**, **updated**, or **superseded**. The key is the **ticker, not the thesis id**, because a ticker always exists and a thesis id does not — thesis attribution lives in frontmatter, never in the path. [Contract →](./contracts/snapshot-synthesis.md)
- **Claim classification is a field, not a badge.** Every claim carries `claim_class ∈ {FACT, DEDUCTED, VIEW}`; the inline `[FACT]`/`[DEDUCTED]`/`[VIEW]` badges are **rendering from it**, and the field wins on disagreement. `facts_count` / `deducted_count` / `views_count` are **derived** from that list, never authored. The reason is that a gate which counts claims by reading prose has stopped being deterministic — which is the one thing a G1 gate must be.
- **Artifacts go to `artifacts/` in thesis mode only.** In single-skill mode there is no `artifacts/` to hold them, and `agentii.md` + `style.md` + `snapshots/` + `sessions/` keep their original behaviour.
- **`_cross/`** — multi-ticker outputs. **`_sector/`** — industry/thematic outputs with no primary ticker.
- **`sessions/`** — transcripts archived by date (not auto-loaded); `INDEX.md` is auto-loaded. [Format →](./contracts/session-format.md)

---

## Citations: Page-Accurate Provenance

Every material fact, table row, and metric in a deliverable is immediately followed by its clickable source link — not deferred to a bottom appendix. **Inline-first placement** is the package's core UVP.

```
Revenue grew 22% YoY to $215.9B [📄 NVDA 10-K p.42](https://agentii.ai/v/NVDA/sec173/42)
```

The bottom `## Citations` section provides a non-duplicative roll-up index. The closing TUI reply includes a **Key Citations** block — the headline 5–10 facts as clickable URLs, so you can cmd+click straight to the exact SEC page without opening the deliverable file.

**Citation format**: `https://agentii.ai/v/{ticker}/{citation_id}/{N}` — path-based, ~7 tokens, browser-redirects to the exact filing page. Earnings-call transcripts use the `ect<N>` id form.

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
│   OpenCode, etc) │     │  30 tools        │     │  Hono + Vercel     │
└─────────────────┘     └──────────────────┘     └────────┬───────────┘
                                                          │
                          ┌───────────────────────────────┤
                          │                               │
                    ┌─────▼──────┐                  ┌─────▼──────┐
                    │  Neon      │                  │  Redis     │
                    │  PostgreSQL│                  │  (Upstash) │
                    │  15.99M    │                  │  tracing   │
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

The skills are portable markdown following the open Agent Skills standard. What differs per host is the **install path**, and not every host has an adapter shipped in this repository:

| Host | Skills | Adapter config |
|------|:---:|----------------|
| Claude Code | ✅ | `adapters/claude-code/.mcp.json` |
| Claude Cowork | ✅ | `adapters/claude-cowork/connector.json` |
| Codex | ✅ | `adapters/codex/codex.json` |
| Goose | ✅ | `adapters/goose/profiles.yaml` |
| OpenClaw | ✅ | `adapters/openclaw/openclaw.json` |
| OpenCode | ✅ | **no adapter shipped yet** — the skills load from its skills directory; see [docs/install](./docs/install/) |

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

> **Two MCP transports.** The quick-start above uses the **hosted HTTP server** at `https://mcp.agentii.ai/mcp`. The files under `adapters/` configure the **stdio** package (`npx -y @agentii/investment-intelligence`) instead. Pick one deliberately — they are not the same process, and mixing them produces a confusing "tools not found".

See [`adapters/`](./adapters/) for per-host configuration files, and [`docs/install/`](./docs/install/) for step-by-step guides. All agents benefit from [`ai-agents.txt`](./ai-agents.txt) at the repo root.

---

## Making It Yours

- **Bring your templates** — mount firm-branded `.pptx` templates at `./templates/` for pitch-deck and earnings-preview
- **Adjust methodology** — edit `## Defaults` tables and `references/institutional-defaults.md`
- **Override via style.md** — per-workspace `style.md` overrides defaults for lookback quarters, reporting currency, peer universe, and output verbosity
- **Set your own limits** — `/agentii:constitution` writes the position caps, concentration limits and regime drift triggers a workspace is governed by
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
| Tools work in one host, not another | HTTP MCP configured in one, stdio npm in the other | See [For Other CLI Agents](#for-other-cli-agents) — pick one transport |
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
│   ├── agentii-plugin/                  # Meta-plugin: /agentii:* surface (70 symlinked skills)
│   ├── vertical-plugins/                # 14 verticals, 80 skills
│   │   ├── equity-research-core/        # 9   company dimensions
│   │   ├── models-and-pitches/          # 9   models + decks
│   │   ├── bio-pharm/                   # 15  FDA catalysts, trials
│   │   ├── scenarios/                   # 10  spec-046 research kit
│   │   ├── quantitative-analysis/       # 5
│   │   ├── idea-generation/             # 5
│   │   ├── options-derivatives/         # 5
│   │   ├── business-intelligence/       # 4
│   │   ├── industry-analysis/           # 4
│   │   ├── macro-strategy/              # 4
│   │   ├── portfolio-strategy/          # 4
│   │   ├── technical-analysis/          # 4
│   │   ├── risk-and-psychology/         # 1
│   │   └── trading-as-business/         # 1
│   └── agent-plugins/
│       └── agentii-equity-agent/        # Managed agent bundle
├── contracts/                           # 34 shared contracts (single source of truth)
├── data-tools/                          # Instant macro/market/earnings data (spec 039)
├── scripts/                             # CI gates, sync, validation, assembly, report pipeline
├── packaging/                           # 4 host export targets (spec 039)
├── docs/                                # install guides, architecture, CLI surfaces
├── adapters/                            # Per-host MCP config (5 hosts)
├── workflows/                           # Enrichment presets (spec 039)
├── style.md                             # Package-shipped formatting standard
├── skill-registry.yaml                  # 80 skills — the registry
├── QUICKSTART.md                        # Step-by-step walkthrough
├── README.md, LICENSE, NOTICE, CHANGELOG.md
└── SKILL.md                             # Root package manifest
```

---

## Contributing

Everything is markdown, YAML, and Python. Fork, edit, PR.

- **Read [QUICKSTART.md](./QUICKSTART.md) first** for a working install, and browse [`docs/`](./docs/) for the architecture notes.
- **Edit skills** in `plugins/vertical-plugins/<vertical>/skills/agentii/<name>/SKILL.md` — the single canonical source
- **Sync changes**: `python3 scripts/sync-agent-skills.py` then `bash scripts/assemble-agentii-namespace.sh`
- **Run `python3 scripts/check.py`** before pushing — validates all manifests, frontmatter, CI gates, and cross-file consistency
- Skills follow the open Agent Skills standard, supported by Claude Code, OpenCode, Codex, OpenClaw, Goose, and Claude Cowork

---

## Disclaimer

**This repository is software.** It does not provide investment, legal, tax, or accounting advice, and nothing it produces is a recommendation, an offer, or a solicitation to buy or sell any security.

The skills generate **analyst work product for review by a qualified professional**. Outputs are staged for human sign-off and are not intended to be acted on unreviewed. Any figure, valuation, model, or conclusion a skill produces may be incomplete, delayed, or wrong — it is derived from the sources cited inline, those sources may themselves be wrong, and the analysis may have misread them. No representation or warranty is made as to accuracy or completeness.

Statements about the future are forward-looking and inherently uncertain. Past performance is not indicative of future results. **You are responsible for your own due diligence** and should consult your own advisers before acting on anything produced with this software. The authors and distributors accept no liability for any loss arising from reliance on it.

Data is provided by agentii.ai and third-party sources under their own terms. Market data may be delayed. Coverage is not universal — skills surface a `data_freshness` warning and are designed to refuse rather than fabricate, but absence of a warning is not a guarantee of completeness.

> **Generated research outputs carry their own disclaimer.** Every presentation-shaped output — `thesis-report.html`, `dashboard.html`, `pitch-deck`, `earnings-preview` — must include the canonical block from [`plugins/vertical-plugins/scenarios/templates/disclaimer.md`](./plugins/vertical-plugins/scenarios/templates/disclaimer.md), which is the single authored source. It must be included verbatim, with placeholders filled; it is never restated, paraphrased, or forked, and `scripts/check_disclaimer.py` fails the build if it drifts.

See [`LICENSE`](./LICENSE) for the software licence and [`NOTICE`](./NOTICE) for attribution.

---

## License

Apache License 2.0 © agentii-ai. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

This package includes skills ported and optimized from [`anthropics/financial-services`](https://github.com/anthropics/financial-services) (Apache 2.0). Methodology bodies stay byte-stable from upstream; data-source blocks and tool calls are replaced with agentii-native equivalents.
