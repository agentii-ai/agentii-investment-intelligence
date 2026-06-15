# Quickstart — agentii-investment-intelligence v2.3.1

<p align="center">
  <strong>5 minutes to your first institutional-grade equity research report.</strong><br>
  No Rust toolchain. No Python virtualenv. No backend install.<br>
  One API key. One MCP server. 31 skills. All six CLI agents.
</p>

---

## 0. Prerequisites

- **Claude Code** (or OpenCode, Goose, Codex, OpenClaw, Cowork) — installed and working
- **Outbound HTTPS** to `mcp.agentii.ai` (the only network dependency)
- **macOS / Linux / Windows** — everything runs locally
- **Python 3.10+** (optional — only needed if you want Excel `.xlsx` or PowerPoint `.pptx` output)
- **LibreOffice 7.4+** (optional — for formula recalculation and PDF export)

---

## 1. Get an API Key

Visit **[agentii.ai/api-keys](https://agentii.ai/api-keys)** — 7-day free trial, 2,000 credits, no credit card required.

You'll receive a key that starts with `sk_live_`. Credits cover all MCP tool calls (SEC filings, XBRL facts, earnings calendar, real-time quotes). [Pricing →](https://agentii.ai/pricing)

---

## 2. Set Your API Key

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc) for persistence across sessions
export AGENTII_API_KEY=sk_live_YOUR_KEY_HERE

# Apply immediately in the current terminal
source ~/.zshrc
```

The key is referenced as `${AGENTII_API_KEY}` in all configuration — **never paste the literal value** into a config file. The only thing that leaves your machine is the `Authorization: Bearer` header on each MCP call.

---

## 3. Global MCP Setup (One-Time)

This registers the `agentii` MCP server so 30+ financial data tools auto-discover in every Claude Code session, from any directory.

```bash
claude mcp add-json --scope user agentii \
  '{"type":"http","url":"https://mcp.agentii.ai/mcp","headers":{"Authorization":"Bearer ${AGENTII_API_KEY}"}}'
```

Writes to `~/.claude.json`. Restart Claude Code.

<details>
<summary><strong>Verify MCP tools are loaded</strong></summary>

```bash
# In Claude Code:
> tools/list

# Expected: 30+ tools — search_xbrl_facts, search_documents, read_source_pages,
#           get_company_financials, search_earnings_calendar, get_realtime_quote, ...
```

</details>

---

## 4. Install Skills (Primary: Local Copy)

All 31 skills register under a **single flat namespace, `/agentii:skill-name`**. There is no `/equity-research-core:*` or `/models-and-pitches:*` surface — every skill is reached the same way regardless of which vertical authored it.

```bash
# From the agentii-investment-intelligence directory:
bash scripts/copy-skills-local.sh
```

This copies all 31 `SKILL.md` files into `.claude/skills/agentii/` and all 31 command wrappers into `.claude/commands/agentii/`. Restart Claude Code.

> **Why local copy instead of plugin install?** Claude Code v2.1.143 has a [known bug](https://github.com/anthropics/claude-code/issues/15178) where `claude plugin install` does not inject skills into the runtime. The local copy bypasses the plugin system entirely and works reliably on all Claude Code versions. When the bug is fixed, you can switch to `claude plugin install agentii@agentii-investment-intelligence` for the unified meta-plugin.

<details>
<summary><strong>Alternative: per-vertical plugin installs (not recommended)</strong></summary>

Installing verticals individually creates **additional** `/vertical:skill` namespaces alongside `/agentii:*`. Prefer the local copy above for a clean single namespace.

```bash
claude plugin marketplace add agentii-ai/agentii-investment-intelligence
claude plugin install equity-research-core    # adds /equity-research-core:* namespace
claude plugin install models-and-pitches       # adds /models-and-pitches:* namespace
# ... etc for other verticals
```

</details>

---

## 5. Office Output Setup (Optional)

Skills like `dcf`, `comps`, `3-statement`, `lbo`, `pitch-deck`, and `earnings-preview` produce real **`.xlsx`** and **`.pptx`** files — not just markdown tables. This works via **code-mode**: the agent writes a self-contained Python script and executes it through `Bash`. No office MCP server. No API calls for file generation. Everything happens locally.

### Install Python Libraries

```bash
pip install openpyxl python-pptx
```

### Install LibreOffice (for formula recalculation + PDF export)

```bash
# macOS
brew install --cask libreoffice

