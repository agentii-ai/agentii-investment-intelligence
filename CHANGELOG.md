# Changelog

All notable changes to `agentii-investment-intelligence`.

## [2.4.0] — 2026-07-17 — spec 039 Enhance Skills

### Added
- **Skill registry + quality system** (Part I): `skill-registry.yaml` (48 entries) with `scripts/_registry.py` atomic API, `scripts/sync-registry.sh` bootstrap, `check.py` **Check 30** (registry↔disk bijection) + license-boundary sub-check (AGPL/GPL denylist for the MIT core). (FR-008–FR-012)
- **Workflow-driven enrichment**: `scripts/enhance-skill.py` runs YAML presets (`workflows/*.yaml`: strategy/case/setup/quality-audit/comprehensive), idempotent knowledge-frameworks writer (dedupe by `citation_id`), chaining with history threading, `--from-registry` batch, contract-preservation guard, rollback-on-score-regression. (FR-001–FR-007, FR-024, FR-025)
- **5-dimension quality score**: `scripts/quality-scan.py` → registry; `--threshold` CI gate (warn-only until spec-037 enrichment), `--fix` remediation. (FR-013–FR-017)
- **spec-037 knowledge bridge**: `scripts/knowledge_bridge.py` — preset→query mapping, runtime `search_by_analogue` axis selection, graceful `coverage_gap`. (FR-018–FR-023)
- **Instant financial/macro data** (Part II): `data-tools/` — `macro_data.py`/`market_data.py`/`earnings_data.py` (`~~macro_data`/`~~market_data`/`~~earnings_data`), envelope-first + zero-key-first (`_envelope.py`/`_cache.py`/`_sources.py`), opt-in `setup_credentials.py` wizard, `mcp_adapters.py` 4-tool surface. OpenBB/wbdata out-of-process only (Constitution VIII).
- **Course-derived skills** (Part III): `scripts/srt-to-skill.py` (IP-safe SRT→SKILL.md, paraphrase-guard + attribution) + `scripts/scaffold_vertical.py`. 4 new verticals + 3 existing-vertical skills — **48 skills total**.
- **Multi-platform packaging** (Part IV): `packaging/export.py`/`export.sh` + `skillseekers.config.yaml` emit codex/cowork/generic-cli variants from canonical SKILL.md, diff-clean, placeholders preserved.

### Fixed
- `assemble-agentii-namespace.sh` hardcoded only 5 verticals — 3 pre-existing verticals (macro-strategy, options-derivatives, portfolio-strategy) were never assembled into the meta-plugin. Now enumerates all 12.
- `run-existing-validators.sh` failed on macOS (no `timeout` binary) — added portable `timeout`/`gtimeout`/none fallback.

## [2.3.0] — 2026-06-15

### Added
- **Code-mode office output**: Excel (openpyxl), PowerPoint (python-pptx), and Word (python-docx, available-but-optional) via `Bash` + LibreOffice headless recalc. Retired the unbuilt `agentii-office` MCP. (FR-040–FR-045)
- **Workspace memory architecture**: `agentii.md` index, YAML frontmatter on all outputs (`key_metrics`, `conclusions`, `facts_count`/`deducted_count`/`views_count`), `snapshots/{ticker}/` Tier-2 thesis files with `[FACT]`/`[DEDUCTED]`/`[VIEW]` taxonomy, `sessions/{YYYY-MM-DD}/` archive. (FR-087–FR-095)
- **Citation provenance**: Inline-first `/v/` clickable links after every material fact, `### Key Citations` block in TUI summary (0–10 URLs), non-duplicative roll-up index. (FR-081)
- **Data-source priority ordering**: XBRL facts first → SEC filings → web search last resort, embedded in preflight routing. (FR-075)
- **Snapshot auto-trigger**: Automatic synthesis after ≥2 skills run on same ticker in a session, with `--no-snapshot` override. (FR-091)
- **Flat `agentii:` namespace**: All 31 skills invoke as `/agentii:skill-name`. Vertical plugins retained for subset installs. (FR-014d)
- **Marketplace CI enforcement**: `check.py` validates marketplace.json version, skill count, and plugin resolution. (FR-001)

### Changed
- **Business-model decontamination**: Fixed `references/prompts/1/` dimension lineage (root cause of `NVDA-recent-quarter/` output bug). Temporal scope broadened to 4 quarters. XBRL-first protocol ordering. The original `essentials.yaml` dimension file was absorbed into the SKILL.md body.
- **Office output fixes**: `xlsx-financials` now produces actual `.xlsx` workbooks (was `.md` description only). `pitch-deck`/`earnings-preview` upgraded to `.pptx` primary output with `.md` as degraded fallback. Stale `xlsx.build`/`pptx.build` references replaced with `Bash`+openpyxl/python-pptx.
- **Deliverable Chain standardization**: `3-statement`/`dcf`/`lbo`/`comps` expanded to full FR-066 format (Inputs → Build → Validate → Output → Next).
- **retrieval.md co-location**: Symlinked into all 5 vertical plugin directories for CLI install resolvability.
- **Boilerplate dedup**: Agent Call Tracing blocks and `!curl` preflight probes replaced with `contracts/` pointers across all skills.

### Fixed
- 7 critical production bugs: `NVDA-recent-quarter/` directory contamination, `xlsx-financials` no-xlsx-output, 4 stale office-tool references, `pitch-deck`/`earnings-preview` missing `.pptx` path and `Bash`.
- 16 CI failures in Deliverable Chain format validation (FR-066 compliance).

## [2.2.2] — 2026-06-14

### Fixed
- Credential contract alignment with spec 024 FR-011f.
- Count reconciliation: 31 skills / 5 verticals documented consistently.
- marketplace.json version bump and metadata updates.

## [2.2.1] — 2026-06-13

### Added
- Unified `agentii` meta-plugin (FR-014d).
- 31 command files restored as thin delegation wrappers (FR-014k reversed).
- 3 CI enforcement gates (Checks 19–21): namespace, Output File, Output Structure.

## [2.2.0] — 2026-06-12

### Added
- 31 skills across 5 verticals: equity-research-core (9), business-intelligence (4), industry-analysis (4), models-and-pitches (9), quantitative-analysis (5).
- Agent plugin (`agentii-equity-agent`) with system prompt ported from `system_v2_7.py`.
- Three-layer agent-use-ready retrieval protocol (Document Discovery → Page Map → Deep Read).
- Path-based citation links (`https://agentii.ai/v/{ticker}/{citation_id}/{N}`).
