# Changelog

All notable changes to `agentii-investment-intelligence`.

## [Unreleased]

### Fixed
- **X-Agentii-Trace contract pair reconciled with the deployed behaviour** — `contracts/x-agentii-trace-header.md`
  and `contracts/x-agentii-trace-delivery.md` to v1.1 (spec 060). v1.0 described a mechanism that was
  never running: a Redis-counter `run_id` mint (the MCP runs with **no environment variables** and no
  shared store, so no counter can exist there), a `depth` and `user_id` the caller sends (both are
  platform values — FR-131 forbids trusting a depth, and accepting an identity from a caller would let
  a client attribute its calls to another account), and a durable table that received no rows (the
  lineage is a column set on `usage_logs`). Anyone implementing from the old text re-created the defect
  it documented, which is why this is a contract change and not a doc tidy.
- **The tracing instruction now states the carry — in every place an agent reads it** (2026-09-23, spec 060's
  eleventh pass). The contract pair above was corrected and **five sources that teach agents kept the
  retired story**: "The MCP server will inject run_id, depth, and user_id automatically"
  (`contracts/skill-methodology-template.md`, `scripts/dev/complete-scaffolds.py`, the cookbook's subagent
  prompt, the shipped agent prompt `contracts/preflight.md` names as canonical, and
  `contracts/mcp-canonical.json`'s trace note). The mechanism depends on the opposite: the run id is minted
  once at `initialize`, arrives as `_run_id` in **every** tool result, and the **caller** sends it onward —
  the proxy's session id lives in one instance's memory, so a conversation that does not carry its own id
  fragments into several runs, and a sub-agent that does not declare `parent=` leaves the call tree flat.
  Measured across the 70 shipped skills before the fix: **zero** mentioned `_run_id`, `parent=` or
  `instance=`, and four different pointer shapes were in use. `scripts/dev/trace_instruction_v1_1.py`
  converges them (keeping each skill's own clause), the two generators that write new skills emit the same
  sentence, and the shipped agent prompt carries the full lifecycle. Verified by the sibling implementation
  the same day: a real `tools/call` now lands `agent=mcp:search_companies`, and a parent/child/sibling
  sequence archives as `depth` 0→1→1 with `instance=dcf-2`.

### Changed
- **CI Check 19 now asserts the pair's substance rather than its existence**: the named durable store,
  the five-field hot-tier member tuple, the absence of the removed per-call mint, and the absence of
  caller-supplied `depth`/`user_id` in the wire format. It was run against the pre-amendment files
  first and failed with 7 issues — the evidence that it has teeth.
- **CI Check 18 now asserts the instruction, not a keyword** (2026-09-23). Its first version passed a
  `## Preflight` block that merely *mentioned* `X-Agentii-Trace` or `_run_id` — which is how the retired
  sentence above stayed green in every skill while teaching that the server supplies what the caller must
  carry. It now requires the **carry** in every Preflight, forbids the retired mechanism in every Preflight
  *and* in the four canonical sources, and requires the three generators to emit the template's pointer
  sentence verbatim ("one sentence, four writers", checked). `tests/test_check_18_trace_instructions.py`
  pins all of it — seven cases, six of them mutations that must fail the check.

### Not in this release
- **No kit version bump, and no mirror propagation.** The pair has exactly **one copy**: the export
  mechanism (`packaging/export.py`) propagates *skills* into `packaging/targets/` and has never covered
  `contracts/`, so there are no mirrors to sync and nothing to re-export. Bumping the version is a
  release action, and the archive half of spec 060 (US3–US5) is not built — asserting a new version
  would claim a capability the repository does not have. The pair carries its own v1.1 heading, which
  is where a reader looks first.

## [3.3.0] — 2026-09-19 — spec 046 Governance + Report Pipeline

### Added
- **Governance layer** (`scenarios` vertical, spec 046): `agentii.constitution` scaffolds a
  workspace's investment constitution — `constitution.md` (prose + SemVer amendment log),
  `constitution.yaml` (executable position/concentration constraints, budgets, regime drift
  triggers), plus `assumptions.yaml`, `value-checks.yaml`, `taxonomy.yaml`. Theses compile
  against a `constitution_pin`, so a stale pin is a hard failure rather than silent drift.
- **Two operating modes**, deliberately coexisting: *thesis mode* (a governed research
  programme under `theses/{nnn}-{slug}/`, outputs to `artifacts/`) and *single-skill mode*
  (one skill against agentii.ai data, no thesis). `agentii.md` has **two roles**, decided by
  the filesystem: a chronicle when `constitution.md` exists, **the constitution itself** when
  it does not — where rotating it would rotate away the project's principles. `agentii_cmd
  singleskill scaffold` creates the single-skill instrument set, which had no entry point before.
- **Report pipeline** (spec 046): `pack → author → assemble → render`. Artifacts are packed
  into a report input; the author writes `content.html` against a fixed outline; the assembler
  injects page furniture — headers, footers, page numbers, TOC, and the disclaimer page — and
  the render step iterates on rendered output rather than source.
- **Disclaimer system** (spec 046): a single authored source at
  `scenarios/templates/disclaimer.md`, gated for the four presentation-shaped outputs
  (`thesis-report.html`, `dashboard.html`, `pitch-deck`, `earnings-preview`). The clause set —
  not the wording — is the contract, and `scripts/check_disclaimer.py` fails the build on drift
  or on a forked copy.
- **Gate tiers G1/G2/G3**: G1 is deterministic (pure script, millisecond, zero LLM — citation
  integrity, numeric canonical form, evidence class); G2 is an independent-context validator
  sub-agent at phase boundaries; G3 is human audit of red items only. A gate that did not run
  must report `mechanism_outcome: VACUOUS`; an un-run gate that reports success is the failure
  mode the layer exists to prevent.
- **New verticals**: `bio-pharm` (15 skills, spec 052), `scenarios` (10, the spec-046 kit),
  `idea-generation` (5), `options-derivatives` (5), `macro-strategy` (4),
  `portfolio-strategy` (4), `technical-analysis` (4), `risk-and-psychology` (1),
  `trading-as-business` (1).

### Changed
- **Count corrections, applied where the count is a claim rather than a record.** The package
  is **80 skills across 14 verticals**, with **33 contracts** and **30 MCP tools**. The 2.4.0 entry
  below says "48 entries" and "48 skills total"; 48 was never the skill count — it is the number of
  addressable sub-prompt modes in `equity-research-core`. Historical entries are left as written;
  this line is the correction.
- **Version unified to 3.3.0.** Four values shipped simultaneously — `SKILL.md` and seven
  `plugin.json` files said 2.2.1, the README badge and QUICKSTART said 2.3.1, and the CHANGELOG's
  latest entry said 2.4.0. All package-level sites now read 3.3.0. The eight verticals at `0.1.0`
  are **independently versioned** and are left alone: they have never had a 1.0, and moving them
  to 3.3.0 would assert a release history they do not have.
- **README rewritten** as the landing page: the broken `demo.gif` hero removed (the file was never
  committed), the self-contradictory figures reconciled (`15.99M` vs `4.17M` XBRL facts; `20+` vs
  `30+` tools; `48` vs `31` vs `80` skills), the 14-row vertical table replacing per-skill tables
  that listed 31 of 80, and a **Disclaimer** section added.

### Fixed
- **`check_disclaimer.py` was invoked by nothing.** It was correct, and it was Q139's named
  enforcement point — but no test module and no CI step ran it, so the disclaimer was gated only
  in principle. It is now a CI step, and `check_*.py` orphanhood is itself gated (Check 48).
- **The spec-matrix separator parsed as a task.** `parse_spec_matrix` skipped only the literal
  `---` while `spec-template.md` emits `|-------|`, so every scaffolded thesis carried a phantom
  task. Fixed structurally rather than by extending a list of literals.
- **The revoked snapshot key survived in a generator.** `spec-template.md` still emitted
  `snapshots/{nnn}-{slug}/YYYY-MM-DD_thesis.md`; every thesis scaffolded afterwards inherited it.
- **Three contracts still carried the retired `_thesis.md` filename** (`memory-load.md`,
  `session-format.md`, `agentii-md-schema.md`) after Q144 replaced it — the same defect as the one
  that had already been corrected in a sibling file.
- **22 cross-reference labels across 7 shipped documents** had been silently emptied to `****` by a
  lossy transform. Recovered from the commits that predate it, not guessed.
- **The Chinese-firewall premise retired from the probe harness.** The provider registry and
  `contracts/SOURCES.md` had been corrected to put it out of scope (users are in the US and the EU);
  `data-tools/source_probe.py` still asserted *"Yahoo geo-blocks this network"* and labelled its
  licence `(geo-blocked)`. `GEO_BLOCK` and `RATE_LIMITED` are now separate outcomes.

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