# Linux (Debian/Ubuntu)
sudo apt install libreoffice-calc libreoffice-impress

# Windows — download from https://www.libreoffice.org/download/
```

### Verify

```bash
python3 -c "import openpyxl; import pptx; print('OK')"   # Python libs
which soffice                                              # LibreOffice
```

### What Happens If You Skip This Step

Skills degrade gracefully — no silent failures. If `openpyxl` is missing when you run `/agentii:dcf NVDA`, the agent produces a `.md` file with full data tables, annotates `data_availability: degraded` and `openpyxl_missing: true` in the YAML frontmatter, and tells you the exact command to fix it:

```
Excel generation requires openpyxl. Install: pip install openpyxl
```

The `.md` fallback contains every number. You're never blocked — just missing the formatted workbook until you install the library.

### Office Output Architecture (Code-Mode + LibreOffice)

```
Retrieved XBRL Facts
       │
       ▼
┌─────────────────────────────────┐
│ 1. Agent writes _build_*.py    │  ← Self-contained openpyxl / python-pptx script
├─────────────────────────────────┤
│ 2. Bash: python3 _build_*.py   │  ← Execute, verify output exists
├─────────────────────────────────┤
│ 3. Bash: python3 recalc.py ... │  ← LibreOffice headless recalc (Excel only)
├─────────────────────────────────┤
│ 4. Audit: hardcoded_count == 0 │  ← Every projection cell is a live formula
└─────────────────────────────────┘
       │
       ▼
  ✅ Validated .xlsx / .pptx on disk
```

| Format | Library | Primary Output | Degraded Fallback | Skills |
|--------|---------|----------------|-------------------|--------|
| **Excel** | `openpyxl` + LibreOffice | `.xlsx` with blue/black/green fonts, named ranges, Checks tab | `.md` with full data tables | `dcf`, `comps`, `3-statement`, `lbo`, `xlsx-financials` |
| **PowerPoint** | `python-pptx` + LibreOffice | `.pptx` with one idea/slide, sourced footers | `.md` slide specification | `pitch-deck`, `earnings-preview` |
| **Word** | `python-docx` (available, deferred) | `.docx` for memo/IC-note deliverables | `.md` (default until memo skill ships) | — (future) |

[Full office contract →](./contracts/office-tooling.md)

---

## 6. Verify Installation

```bash
# Smoke test: run your first research command
/agentii:recent-quarter LLY
```

**Expected**: a structured, citation-backed report lands at `LLY/{timestamp}_recent-quarter_summary.md`. Every material fact is immediately followed by a clickable source link:

```
Revenue grew 22% YoY to $215.9B [📄 LLY 10-K p.42](https://agentii.ai/v/LLY/sec129/42)
```

The closing TUI reply includes a **Key Citations** block of clickable URLs — cmd+click straight to the exact SEC filing page without opening the deliverable file.

<details>
<summary><strong>What the workspace looks like after a few runs</strong></summary>

```
workspace/
├── agentii.md                          # Project memory index (auto-updated)
├── LLY/
│   ├── 2026-06-15_0930_recent-quarter_summary.md
│   ├── 2026-06-15_1045_dcf_base.xlsx
│   └── 2026-06-15_1100_business-model_structural.md
├── snapshots/
│   └── LLY/
│       └── 2026-06-15_thesis.md        # Auto-synthesized after ≥2 skills on same ticker
├── sessions/
│   ├── INDEX.md
│   └── 2026-06-15/                     # Full transcripts (on-demand)
├── _cross/                              # Multi-ticker analyses (peer-bench, comps)
└── _sector/                             # Pure sector/thematic analyses
```

Every `.md` output opens with a YAML frontmatter block (`ticker`, `date`, `skill`, `key_metrics`, `conclusions`, `facts_count`, `deducted_count`, `views_count`, `citation_count`). The `[FACT]`/`[DEDUCTED]`/`[VIEW]` taxonomy classifies every claim in snapshot thesis files.

</details>

---

## 7. Update Skills

When a new version of the package is released, update in place:

```bash
# 1. Pull the latest from GitHub
cd agentii-investment-intelligence
git pull origin main

# 2. Re-run the local copy to pick up changed skills
bash scripts/copy-skills-local.sh

# 3. If office dependencies changed, re-run the pip install
pip install --upgrade openpyxl python-pptx

# 4. Restart Claude Code
```

**Check your version**: look at the badge in [README.md](./README.md) or run:

```bash
grep '"version"' .claude-plugin/marketplace.json
```

**What changes between versions**: skills are pure markdown — `git pull` is all you need. MCP tools update server-side at `mcp.agentii.ai` (no action needed). Office Python libraries (`openpyxl`, `python-pptx`) follow their own release cycles — `pip install --upgrade` when prompted.

---

## 8. Skills at a Glance

All 31 skills invoke as `/agentii:skill-name`. Trigger phrases auto-activate them from natural language too.

| Vertical | Skills | Focus |
|----------|--------|-------|
| **equity-research-core** | `recent-quarter`, `business-model`, `competitive`, `growth-strategy`, `secular-trends`, `turnaround`, `risk`, `earnings-sentiment`, `valuation-methods` | Fundamental analysis |
| **models-and-pitches** | `dcf`, `comps`, `3-statement`, `lbo`, `sotp-valuation`, `audit-xls`, `xlsx-financials`, `pitch-deck`, `earnings-preview` | Valuation models + presentations |
| **quantitative-analysis** | `ratio-analysis`, `peg-valuation`, `reverse-dcf`, `ddm-valuation`, `residual-income` | Quantitative valuation |
| **business-intelligence** | `revenue-decomp`, `unit-economics`, `what-if`, `operational-kpi` | Operational analytics |
| **industry-analysis** | `peer-bench`, `sector-overview`, `competitive-positioning`, `supply-chain` | Industry + peer analysis |

All valuation skills support `--mode=scenario` for Bear/Base/Bull probability-weighted analysis.

---

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `/agentii:recent-quarter` shows "no command" | Skills not copied | Run `bash scripts/copy-skills-local.sh` then restart |
| `tools/list` shows 0 agentii tools | MCP not configured or key not set | Run the global MCP setup in step 3; verify `echo $AGENTII_API_KEY` |
| `${AGENTII_API_KEY}` not expanded | Env var set after Claude Code started | Restart Claude Code after `export AGENTII_API_KEY=...` |
| `✘ not authenticated` / `AGENTII_AUTH_REQUIRED` | Key expired or invalid | Check at [agentii.ai/api-keys](https://agentii.ai/api-keys) |
| `AGENTII_CREDITS_EXHAUSTED` | Trial credits used | Regenerate key or upgrade at [agentii.ai](https://agentii.ai) |
| `list_xbrl_concepts` returns empty | Concept name format | Try "Revenues" not "Revenue", "NetIncomeLoss" not "Net Income" |
| Ticker not found | Non-canonical ticker | Three-layer resolution handles aliases (GOOGL→GOOG, BRK.B→BRK.A) |
| `.xlsx` not produced | `openpyxl` not installed | `pip install openpyxl` — skill produces `.md` fallback with exact command |
| `.pptx` not produced | `python-pptx` not installed | `pip install python-pptx` — skill produces `.md` slide spec with exact command |
| LibreOffice recalc fails | LibreOffice not installed or wrong version | `brew install --cask libreoffice` (macOS) or `apt install libreoffice-calc` (Linux) |
| `data_freshness` warning on ticker | < 100% coverage in launch cohort | Partial data surfaced transparently; no fabrication |
| Sector/domain mismatch | Clinical skill invoked on a tech ticker | Skill refuses with a structured explanation — by design |

---

## 10. Next Steps

- **Read the full [README](./README.md)** — architecture, workspace memory, citation format, pricing, coverage
- **Review the [office contract](./contracts/office-tooling.md)** — code-mode Excel/PowerPoint/Word conventions
- **Skim the skill catalog** — every `plugins/vertical-plugins/<vertical>/skills/agentii/<name>/SKILL.md` is a self-contained methodology
- **Set up a workspace `style.md`** — override default lookback quarters, reporting currency, peer universe, and output verbosity per project
- **Chain skills**: `dcf → pitch-deck` for end-to-end model-to-deck workflows; `xlsx-financials → audit-xls` for quality assurance
- **Read the [CHANGELOG](./CHANGELOG.md)** for what changed in v2.3.1
- **Report issues** at [github.com/agentii-ai/agentii-investment-intelligence](https://github.com/agentii-ai/agentii-investment-intelligence)

---

<p align="center">
  <strong>One API key. One MCP server. 31 skills. Zero infrastructure.</strong><br>
  <a href="https://agentii.ai">agentii.ai</a>
</p>
