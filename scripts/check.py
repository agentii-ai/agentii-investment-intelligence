#!/usr/bin/env python3
"""
Lint all plugin + managed-agent manifests and verify cross-file references.

Ported and extended from anthropics/financial-services/scripts/check.py
(Apache 2.0) with 14 mandatory checks per spec 023 FR-014a/b, FR-020a/b, FR-054, FR-010, FR-052b
(checks 13 + 14 added per Round 4 Q12 + Q15; checks 19–22 added per Phase 10
agentic-search mechanisms FR-056, FR-058, FR-060, FR-064):

  1.  YAML parse all *.yaml under managed-agent-cookbooks/.
  2.  JSON parse all plugin.json / marketplace.json / steering-examples.json /
      *.schema.json contract files.
  3.  agent.md frontmatter has name + description.
  4.  Reference resolution (system.file, skills[].path, skills[].from_plugin,
      callable_agents[].manifest).
  5.  Skill drift detection between agent-plugin bundles and vertical sources.
  6.  Agent prose `skill-name` references resolve to bundled skills.
  7.  Marketplace source paths resolve to directories with plugin.json.
  8.  Every managed-agent-cookbook has agent.yaml + README.md + steering-examples.json.
  9.  Every SKILL.md has ## Output Structure + ## Error Handling.
  10. Every SKILL.md frontmatter has multi_ticker_semantics.
  11. Every SKILL.md has ## Defaults OR frontmatter `parameter_free: true`.
  12. Every SKILL.md has ## Triggers with ≥10 list items.
  13. Every vertical's .mcp.json `agentii` entry is byte-identical to
      contracts/mcp-canonical.json (FR-010, Round 4 Q15).
  14. RETIRED (2026-06-13, Phase 23) — all commands deleted per FR-014k.
  15–17. (Reserved for FR-044 protocol, pre-publish gate, essentials.yaml)
  18. Every SKILL.md ## Preflight section contains X-Agentii-Trace or
      _run_id instruction (FR-106g(c) / Phase 22 agent call tracing).
  19. Contracts x-agentii-trace-header.md and x-agentii-trace-delivery.md
      exist; mcp-canonical.json includes _trace_note (FR-106g(c) / Phase 22).
  20. Every SKILL.md has temporal_scope frontmatter block with valid
      default_quarters (1-20), max_quarters (>= default_quarters, <= 20),
      description (FR-058 / Phase 10 agentic search).
  21. Every SKILL.md has allowed_tools list with valid canonical tool names,
      office-plane tools only in models-and-pitches, structured_only skills
      exclude document tools (FR-060 / Phase 10).
  22. Every SKILL.md has three-layer protocol in ## Methodology OR
      valid retrieval_scope opt-out in frontmatter (FR-056 / Phase 10).
  23. Every SKILL.md ## Methodology has all 5 required subsections
      (FR-064 / Phase 10).
  24. Every models-and-pitches skill has references/{formula-sheet,
      validation-checklist, institutional-defaults}.md (FR-068 / Phase 11).
  25. Every models-and-pitches SKILL.md has ## Deliverable Chain with
      Inputs→Build→Validate→Output→Next flow (FR-066 / Phase 11).
  26. Every models-and-pitches SKILL.md has ## Validation Gates with
      3–5 concrete assertions (FR-067 / Phase 11).

Exit 0 if clean, 1 otherwise. Requires: pyyaml, jsonschema.
"""
import datetime
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
MANAGED = ROOT / "managed-agent-cookbooks"
CONTRACTS = ROOT / "contracts"

errors: list[str] = []
notices: list[str] = []
checked = 0

# ── T128: the measured surface of every check ───────────────────────────────
#
# `checked` is GLOBAL. A check that examines nothing adds nothing to it and
# reports no errors — which reads exactly like a clean result. That is Q105's
# defect (`VACUOUS`) at the level of the gate runner itself.
#
# Each section marks its surface on entry and counts every file it walks, so the
# delta between consecutive marks is that section's examined count.
#
# WHAT A ZERO MEANS, corrected 2026-09-21 (spec 058 T001/T002, FR-006): every
# section now counts, so a zero delta means the section genuinely walked an empty
# tree — not "forgot to report". A zero therefore FAILS the gate; it is no longer
# a warning. Before T001, 13 of 24 sections reported nothing and a zero was
# ambiguous between the two states. Section 4 ("reference resolution") is the
# case that motivated the correction: it read every managed-agent yml and counted
# none of them, reporting 0 while examining plenty.
#
# HISTORY — kept, because the stale version of this comment caused a real
# misdiagnosis. Check 32 previously carried its OWN copy of spec 046 Q34's rule
# in the literal `"/agentii." in text` form, which the corrected rule 3 calls
# unimplementable. It reported 0 findings over 48 files and **did not fire by
# luck**: the first `https://agentii.ai/v/...` citation added under `scenarios/`
# would have fired it falsely, and the same rule was implemented a second time in
# scripts/check_no_baked_harness_strings.py (URL-aware, verb-aware). **That was
# repaired on 2026-09-18** — the second copy is deleted and Check 32 delegates to
# that module, which reports its own surface (4,842 files scanned). Spec 058's
# Background §A read the old wording of this comment and recorded the *fixed*
# defect as open; the comment was the cause, which is why it is corrected here
# rather than deleted.
#
# Check numbers 14–17 are RECLAIMED (2026-09-21, spec 058 T003 / FR-007): 14 was
# retired and 15–17 reserved, so all four occupied the namespace while examining
# nothing. They are free for reuse and are not named in the surface table — the
# inventory is exactly the sections that examine something. Their old comments used
# to sit at what is now Check 18's block, INSIDE a counted region: a reclaim note is
# itself a naming of the reclaim, which is the thing FR-007 says not to count. Check
# 26 was never assigned (git log -S"Check 26" is empty); its absence is a numbering
# gap, not a lost check, and is recorded here so a later reader does not have to
# re-derive that.
#
# THREE STATES, not two (spec 058 T001/T002/T003, FR-006):
#
#   1. examined N > 0                      → normal
#   2. examined 0, declared pending        → reported, and FAILS on its expiry date
#                                            (contracts/pending.yaml, FR-054)
#   3. examined 0, conditional on an input → reported on EVERY run, and honoured only
#      that does not exist yet               while that input is genuinely absent
#
# State 3 exists because two checks are dormant by construction, not by neglect:
# Check 34 fires only when a workspace's `theses/INDEX.md` is committed, and Check 35
# needs a contract plus its implementation. Marking them pending would invent an owner
# and an expiry for work nobody owes; leaving them unmarked is what the 2026-09-21
# audit found nine blocks doing — reporting no surface at all, which reads exactly like
# a pass. A conditional declaration is honoured ONLY while its path is absent: if the
# path exists and the section still examined nothing, that is an error, so the state
# cannot be used to silence a section whose input is right there.
SURFACES: list[tuple[str, int, str, str | None]] = []


def _mark(name: str, note: str = "", conditional: str | None = None) -> None:
    """Record the surface examined so far. Called at each section header; the
    delta from the previous mark is that section's examined count.

    `conditional` names the repo-relative path whose absence explains a zero surface.
    See the three-states note above."""
    SURFACES.append((name, checked, note, conditional))


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    """Non-fatal notice. Used for phased migrations where the target state is not
    yet reachable (e.g. the spec-039 FR-034 allowed_tools migration)."""
    notices.append(msg)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)



# ── spec 058 T011 / FR-054: declared deferrals ──────────────────────────────
#
# Two states read identically from `checked` alone, and FR-006 only names one of them:
#
#   * a section that is BROKEN or unwired — it examines nothing because nothing is
#     wired to it. This MUST fail, and it does.
#   * a section whose INPUT does not exist yet — it examines nothing because there is
#     nothing to examine. Failing is wrong (the section is correct; its subject is
#     absent) and reporting clean is wrong (a vacuous section must never read as
#     productive). This file's business.
#
# `contracts/pending.yaml` is the third answer for the second state: a named owner, a
# reason, and a date after which the gate fails. See that file for the rules.
PENDING: dict[str, dict] = {}
_PENDING_CONSULTED: set[str] = set()
_PENDING_REQUIRED = ("id", "subject", "what", "owner", "expires", "reason")
_PENDING_FILE = CONTRACTS / "pending.yaml"
if _PENDING_FILE.is_file():
    try:
        _pdoc = yaml.safe_load(_PENDING_FILE.read_text()) or {}
    except yaml.YAMLError as _e:
        err(f"pending: {rel(_PENDING_FILE)}: {_e}")
        _pdoc = {}
    for _pe in _pdoc.get("pending") or []:
        _pmissing = [k for k in _PENDING_REQUIRED if not _pe.get(k)]
        if _pmissing:
            err(f"pending: entry {_pe.get('id', '?')!r}: missing "
                f"{', '.join(_pmissing)} — a deferral with no owner and no expiry is "
                f"how a temporary state becomes permanent (FR-054)")
            continue
        try:
            _pexp = datetime.date.fromisoformat(str(_pe["expires"]))
        except ValueError:
            err(f"pending: {_pe['id']}: expires={_pe['expires']!r} is not an ISO date "
                f"(FR-054)")
            continue
        if _pexp < datetime.date.today():
            err(f"pending: {_pe['id']} ({_pe['subject']}) EXPIRED {_pe['expires']} — "
                f"owner: {_pe['owner']}. Resolve it or re-declare with a new date "
                f"(FR-054).")
            continue
        PENDING[_pe["subject"]] = _pe


def _pending_covers(name: str) -> dict | None:
    """The pending declaration covering this section name, if any.

    Subjects are `check:<n>`; section marks are `8. …` or `Check 20: …`, so the match
    is on the leading number rather than the full string."""
    for _subj, _e in PENDING.items():
        _kind, _, _num = _subj.partition(":")
        if _kind != "check" or not _num.isdigit():
            continue
        if re.match(rf"^(Check )?{_num}([.:]|$)", name):
            _PENDING_CONSULTED.add(_subj)
            return _e
    return None
# --- 1. YAML parse ----------------------------------------------------------

_mark('1. YAML parse')
for yml in sorted(MANAGED.rglob("*.yaml")):
    checked += 1
    try:
        with open(yml) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(f"YAML parse: {rel(yml)}: {e}")

for yml in sorted(CONTRACTS.rglob("*.yaml")):
    checked += 1
    try:
        with open(yml) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(f"YAML parse: {rel(yml)}: {e}")

# --- 2. JSON parse ----------------------------------------------------------

_mark('2. JSON parse')
json_globs = [
    ".claude-plugin/marketplace.json",
    "plugins/**/.claude-plugin/plugin.json",
    "plugins/**/.mcp.json",
    "managed-agent-cookbooks/*/steering-examples.json",
    "contracts/*.json",
    "contracts/*.schema.json",
    "plugins/vertical-plugins/*/contracts/*.json",
    "managed-agent-cookbooks/*/contracts/*.json",
]
for pat in json_globs:
    for jf in sorted(ROOT.glob(pat)):
        checked += 1
        try:
            json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            err(f"JSON parse: {rel(jf)}: {e}")

# --- 3. agent.md frontmatter -----------------------------------------------

_mark('3. agent.md frontmatter')
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    checked += 1
    text = md.read_text()
    if not text.startswith("---"):
        err(f"frontmatter: {rel(md)}: missing leading ---")
        continue
    try:
        _, fm, _ = text.split("---", 2)
        meta = yaml.safe_load(fm)
        for k in ("name", "description"):
            if k not in meta:
                err(f"frontmatter: {rel(md)}: missing '{k}'")
    except (ValueError, yaml.YAMLError) as e:
        err(f"frontmatter: {rel(md)}: {e}")


# --- 4. reference resolution -----------------------------------------------

_mark('4. reference resolution')
def check_refs(yml: Path) -> None:
    try:
        data = yaml.safe_load(yml.read_text()) or {}
    except yaml.YAMLError:
        return
    base = yml.parent
    sys_spec = data.get("system")
    if isinstance(sys_spec, dict) and "file" in sys_spec:
        p = (base / sys_spec["file"]).resolve()
        if not p.is_file():
            err(f"ref: {rel(yml)}: system.file -> {sys_spec['file']} (not found)")
    for s in data.get("skills") or []:
        if isinstance(s, dict) and "path" in s:
            p = (base / s["path"]).resolve()
            if not p.exists():
                err(f"ref: {rel(yml)}: skills.path -> {s['path']} (not found)")
        if isinstance(s, dict) and "from_plugin" in s:
            p = (base / s["from_plugin"]).resolve()
            if not (p / "skills").is_dir():
                err(f"ref: {rel(yml)}: skills.from_plugin -> {s['from_plugin']} (no skills/ dir)")
    for c in data.get("callable_agents") or []:
        if isinstance(c, dict) and "manifest" in c:
            p = (base / c["manifest"]).resolve()
            if not p.is_file():
                err(f"ref: {rel(yml)}: callable_agents.manifest -> {c['manifest']} (not found)")


for yml in sorted(MANAGED.rglob("*.yaml")):
    checked += 1  # 4. reference resolution
    check_refs(yml)

# --- 5. agent-plugin bundled skills match vertical source ------------------

_mark('5. agent-plugin bundled skills match vertical source')
import filecmp

# Keyed by skill name under the agentii namespace (skills/agentii/<name>/).
src_by_name = {p.name: p for p in PLUGINS.glob("vertical-plugins/*/skills/agentii/*") if p.is_dir()}
for bundled in sorted(PLUGINS.glob("agent-plugins/*/skills/agentii/*")):
    checked += 1  # 5. bundled skills
    if not bundled.is_dir():
        continue
    src = src_by_name.get(bundled.name)
    if not src:
        err(f"bundled-skill: {rel(bundled)}: no vertical source named '{bundled.name}'")
        continue
    cmp = filecmp.dircmp(src, bundled)
    if cmp.diff_files or cmp.left_only or cmp.right_only:
        err(f"bundled-skill: {rel(bundled)}: drifted from {rel(src)} (run sync-agent-skills.py)")

# --- 6. agent.md skill references -------------------------------------------

_mark('6. agent.md skill references')
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    checked += 1  # 6. agent.md skill references
    slug = md.parents[1].name
    sk_dir = PLUGINS / "agent-plugins" / slug / "skills" / "agentii"
    bundle = {p.name for p in sk_dir.iterdir() if p.is_dir()} if sk_dir.is_dir() else set()
    for ref in set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", md.read_text())):
        if ref in src_by_name and ref not in bundle:
            err(
                f"agent-prose: {rel(md)}: references `{ref}` but "
                f"plugins/agent-plugins/{slug}/skills/{ref}/ is not bundled"
            )

# --- 7. marketplace source paths resolve ------------------------------------

_mark('7. marketplace source paths resolve')
mp = ROOT / ".claude-plugin" / "marketplace.json"
if mp.is_file():
    for p in json.loads(mp.read_text()).get("plugins", []):
        checked += 1  # 7. marketplace
        src = (ROOT / p["source"]).resolve()
        if not (src / ".claude-plugin" / "plugin.json").is_file():
            err(f"marketplace: {p['name']} source -> {p['source']} (no plugin.json)")

# --- 8. required files per managed-agent-cookbook ---------------------------

_mark('8. required files per managed-agent-cookbook')
# Cookbooks are populated in Phase 7 (US7). At Phase 1, a cookbook directory
# may exist with only `contracts/` and `subagents/` subdirs and no agent.yaml.
# Treat the cookbook as "populated" only once agent.yaml exists at the root.
for d in sorted(MANAGED.iterdir()):
    if not d.is_dir():
        continue
    if not (d / "agent.yaml").is_file():
        continue  # not yet populated — declared pending (check:8) in contracts/pending.yaml
    # The surface is the cookbooks VALIDATED, not the directories walked. An earlier
    # version counted every directory, which made this section report 1 while
    # validating 0 — a vacuous section reading as productive, which is the defect
    # FR-006 exists to catch (spec 058 U2, found by the Phase-1 analysis).
    checked += 1
    for req in ("agent.yaml", "README.md", "steering-examples.json"):
        if not (d / req).is_file():
            err(f"missing: {rel(d)}/{req}")

# --- 9-12. SKILL.md structural checks ---------------------------------------

_mark('9-12. SKILL.md structural checks')
# Skills live under the unified `skills/agentii/<name>/` namespace (Phase 23,
# FR-014c/e). Globs MUST target that depth — `skills/*/SKILL.md` matches the
# namespace dir, not the skills, and silently validates zero files.
SKILL_FILES = sorted(PLUGINS.glob("vertical-plugins/*/skills/agentii/*/SKILL.md")) + \
              sorted(PLUGINS.glob("agent-plugins/*/skills/agentii/*/SKILL.md")) + \
              sorted(PLUGINS.glob("agentii-plugin/skills/agentii/*/SKILL.md"))


# spec 046 Q25 (consequence #4): kit/orchestrator bodies are workspace meta-commands
# and DAGs, not ticker analyses — the ticker-specific structure checks below do not
# apply to them (three body types → three validators). Check 30's registry↔disk
# bijection still covers them; the role-based validator split is the design.
def _meta_role(sk: Path) -> bool:
    try:
        text = sk.read_text(encoding="utf-8")
    except OSError:
        return False
    if not text.startswith("---"):
        return False
    try:
        _, fm, _ = text.split("---", 2)
        return (yaml.safe_load(fm) or {}).get("role") in ("kit", "orchestrator")
    except (ValueError, yaml.YAMLError):
        return False


SKILL_FILES = [sk for sk in SKILL_FILES if not _meta_role(sk)]

# Self-test: the gate must never silently match zero skills again. If this
# fires, the namespace layout changed and the globs above need updating.
MIN_EXPECTED_SKILLS = 55
if len(SKILL_FILES) < MIN_EXPECTED_SKILLS:
    err(
        f"check-config: SKILL_FILES glob matched {len(SKILL_FILES)} files "
        f"(expected >= {MIN_EXPECTED_SKILLS}) — skill-level checks would be a "
        f"no-op. Verify the skills/agentii/<name>/SKILL.md namespace layout."
    )

for sk in SKILL_FILES:
    checked += 1
    text = sk.read_text()
    # parse frontmatter
    meta = {}
    if text.startswith("---"):
        try:
            _, fm, body = text.split("---", 2)
            meta = yaml.safe_load(fm) or {}
        except (ValueError, yaml.YAMLError) as e:
            err(f"skill-frontmatter: {rel(sk)}: {e}")
            continue
    else:
        err(f"skill-frontmatter: {rel(sk)}: missing leading ---")
        continue

    # Check 9: ## Output Structure + ## Error Handling
    if "## Output Structure" not in text:
        err(f"skill-structure: {rel(sk)}: missing '## Output Structure' (FR-020a)")
    if "## Error Handling" not in text:
        err(f"skill-structure: {rel(sk)}: missing '## Error Handling' (FR-020b)")

    # Check 10: multi_ticker_semantics in frontmatter
    mts = meta.get("multi_ticker_semantics")
    valid_mts = {"single_target", "target_with_optional_peers", "target_with_required_peers", "basket_v1_1"}
    if mts not in valid_mts:
        err(
            f"skill-mts: {rel(sk)}: multi_ticker_semantics '{mts}' invalid "
            f"(must be one of {sorted(valid_mts)}) (FR-054)"
        )

    # Check 11: ## Defaults OR parameter_free: true
    if "## Defaults" not in text and not meta.get("parameter_free", False):
        err(
            f"skill-defaults: {rel(sk)}: missing '## Defaults' table "
            f"and frontmatter parameter_free is not true (FR-014b)"
        )

    # Check 12: ## Triggers with ≥10 items (scaffold may have 0; warn only if section exists with <10)
    trig_match = re.search(r"## Triggers\s*\n(.*?)(?=\n##|\Z)", text, flags=re.DOTALL)
    if trig_match:
        trig_body = trig_match.group(1)
        items = re.findall(r"^\s*[-*]\s+\S+", trig_body, flags=re.MULTILINE)
        if items and len(items) < 10:
            err(
                f"skill-triggers: {rel(sk)}: '## Triggers' has {len(items)} items "
                f"(need ≥10 per FR-014a)"
            )

# --- Check 13: vertical .mcp.json agentii entry == mcp-canonical.json --------

_mark('Check 13: vertical .mcp.json agentii entry == mcp-canonical.json')
MCP_CANONICAL = CONTRACTS / "mcp-canonical.json"
if MCP_CANONICAL.exists():
    try:
        canonical = json.loads(MCP_CANONICAL.read_text())
        canonical_agentii = canonical.get("agentii")
    except json.JSONDecodeError as e:
        err(f"mcp-canonical: {rel(MCP_CANONICAL)}: invalid JSON: {e}")
        canonical_agentii = None
    if canonical_agentii:
        for vertical_dir in (PLUGINS / "vertical-plugins").glob("*/"):
            mcp_path = vertical_dir / ".mcp.json"
            if not mcp_path.exists():
                err(
                    f"mcp-replication: {rel(vertical_dir)}: missing .mcp.json "
                    f"(FR-010 / Round 4 Q15 — every vertical must replicate canonical agentii entry)"
                )
                continue
            checked += 1
            try:
                vertical_mcp = json.loads(mcp_path.read_text())
            except json.JSONDecodeError as e:
                err(f"mcp-replication: {rel(mcp_path)}: invalid JSON: {e}")
                continue
            servers = vertical_mcp.get("mcpServers", vertical_mcp)
            vertical_agentii = servers.get("agentii")
            if vertical_agentii != canonical_agentii:
                err(
                    f"mcp-replication: {rel(mcp_path)}: 'agentii' entry differs from "
                    f"contracts/mcp-canonical.json (FR-010 / Round 4 Q15 byte-equality)"
                )
else:
    err("mcp-canonical: contracts/mcp-canonical.json missing (FR-010 / Round 4 Q15)")

# --- Check 18: SKILL.md Preflight carries the tracing instruction AND the carry (FR-106g(c), spec 060) ---
# (The reclaimed numbers 14–17 and the never-assigned 26 are recorded at the SURFACES
#  definition above, not here: a reclaim note inside a counted region occupies the
#  inventory it declares empty — FR-007.)
#
# **Hardened 2026-09-23.** The first version asserted that a Preflight block *mentions*
# `X-Agentii-Trace` **or** `_run_id` — a keyword test. Under it, a block that taught the *retired*
# mechanism passed: "The MCP server will inject run_id, depth, and user_id automatically" (v1.0's
# story, removed by spec 060 D-22 because the proxy is a stateless thin proxy that mints nothing per
# call, and by FR-131/FR-204 because depth and identity never travel on the wire). Measured that day:
# 149 counted files, and the retired sentence still sat in **five** sources no check read — the
# authoring template, `scripts/dev/complete-scaffolds.py`, the cookbook's subagent prompt, the shipped
# agent prompt, and `contracts/mcp-canonical.json`'s trace note. So this check now asserts three
# things: (1) every Preflight states the **carry** — the run id is minted once at `initialize`, arrives
# as `_run_id` in every tool result, and the caller sends it onward; (2) no Preflight and no canonical
# source teaches the retired story; (3) the generators that write the pointer agree, verbatim, with the
# sentence the template declares — "one sentence, four writers" as a checked property.

_mark('Check 18: SKILL.md Preflight carries the tracing instruction AND the carry (FR-106g(c), spec 060 D-22)')

RETIRED_TRACE_RE = re.compile(
    r"inject\w*[^.\n]{0,60}run_?id|auto-?generat\w*[^.\n]{0,40}run_?id|depth\s*=\s*\{|user_?id\s*=\s*\{",
    re.IGNORECASE,
)

for sk in SKILL_FILES:
    checked += 1
    text = sk.read_text()
    preflight_match = re.search(r'## Preflight\n(.*?)(?=\n## )', text, re.DOTALL)
    if not preflight_match:
        err(f"agent tracing: {rel(sk)}: ## Preflight section not found")
        continue
    preflight = preflight_match.group(1)
    if '_run_id' not in preflight:
        err(
            f"agent tracing: {rel(sk)}: ## Preflight does not state the _run_id carry — the run id is "
            f"minted once at initialize and the CALLER sends it on every subsequent call (spec 060 D-22); "
            f"a pointer that names only the header is the instruction that lets one run fragment"
        )
    retired = RETIRED_TRACE_RE.search(preflight)
    if retired:
        err(
            f"agent tracing: {rel(sk)}: ## Preflight teaches the retired mechanism ({retired.group(0)!r}) — "
            f"the server injects nothing: run_id is caller-carried, depth is platform-derived, identity "
            f"comes from the API key (spec 060 D-22, FR-131, FR-204)"
        )

# ── The canonical sources: the text an agent actually reads, and the template the next skill is written from.
# The shipped agent prompt is named as canonical by `contracts/preflight.md`; the cookbook prompt is the
# kit's only subagent instruction; the template is what a future skill is authored against; the MCP
# declaration's trace note is contract text.
CANONICAL_TRACE_SOURCES = [
    (PLUGINS / "agent-plugins/agentii-equity-agent/agents/agentii-equity-agent.md", "the canonical agent prompt"),
    (CONTRACTS / "skill-methodology-template.md", "the authoring template"),
    (MANAGED / "agentii-equity-agent/subagents/system-prompts/retrieval.md", "the cookbook subagent prompt"),
    (CONTRACTS / "mcp-canonical.json", "the MCP declaration's trace note"),
]
for src, what in CANONICAL_TRACE_SOURCES:
    checked += 1
    if not src.exists():
        err(f"agent tracing: {what} missing: {rel(src)} (spec 060 FR-106g(c))")
        continue
    src_text = src.read_text()
    if '_run_id' not in src_text:
        err(f"agent tracing: {rel(src)} ({what}): does not state the _run_id carry (spec 060 D-22)")
    if 'parent' not in src_text:
        err(f"agent tracing: {rel(src)} ({what}): does not state that a spawned agent declares parent= (spec 060 D-2/D-23)")
    retired = RETIRED_TRACE_RE.search(src_text)
    if retired:
        err(
            f"agent tracing: {rel(src)} ({what}): still teaches the retired mechanism ({retired.group(0)!r}) — "
            f"spec 060 D-22/FR-131/FR-204 removed it"
        )

# ── The generators must write the template's sentence, or the next skill/export brings the old one back.
_template_text = (CONTRACTS / "skill-methodology-template.md").read_text()
_pointer_match = re.search(r"Include the `X-Agentii-Trace` header on every tool call[^\n]*", _template_text)
CANONICAL_POINTER = _pointer_match.group(0).strip() if _pointer_match else None
GENERATORS = [
    ROOT / "scripts/dev/trace_instruction_v1_1.py",
    ROOT / "scripts/scaffold_vertical.py",
    ROOT / "scripts/dev/complete-scaffolds.py",
    # Superseded for the pointer (it re-inserts its own pre-flight line, see its docstring) but its
    # constant is checked anyway: a file that *would* write the old pointer if run is exactly the kind
    # of landmine this check exists to keep defused.
    ROOT / "scripts/dev/ctx_opt_us2_preflight.py",
]
checked += 1
if CANONICAL_POINTER is None:
    err(
        "agent tracing: contracts/skill-methodology-template.md declares no canonical tracing pointer — "
        "the generators have nothing to agree with (spec 060 D-22)"
    )
else:
    for gen in GENERATORS:
        checked += 1
        if not gen.exists():
            err(f"agent tracing: generator missing: {rel(gen)}")
            continue
        if CANONICAL_POINTER not in gen.read_text():
            err(
                f"agent tracing: {rel(gen)}: writes a tracing pointer that differs from the template's — "
                f"expected the sentence in contracts/skill-methodology-template.md, verbatim "
                f"(run scripts/dev/trace_instruction_v1_1.py to converge the skills)"
            )

# --- Check 19: X-Agentii-Trace contract pair states the SHIPPED behaviour (FR-106g(c), spec 060 T024-T026) ---
#
# As written (v1.0 of this check) it asserted only that two files exist. Both files existed, both
# were frozen, and both described a mechanism the deployed MCP never had: a Redis-minted run_id,
# `agent_traces` as the durable store, and a per-call re-mint as "graceful degradation". The check
# passed the whole time. That is the same failure shape as the tracer itself — a gate that verifies
# presence while the behaviour drifts — so it now asserts the properties a reader implements from:
# the store that actually receives the row, the member tuple the hot tier actually holds, and the
# absence of the two behaviours spec 060 removed.
#
# Absence assertions are the load-bearing ones here. A contract that *adds* the new story while
# leaving the old paragraph in place still re-implements the dropped mint for anyone who reads it.

_mark('Check 19: X-Agentii-Trace contract pair states the shipped behaviour (FR-106g(c), spec 060 T024-T026)')

trace_header_md = CONTRACTS / "x-agentii-trace-header.md"
trace_delivery_md = CONTRACTS / "x-agentii-trace-delivery.md"
for contract_file in [trace_header_md, trace_delivery_md]:
    checked += 1
    if not contract_file.exists():
        err(f"agent tracing: {rel(contract_file)}: contract file missing (FR-106g(c))")

if trace_header_md.exists():
    header_text = trace_header_md.read_text()

    checked += 1
    if "usage_logs" not in header_text:
        err(f"agent tracing: {rel(trace_header_md)}: does not name usage_logs as the durable store (spec 060 D-1)")

    # The durable store the contract named before spec 060 was never written to. Naming it again — even
    # to say "the old one" — is how a reader ends up querying a table that does not exist.
    checked += 1
    if "agent_traces" in header_text:
        err(
            f"agent tracing: {rel(trace_header_md)}: still names the retired agent_traces table; "
            f"the record lands in usage_logs (spec 060 D-1)"
        )

    # The hot tier's member tuple. A reader reconstructing a tree from Redis needs this exactly: five
    # fields, in this order, with depth NOT among them (depth is derived, not stored — spec 060 D-28).
    checked += 1
    if "agent|parent|instance|endpoint|status" not in header_text:
        err(
            f"agent tracing: {rel(trace_header_md)}: the 5-field member tuple "
            f"`agent|parent|instance|endpoint|status` is not stated (spec 060 R-11)"
        )

    # FR-131: depth is auto-derived, never trusted from the header; FR-204: an identity is never
    # accepted from a caller. A format line that advertises either invites exactly what they forbid.
    checked += 1
    if re.search(r"depth=\{", header_text) or re.search(r"user_id=\{", header_text):
        err(
            f"agent tracing: {rel(trace_header_md)}: the caller-facing format still advertises "
            f"depth= or user_id= — both are platform-derived (FR-131, FR-204)"
        )

    # The pair must AGREE on who may supply `agent` (spec 060 D-26, added 2026-09-23). The delivery
    # contract gained the proxy-supplied actor (`agent=mcp:{tool_name}` where the caller declared none)
    # and this file still said "LLM agent" only — so the two halves of one mechanism described
    # different ones, which is the divergence D-26 exists to remove and the reason a reader cannot
    # resolve a conflict between them.
    checked += 1
    if "mcp:{tool" not in header_text:
        err(
            f"agent tracing: {rel(trace_header_md)}: does not state that the proxy supplies "
            f"`agent=mcp:{{tool_name}}` where the caller declared no agent, while "
            f"x-agentii-trace-delivery.md does (spec 060 D-26, D-16)"
        )

if trace_delivery_md.exists():
    delivery_text = trace_delivery_md.read_text()

    # Minted once per run, at initialize, and carried by the caller thereafter (spec 060 D-22). The
    # contract must say so positively: "the server will inject it" was the old story and it is false —
    # mcp-agentii has no env vars and no Redis, so nothing server-side can mint or remember an id.
    checked += 1
    if not re.search(r"mint\w*\s+once|once\s+per\s+run", delivery_text, re.I):
        err(f"agent tracing: {rel(trace_delivery_md)}: does not state that the run_id is minted once (spec 060 D-22)")

    checked += 1
    if re.search(r"\bINCR\b", delivery_text):
        err(f"agent tracing: {rel(trace_delivery_md)}: still documents the Redis INCR mint — removed (spec 060 D-22)")

    # The graceful-degradation paragraph re-minted a fresh id when one was missing. That is the defect
    # D-22 names, described as a feature. An absent id must record as untraced, never be invented.
    checked += 1
    if re.search(r"auto-?generat\w*", delivery_text, re.I):
        err(
            f"agent tracing: {rel(trace_delivery_md)}: still documents auto-generating a missing run_id; "
            f"a call without one is recorded untraced and is never given a fresh id (spec 060 D-22)"
        )

checked += 1
canonical_mcp = CONTRACTS / "mcp-canonical.json"
if canonical_mcp.exists():
    try:
        mcp_data = json.loads(canonical_mcp.read_text())
        if "_trace_note" not in mcp_data:
            err(f"agent tracing: {rel(canonical_mcp)}: missing _trace_note field (FR-106g(c))")
    except json.JSONDecodeError:
        err(f"agent tracing: {rel(canonical_mcp)}: invalid JSON")
else:
    err(f"agent tracing: {rel(canonical_mcp)}: file missing")

# --- Check 20: temporal_scope frontmatter field (FR-058) --------------------

_mark('Check 20: temporal_scope frontmatter field (FR-058)')
for sk in SKILL_FILES:
    checked += 1  # Check 20
    try:
        _, fm_text, _ = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    ts = meta.get("temporal_scope")
    if not isinstance(ts, dict):
        err(
            f"skill-temporal-scope: {rel(sk)}: missing 'temporal_scope' frontmatter block "
            f"(FR-058 — must have default_quarters, max_quarters, description)"
        )
        continue
    dq = ts.get("default_quarters")
    mq = ts.get("max_quarters")
    desc = ts.get("description")
    if not isinstance(dq, (int, float)) or dq < 1 or dq > 20:
        err(
            f"skill-temporal-scope: {rel(sk)}: default_quarters={dq} invalid "
            f"(must be 1-20) (FR-058)"
        )
    if not isinstance(mq, (int, float)) or mq < (dq or 1) or mq > 20:
        err(
            f"skill-temporal-scope: {rel(sk)}: max_quarters={mq} invalid "
            f"(must be >= default_quarters and <= 20) (FR-058)"
        )
    if not isinstance(desc, str) or len(desc.strip()) < 10:
        err(
            f"skill-temporal-scope: {rel(sk)}: description missing or too short "
            f"(FR-058 — human-readable rationale required)"
        )

# --- Check 21: allowed_tools frontmatter field (FR-060) ---------------------

_mark('Check 21: allowed_tools frontmatter field (FR-060)')
# Set of models-and-pitches skill names (office-plane tools allowed only here).
# Sourced from the vertical so it works for the flattened agentii-plugin copies.
_MODELS_AGENTII = PLUGINS / "vertical-plugins" / "models-and-pitches" / "skills" / "agentii"
MODELS_SKILL_NAMES = {
    p.name for p in _MODELS_AGENTII.iterdir()
    if p.is_dir() and (p / "SKILL.md").is_file()
} if _MODELS_AGENTII.is_dir() else set()
# Gather canonical MCP tool names from tool-name-map.json
CANONICAL_TOOLS: set[str] = set()
OFFICE_TOOLS = {"xlsx.build", "xlsx.recalc", "xlsx.evaluate", "xlsx.audit", "xlsx.convert", "pptx.build", "pptx.refresh", "pptx.edit", "xlsx.edit", "xlsx-read"}
DOCUMENT_TOOLS = {"read_source_outline", "read_source_deep_outline", "read_source_pages", "search_keyword_in_source", "search_documents", "search_sec_filings"}
# Full canonical surface: FR-011 MCP tools + office tools
FR011_TOOLS = {
    "search_clinical_trials", "search_xbrl_facts", "read_rendered_statement",
    "search_documents", "search_sec_filings", "get_sec_filing",
    "get_entity_knowledge", "read_source_pages", "search_keyword_in_source",
    "read_source_outline", "list_sources", "get_company_profile",
    "search_companies", "search_catalysts", "get_company_financials",
    "search_insider_trades", "search_biotech_news", "search_medical_devices",
    "get_homepage_summary", "search_earnings_calendar", "get_company_fiscal_calendar",
    "list_xbrl_concepts", "search_cross_period", "search_ipos",
    "get_stock_quote", "get_realtime_quote", "get_options_chain", "get_index_quotes",
    "search_stock_movers", "search_faers_events", "list_coverage",
    "get_ticker_coverage", "list_upcoming_earnings", "get_earnings_calendar_event",
    "list_domains", "search_unified",
    # Phase 24+ agentic-search surface (spec 019 FR-119 + batch primitive FR-051a)
    "read_source_deep_outline", "batch_search",
    # XBRL Part B statement/calculation surface (spec 019 P0)
    "get_statement", "get_statement_structure", "get_calculation_tree",
    "validate_calculation", "get_financial_ratios", "get_segment_data",
    # Spec 052 — med MCP layer (registered in mcp.js P0_TOOLS 2026-09-04)
    "get_clinical_trial", "search_fda_approvals", "get_fda_approval",
    "search_adcom_meetings", "get_adcom_meeting",
    "get_peer_comparison",
    # Spec 049 — med data surface (PDUFA/device calendars + drug/device universes)
    "get_upcoming_pdufa", "get_pdufa_decision", "get_device_decision",
    "search_universe_drugs", "search_universe_devices",
    "get_company_drugs", "get_company_devices",
    # Spec 055 — drug-knowledge + ACIP calendar surface (live in mcp.js P0_TOOLS)
    "search_drug_knowledge", "get_drug_knowledge",
    "search_drugs_by_target", "search_drugs_by_indication",
    "search_acip_events", "get_acip_event",
    "search_commercial_track", "get_ct_status_changes",
}
# Claude Code built-in tools usable by skills (e.g. xlsx-financials runs an
# openpyxl script via Bash per contracts/office-tooling.md).
BUILTIN_TOOLS = {"Bash"}
# Spec 037 knowledge-plane tools. This set MUST stay in sync with the tools
# deployed in the MCP proxy (agentii-ai/apps/mcp/api/mcp.js P0_TOOLS) — spec 039
# FR-034 requires each skill's allowed_tools to be a subset of the live surface.
KNOWLEDGE_CASE_TOOLS = {
    # cases
    "search_investment_cases", "get_investment_case",
    # strategies (spec 039 FR-034 migration target)
    "search_investment_strategies", "get_investment_strategy",
    # technical setups (L4 / execution layer)
    "search_technical_setups", "get_technical_setup",
    # cross-cutting analogue bridge (returns {cases, strategies} only — FR-032)
    "search_by_analogue",
    # knowledge entries (K1-K8 analytical frameworks — spec 037)
    "search_knowledge_entries", "get_knowledge_entry",
    # knowledge graph traversal
    "list_related_cases", "list_related_entries",
}
# Superseded by the spec-037 family above (spec 039 FR-034). Still accepted so the
# 35 un-migrated skills keep passing, but every use is reported as a notice.
# tasks.md T108 removes the last usage; T118 then promotes this to a hard error.
DEPRECATED_KNOWLEDGE_TOOLS = {
    # knowledge pipeline tools are now live in mcp.agentii.ai
    # deprecated mappings removed 2026-08-01 — use actual tool names directly
}
KNOWLEDGE_CASE_TOOLS.update(DEPRECATED_KNOWLEDGE_TOOLS)
CANONICAL_TOOLS.update(FR011_TOOLS)
CANONICAL_TOOLS.update(OFFICE_TOOLS)
CANONICAL_TOOLS.update(DOCUMENT_TOOLS)
CANONICAL_TOOLS.update(KNOWLEDGE_CASE_TOOLS)
CANONICAL_TOOLS.update(BUILTIN_TOOLS)
# Also load from tool-name-map for any missing
tnm_path = CONTRACTS / "tool-name-map.json"
if tnm_path.exists():
    try:
        tnm = json.loads(tnm_path.read_text())
        CANONICAL_TOOLS.update(tnm.get("system_v2_7", {}).values())
        if isinstance(tnm.get("mcp_tool_descriptions"), dict):
            CANONICAL_TOOLS.update(tnm["mcp_tool_descriptions"].keys())
    except (json.JSONDecodeError, KeyError):
        pass

for sk in SKILL_FILES:
    checked += 1  # Check 21
    try:
        _, fm_text, _ = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    at = meta.get("allowed_tools")
    if not isinstance(at, list) or len(at) < 1:
        err(
            f"skill-allowed-tools: {rel(sk)}: missing or empty 'allowed_tools' list "
            f"(FR-060 — must declare ~5-10 tools the skill uses)"
        )
        continue
    # Determine whether this is a models-and-pitches skill by NAME membership.
    # The agentii-plugin/agent-plugin copies flatten the vertical out of the
    # path, so the vertical can't be read positionally — match the skill name
    # against the set sourced from vertical-plugins/models-and-pitches/.
    is_models = (sk.parent.name in MODELS_SKILL_NAMES)
    rs = meta.get("retrieval_scope", "")
    for tool in at:
        if tool in DEPRECATED_KNOWLEDGE_TOOLS:
            warn(
                f"deprecated-tool: {rel(sk)}: '{tool}' is superseded by "
                f"'{DEPRECATED_KNOWLEDGE_TOOLS[tool]}' (spec 039 FR-034) — migrate via tasks.md T108"
            )
            continue
        if tool in CANONICAL_TOOLS:
            continue
        # Also accept office tools and tools in the MCP canonical + FR-011 list
        if tool in OFFICE_TOOLS or tool in DOCUMENT_TOOLS:
            CANONICAL_TOOLS.add(tool)  # lazily expand
            continue
        err(
            f"skill-allowed-tools: {rel(sk)}: tool '{tool}' not found in canonical "
            f"tool surface (FR-060)"
        )
    # office-plane tools only in models-and-pitches
    if not is_models:
        for tool in at:
            if tool in OFFICE_TOOLS:
                err(
                    f"skill-allowed-tools: {rel(sk)}: office-plane tool '{tool}' "
                    f"declared by non-models-and-pitches skill (FR-060)"
                )
    # structured_only skills exclude document-retrieval tools
    if rs == "structured_only":
        for tool in at:
            if tool in DOCUMENT_TOOLS:
                err(
                    f"skill-allowed-tools: {rel(sk)}: document-retrieval tool '{tool}' "
                    f"declared by retrieval_scope: structured_only skill (FR-060)"
                )

# --- Check 22: three-layer protocol presence OR retrieval_scope opt-out (FR-056) ---

_mark('Check 22: three-layer protocol presence OR retrieval_scope opt-out (FR-056)')
for sk in SKILL_FILES:
    checked += 1  # Check 22
    try:
        _, fm_text, _ = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    rs = meta.get("retrieval_scope")
    valid_rs = {"structured_only", "single_document", "simple_lookup", "unstructured_document_search"}
    has_layer1 = "read_source_outline" in sk.read_text()
    has_layer3 = "read_source_pages" in sk.read_text()
    has_protocol = has_layer1 and has_layer3
    if rs and rs not in valid_rs:
        err(
            f"skill-retrieval-scope: {rel(sk)}: retrieval_scope '{rs}' invalid "
            f"(must be one of {sorted(valid_rs)}) (FR-056)"
        )
    if not rs and not has_protocol:
        err(
            f"skill-retrieval-scope: {rel(sk)}: no retrieval_scope opt-out and "
            f"no three-layer protocol found in methodology (FR-056 — must contain "
            f"Layer 1→2→2.5→3 OR declare retrieval_scope)"
        )

# --- Check 23: methodology template subsection conformance (FR-064) ----------

_mark('Check 23: methodology template subsection conformance (FR-064)')
# Subsections may carry an optional ordinal prefix, e.g. "### 1. Retrieval Scope"
# (the canonical skill-methodology-template.md numbers them). Match both forms.
METHODOLOGY_SUBS = [
    "Retrieval Scope",
    "Retrieval Strategy",
    "Temporal Scope",
    "Tool Allowlist",
    "Protocol",
]
for sk in SKILL_FILES:
    checked += 1  # Check 23
    text = sk.read_text()
    if "## Methodology" not in text:
        err(
            f"skill-methodology: {rel(sk)}: missing '## Methodology' section "
            f"(FR-064 — all 5 subsections required: {', '.join(METHODOLOGY_SUBS)})"
        )
        continue
    for sub in METHODOLOGY_SUBS:
        if not re.search(rf"^###\s+(?:\d+\.\s+)?{re.escape(sub)}\b", text, re.MULTILINE):
            err(
                f"skill-methodology: {rel(sk)}: missing '### {sub}' subsection "
                f"under ## Methodology (FR-064 — skill-methodology-template.md)"
            )

# --- Check 24: models-and-pitches references/ directory (FR-068) -------------

_mark('Check 24: models-and-pitches references/ directory (FR-068)')
MODELS_DIR = PLUGINS / "vertical-plugins" / "models-and-pitches" / "skills" / "agentii"
REQUIRED_REFS = {"formula-sheet.md", "validation-checklist.md", "institutional-defaults.md"}
for sk_dir in sorted(MODELS_DIR.iterdir()) if MODELS_DIR.is_dir() else []:
    checked += 1  # Check 24a
    if not sk_dir.is_dir():
        continue
    if not (sk_dir / "SKILL.md").is_file():
        continue  # shared dirs (e.g. references/) are not skills
    refs_dir = sk_dir / "references"
    if not refs_dir.is_dir():
        err(f"skill-references: {rel(sk_dir)}: missing 'references/' directory (FR-068)")
        continue
    for req in REQUIRED_REFS:
        ref_file = refs_dir / req
        if not ref_file.is_file():
            err(f"skill-references: {rel(sk_dir)}: missing references/{req} (FR-068)")
        elif ref_file.stat().st_size < 50:
            err(f"skill-references: {rel(sk_dir)}: references/{req} is empty or too short (FR-068)")

# --- Check 24: models-and-pitches Deliverable Chain (FR-066) -----------------

_mark('Check 24: models-and-pitches Deliverable Chain (FR-066)')
for sk_md in sorted(MODELS_DIR.glob("*/SKILL.md")) if MODELS_DIR.is_dir() else []:
    checked += 1  # Check 24b
    text = sk_md.read_text()
    if "## Deliverable Chain" not in text:
        err(f"skill-chain: {rel(sk_md)}: missing '## Deliverable Chain' section (FR-066)")
        continue
    # Extract the chain section and verify it has the 5 sub-steps
    chain_match = re.search(r"## Deliverable Chain\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if chain_match:
        chain_body = chain_match.group(1)
        for step in ("Inputs", "Build", "Validate", "Output", "Next"):
            if step.lower() not in chain_body.lower() and step not in chain_body:
                # Check for common representations
                has_build = any(kw in chain_body for kw in ["xlsx_build", "pptx_build", "xlsx_audit", "pptx_edit"])
                has_chain = "→" in chain_body or "->" in chain_body
                if not (has_build and has_chain):
                    err(f"skill-chain: {rel(sk_md)}: Deliverable Chain missing '{step}' sub-step (FR-066)")

# --- Check 25: models-and-pitches Validation Gates (FR-067) ------------------

_mark('Check 25: models-and-pitches Validation Gates (FR-067)')
for sk_md in sorted(MODELS_DIR.glob("*/SKILL.md")) if MODELS_DIR.is_dir() else []:
    checked += 1  # Check 25
    text = sk_md.read_text()
    if "## Validation Gates" not in text:
        err(f"skill-gates: {rel(sk_md)}: missing '## Validation Gates' section (FR-067)")
        continue
    gates_match = re.search(r"## Validation Gates\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
    if gates_match:
        gates_body = gates_match.group(1)
        items = re.findall(r"^\s*\d+\.\s+\*\*", gates_body, re.MULTILINE)
        if len(items) < 3:
            err(f"skill-gates: {rel(sk_md)}: Validation Gates has {len(items)} items (need >= 3 per FR-067)")
        elif len(items) > 5:
            err(f"skill-gates: {rel(sk_md)}: Validation Gates has {len(items)} items (max 5 per FR-067)")

# --- Check 27: Namespace gate — no SKILL.md outside skills/agentii/ (FR-014e, Phase 23) ---

_mark('Check 27: Namespace gate — no SKILL.md outside skills/agentii/ (FR-014e, Phase 23)')
# Recursively enumerates every SKILL.md under any skills/ dir; fails if the file
# is not located under a skills/agentii/ namespace segment. Recursive glob is
# required so a stray skills/<name>/SKILL.md (old layout) is actually detected.
ALL_SKILL_MD_FILES = sorted(PLUGINS.glob("vertical-plugins/*/skills/**/SKILL.md")) + \
                     sorted(PLUGINS.glob("agent-plugins/*/skills/**/SKILL.md")) + \
                     sorted(PLUGINS.glob("agentii-plugin/skills/**/SKILL.md"))
for sk in ALL_SKILL_MD_FILES:
    checked += 1
    if "/skills/agentii/" not in sk.as_posix():
        err(
            f"skill-namespace: {rel(sk)}: SKILL.md outside skills/agentii/ namespace "
            f"— FR-014c/FR-014e namespace gate"
        )

# --- Check 50: Namespace gate, the other half — no directory WITHOUT a SKILL.md
#     (spec 046 Part III; found by the 2026-09-19 upgrade audit)
#
# Check 27 above catches a SKILL.md in the WRONG PLACE. This catches a directory
# in the RIGHT place with NO SKILL.md. They are exact complements, and the gap
# between them was invisible for as long as it existed:
#
#   * Check 27 globs `skills/**/SKILL.md`. A directory with no SKILL.md produces no
#     hit, so it cannot be found by a check that looks for SKILL.md files. Five such
#     directories were committed — four inside the install path, two of those a level
#     too high for the installer's loop to even reach.
#   * Check 30's own comment already says "shared dirs like .../agentii/references/
#     are NOT skills" — it EXCLUDES them from the registry comparison, so an orphan is
#     absent from both sides of the bijection and it passes. The exclusion is correct;
#     it was simply unguarded, and "correctly excluded" and "does not exist" are the
#     same thing to every check that was running.
#
# The cost was not cosmetic. A directory at `skills/agentii/<name>/` is enumerated as
# a skill by `copy-skills-local.sh` and `assemble-agentii-namespace.sh` (both walk
# `"$dir"/*/`), so orphans made directory enumeration report 82 while every SKILL.md
# glob reported 80 — and the diff between those two numbers is what a reader sees as
# "this skill is installed but missing".
_mark('Check 50: Namespace gate — no directory without a SKILL.md (spec 046)')

# (root, what a legitimate child of it is)
_NS_ROOTS = [
    (PLUGINS / "vertical-plugins", "skills/agentii"),      # children = skill dirs
    (PLUGINS / "vertical-plugins", "skills"),              # only legitimate child = agentii/
    (PLUGINS / "agent-plugins", "skills/agentii"),
]
_orphans: list[Path] = []
for _base, _suffix in _NS_ROOTS:
    for _root in sorted(_base.glob(f"*/{_suffix}")):
        checked += 1
        for _child in sorted(p for p in _root.iterdir() if p.is_dir()):
            if _suffix == "skills":
                # At the `skills/` level the ONE legitimate entry is the agentii
                # namespace. Anything else is the pre-Phase-23 layout or a stub.
                if _child.name == "agentii":
                    continue
            if not (_child / "SKILL.md").is_file():
                _orphans.append(_child)
if _orphans:
    for _o in _orphans:
        err(
            f"skill-namespace: {rel(_o)} is a directory in a skill namespace with no "
            f"SKILL.md — it is enumerated as a skill by copy-skills-local.sh and "
            f"assemble-agentii-namespace.sh, and skipped with a warning on every "
            f"install. Delete it, or move it out of the skills tree (Check 50)."
        )

# The duplicate-name half. `copy-skills-local.sh` keys its destination FLAT by name
# (`$SKILLS_DST/$skill_name`) and `sync-agent-skills.py` does `src_by_name[name] = src`,
# so two skills sharing a name would be a SILENT overwrite — whichever vertical is
# walked last wins, and nothing reports it. No collision exists today; this is the
# guard that keeps it that way, because the failure mode it prevents is invisible.
#
# Scoped to ONE source, and deduplicated by RESOLVED path. Both refinements came from
# this check's own false positives on its first two runs, and both are load-bearing:
#
#   * Dedup by resolved path: `agentii-plugin/skills/agentii/*` is a tree of SYMLINKS
#     into the verticals, so a naive scan sees every skill twice. Run 1 reported all 70
#     of them as duplicates. A symlink to a file IS that file.
#   * Scope to `vertical-plugins`: run 2 reported 9 collisions between
#     `equity-research-core/*` and `agent-plugins/agentii-equity-agent/*`. Those are
#     real second copies — but they are a SEPARATE DISTRIBUTION BUNDLE, not part of the
#     flat destination. `copy-skills-local.sh` walks only `vertical-plugins/*/skills/
#     agentii`, so an agent-plugin copy can never overwrite a vertical's. Flagging them
#     here would report drift — a genuine concern, but a different one — as a collision
#     that cannot happen, and the two would be fixed by different means.
#
# The question this half answers is narrow and decidable: **can two files race for one
# name at the flat destination?** Only the verticals can.
_SEEN_NAMES: dict[str, Path] = {}
for _sk in sorted(PLUGINS.glob("vertical-plugins/*/skills/agentii/*/SKILL.md")):
    checked += 1
    _name = _sk.parent.name
    _real = _sk.resolve()
    if _name in _SEEN_NAMES:
        if _SEEN_NAMES[_name] == _real:
            continue          # the same file reached through a symlink — not a collision
        err(
            f"skill-namespace: duplicate skill name '{_name}' — {rel(_SEEN_NAMES[_name])} "
            f"and {rel(_sk)} are two DIFFERENT files. The install destination is keyed "
            f"flat by name, so one would silently overwrite the other (Check 50)."
        )
    else:
        _SEEN_NAMES[_name] = _real

# --- Check 51: Command coverage — every kit/orchestrator skill has a command file
#     (spec 046 Part III; found by the `/agentii:synthesize` report, 2026-09-19)
#
# A `role: kit|orchestrator` skill is a WORKSPACE meta-command: the user invokes it as
# `/agentii:<name>` to drive a thesis. That is what the role means, and the command file
# is what makes the name resolvable at all. So `commands/` has to carry one entry per
# kit skill.
#
# It carried 8 of 10. `synthesize` and `full-equity-research` had none, so
# `/agentii:synthesize` answered `No commands match` and the report step had no by-name
# entry point. Nothing reported it: `COMMAND_FILES` above is built and then used for
# exactly one thing — Gate 9's double-brace scan — so no check had ever compared the
# command set to the skill set. The convention held at 8/10 and was unenforced at 2/10.
#
# Scoped to kit/orchestrator roles, deliberately, and the scope is the honest part. The
# other 69 skills follow a DIFFERENT convention — a 9–12 line wrapper with
# `argument-hint` and a MODE_SYNTAX pointer — and 29 of them have no command at all,
# mostly because their vertical has no `commands/` directory yet. That is undecided
# scope, not a violation; asserting it here would fail the suite on a state nobody has
# ruled against. This check asserts only the rule that is actually a rule.
#
# The reverse direction IS universal, because an orphan command is unambiguous: it
# resolves to a skill that does not exist. Measured 2026-09-19: zero such commands, so
# this half currently guards rather than repairs.
_mark('Check 51: Command coverage — kit skill ⇒ command file (spec 046)')

_VP = PLUGINS / "vertical-plugins"
_KIT_SKILLS: dict[str, tuple[str, Path]] = {}
for _sk in sorted(_VP.glob("*/skills/agentii/*/SKILL.md")):
    checked += 1
    if _meta_role(_sk):
        _KIT_SKILLS[_sk.parent.name] = (_sk.relative_to(_VP).parts[0], _sk)

# Self-test, in the shape of MIN_EXPECTED_SKILLS above. This check reads a role and acts
# on the result; if the role reader broke, it would find nothing and report clean while
# examining nothing — Q105's defect at the level of the check itself.
MIN_EXPECTED_KIT_SKILLS = 8
if len(_KIT_SKILLS) < MIN_EXPECTED_KIT_SKILLS:
    err(
        f"check-config: the kit/orchestrator role scan matched {len(_KIT_SKILLS)} "
        f"skill(s) (expected >= {MIN_EXPECTED_KIT_SKILLS}) — Check 51 would examine "
        f"nothing. Verify that `role:` is still read from skill frontmatter."
    )

for _name, (_vertical, _sk) in sorted(_KIT_SKILLS.items()):
    _cmd = _VP / _vertical / "commands" / f"{_name}.md"
    if not _cmd.is_file():
        err(
            f"command-coverage: {rel(_sk)} declares role: kit|orchestrator but "
            f"{rel(_cmd)} does not exist — `/agentii:{_name}` cannot resolve, so the "
            f"skill has no by-name entry point. Write the 4-line wrapper the other kit "
            f"skills carry (Check 51)."
        )

for _cmd in sorted(_VP.glob("*/commands/*.md")):
    checked += 1
    _name = _cmd.stem
    _vertical = _cmd.relative_to(_VP).parts[0]
    if not (_VP / _vertical / "skills" / "agentii" / _name / "SKILL.md").is_file():
        err(
            f"command-coverage: {rel(_cmd)} resolves to `/{_vertical}:{_name}` (and to "
            f"`/agentii:{_name}` once namespaced), but no skill named '{_name}' exists "
            f"in that vertical — the command points at nothing (Check 51)."
        )

# --- spec 058 Check 52: artifact-frontmatter fields a gate reads must be declared ---
_mark('Check 52: artifact-frontmatter fields a gate reads must be declared (FR-037)')
# FR-037 / T015. Delegates, following Check 32's precedent — the rule is implemented
# once, in scripts/check_gate_fields.py, which is also runnable standalone and tested.
#
# Why it exists: `entity_claims` is read by five gates and absent from 128 artifacts of
# theses 001–003, so every cross-run contradiction check there was vacuous. Nothing
# reported it, because nothing compared what the gates read against what the contract
# declared. A gate whose input does not exist reports exactly what a satisfied gate
# reports — FR-037 is that comparison, made executable.
try:
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_gate_fields as _cgf
    _gf_problems, _gf_counts = _cgf.check_a()
    # 7 gate scripts read + every script in scripts/ re-read to DERIVE the gate population
    # (FR-037's `gates:` list is hand-maintained; check_gate_fields now computes what it
    # should contain from the code and fails on a mismatch — spec 058 audit).
    checked += _gf_counts["gates_scanned"] + _gf_counts.get("scripts_scanned", 0)
    for _gf_p in _gf_problems:
        err(_gf_p)
    for _gf_c in _gf_counts["declared_but_unread"]:
        warn(f"gate-fields: '{_gf_c}' is declared but read by no gate — a field recording "
             f"a condition that triggers nothing: consume it or remove it (Check 52)")
    for _gf_d in _gf_counts["declared_dynamic"]:
        # The message carries its own heading ("declared-dynamic read: … ACCOUNTED FOR");
        # prefixing it with a second one made the notice read as two claims.
        warn(f"gate-fields: {_gf_d}")
except Exception as _e:                       # noqa: BLE001
    err(f"check 52 could not run: {type(_e).__name__}: {_e} — a check that "
        f"cannot execute must say so, not pass (Q105)")

# --- spec 058 Check 53: no port sentinel, no placeholder dimension token (FR-045) ---
# The seven machine-ported equity-research-core skills carried
# `<!-- BEGIN port-dimension-prompts methodology + modes -->` in `SKILL.md` and its END twin
# in `references/modes.md`, plus **12 literal `dim` tokens** in their Triggers blocks, where
# a dimension name belongs — so the block read `- analyze dim competitive landscape`.
#
# Their producer is RETIRED (2026-06-13, FR-014c) and its body is not valid Python — a state
# `tests/test_write_boundary.py:107–133` already reports — so nothing will ever consume the
# sentinels again. They are dead weight in shipped skills. Measured 2026-09-21: T034 removed
# 84 tokens and 14 sentinels from the vertical tree, and T037 propagated that to the bundle.
#
# NARROW ON PURPOSE. `{ticker}`-style placeholders are LEGITIMATE in a SKILL.md — the file is
# an instruction, which is why `validate-citations.py` accepts them — so a general
# "unsubstituted variable" rule would fire on correct content. This matches exactly two
# things: the retired sentinel (either form) and the bare `dim` TOKEN at the start of a
# Triggers bullet. Both are unmistakeable; neither has a legitimate use.
_mark('Check 53: no port sentinel and no placeholder dimension token (FR-045)')
_PORT_SENTINEL = "port-dimension-prompts"
_DIM_TOKEN = re.compile(r"(?m)^\s*[-*]\s+(?:[a-z]+ )*\bdim\b")
for _sk in SKILL_FILES:
    checked += 1
    _t = _sk.read_text()
    if _PORT_SENTINEL in _t:
        err(f"ported-sentinel: {rel(_sk)}: carries the retired port sentinel "
            f"`{_PORT_SENTINEL}` — its producer is retired (FR-014c) and nothing consumes "
            f"it, so a shipped skill must not carry it (FR-045)")
    for _m in _DIM_TOKEN.finditer(_t):
        err(f"placeholder-token: {rel(_sk)}: {_m.group(0).strip()!r} — the literal `dim` "
            f"token is an unsubstituted placeholder in a Triggers bullet (FR-045)")
    # The END sentinel travelled with the mode sections into references/modes.md, so the
    # pair is checked as a pair: scanning SKILL.md alone would certify a clean skill whose
    # references still carried half of it.
    _modes = _sk.parent / "references" / "modes.md"
    if _modes.is_file():
        checked += 1
        if _PORT_SENTINEL in _modes.read_text(encoding="utf-8", errors="ignore"):
            err(f"ported-sentinel: {rel(_modes)}: carries the retired port sentinel — the "
                f"END half of the pair (FR-045)")

# --- spec 058 Check 54: every analysis skill declares a section list (FR-044, FR-048) ---
# FR-048: the enforced core applies to every analysis skill that declares it — over the
# registry's 80 skills that is **70 analysis skills, all of them declaring ≥3 numbered
# elements in `## Output Structure` (floor 5, maximum 13)**. So there is no exception to
# tolerate, and a check written to tolerate one would be tolerating something that does not
# exist. FR-044 is the other half: a skill whose `references/output-structure.md` enumerates
# no sections MUST NOT be treated as having a declared structure — it declares NOTHING, and
# that state is reported here rather than passed over.
#
# THE EXEMPTION IS BY DECLARED ROLE, never by absence, and it is already made: line 402
# filters SKILL_FILES with `_meta_role(sk)`, so the 9 kit and 1 orchestrator skills — which
# have no `## Output Structure` section at all — are outside this population by their own
# declaration. Exempting them for LACKING the section would exempt a broken analysis skill
# for exactly the same reason, which is the defect this check exists to remove.
#
# Self-test in the shape of MIN_EXPECTED_SKILLS: if the role filter broke, the population
# would collapse and this check would report clean while examining nothing.
_mark('Check 54: every analysis skill declares a section list (FR-044, FR-048)')
NUM_MIN_ELEMENTS = 3
MIN_EXPECTED_ANALYSIS = 60          # measured 2026-09-21: 70 analysis + 9 bundle copies
_OUT_BLOCK = re.compile(r"(?m)^## Output Structure\s*\n(.*?)(?=\n## |\Z)", re.DOTALL)
_NUMBERED_ELEMENT = re.compile(r"(?m)^\s*\d+\.\s+\S")
if len(SKILL_FILES) < MIN_EXPECTED_ANALYSIS:
    err(f"check-config: SKILL_FILES holds {len(SKILL_FILES)} file(s) (expected >= "
        f"{MIN_EXPECTED_ANALYSIS}) — Check 54 would be a no-op")
for _sk in SKILL_FILES:
    checked += 1
    _blk = _OUT_BLOCK.search(_sk.read_text())
    _n = len(_NUMBERED_ELEMENT.findall(_blk.group(1))) if _blk else 0
    if _n == 0:
        err(f"declares-nothing: {rel(_sk)}: `## Output Structure` enumerates no elements. "
            f"This is the 'the skill declares nothing and cannot be held to it' state "
            f"FR-044 says must be REPORTED rather than silently exempted — the skill needs "
            f"its section list, or an explicit record that it has none (FR-044, FR-048)")
    elif _n < NUM_MIN_ELEMENTS:
        err(f"declares-too-little: {rel(_sk)}: {_n} element(s) in `## Output Structure`; "
            f"the enforced floor is {NUM_MIN_ELEMENTS} and the measured corpus floor is 5 "
            f"(FR-048)")

# --- spec 058 Check 55: every script CI runs is exercised by a test (FR-003) ---
# Delegates, following Check 32/52's precedent: the rule is implemented once, in
# `scripts/check_script_coverage.py`, runnable standalone and tested.
#
# Why it belongs in THIS gate: measured 2026-09-21, seven CI-run scripts were reached by no
# test — and running them found that **two fail** (34 violations in
# `validate-multi-ticker-syntax.py`, one in `validate-prose-safety.py`) and a third passes
# having scanned zero files. `check.py` does not invoke those scripts, so the local gate was
# green while CI was red, which is this specification's defect class in its purest form.
_mark('Check 55: every CI-run script is exercised by a test (FR-003)')
try:
    import check_script_coverage as _csc
    _sc_problems, _sc_counts = _csc.check()
    # The surface is the CI-run scripts examined; a population that collapsed to nothing
    # would make this check pass without meaning anything (the delegate refuses that too).
    checked += len(_sc_counts["ci_run"])
    for _sc_p in _sc_problems:
        err(_sc_p)
except Exception as _e:                       # noqa: BLE001
    err(f"check 55 could not run: {type(_e).__name__}: {_e} — a check that cannot "
        f"execute must say so, not pass (Q105)")

# --- Check 28: Output File gate — every SKILL.md must have ## Output File (FR-014e, Phase 23) ---

_mark('Check 28: Output File gate — every SKILL.md must have ## Output File (FR-014e, Phase 23)')
for sk in SKILL_FILES:
    checked += 1  # Check 28
    text = sk.read_text()
    if "## Output File" not in text:
        err(
            f"skill-output-file: {rel(sk)}: missing '## Output File' section "
            f"(FR-079/FR-014e — must specify target file path with {{ticker}}, _cross/, or _sector/)"
        )
    else:
        # Extract ## Output File section content
        of_match = re.search(r"## Output File\s*\n(.*?)(?=\n## |\Z)", text, re.DOTALL)
        if of_match:
            of_body = of_match.group(1)
            if not re.search(r"\{ticker\}|_cross/|_sector/", of_body):
                err(
                    f"skill-output-file: {rel(sk)}: '## Output File' must contain "
                    f"{{ticker}}, _cross/, or _sector/ path template (FR-079/FR-014e)"
                )

# --- Check 29: Output Structure gate — ≥5 non-empty lines (FR-014e, Phase 23) ---

_mark('Check 29: Output Structure gate — ≥5 non-empty lines (FR-014e, Phase 23)')
for sk in SKILL_FILES:
    checked += 1  # Check 29 — walked the same SKILL_FILES Check 28 does; it counted
    #                none of them until 2026-09-21, so its row reported the NEXT two
    #                blocks' files (1 + 12) while claiming to be its own surface.
    text = sk.read_text()
    # Count non-empty lines between ## Output Structure and next ## heading
    structure_match = re.search(r"## Output Structure\s*\n(.*?)(?=\n## )", text, re.DOTALL)
    if structure_match:
        structure_body = structure_match.group(1)
        non_empty_lines = [l for l in structure_body.split("\n") if l.strip()]
        if len(non_empty_lines) < 5:
            err(
                f"skill-output-structure: {rel(sk)}: '## Output Structure' has "
                f"{len(non_empty_lines)} non-empty lines (need ≥5 per FR-014e)"
            )

# === Phase 28 (spec 023) Context-Optimization CI gates =====================
# Lock in the optimization end-state so drift cannot reappear.
import re as _re

COMMAND_FILES = sorted(PLUGINS.glob("vertical-plugins/*/commands/*.md"))

_mark('Phase 28: Context-Optimization CI gates 1–12 (spec 023 T057–T084)')


def _section(text: str, header: str) -> str:
    m = _re.search(rf"\n{_re.escape(header)}\s*\n(.*?)(?=\n## |\Z)", text, _re.DOTALL)
    return m.group(1) if m else ""


# Gate 1 (T057): tracing/preflight canonical strings live only in contracts (pointers in bodies)
for sk in SKILL_FILES:
    t = sk.read_text()
    if "first tool you call will return" in t:
        err(f"ctx-gate-tracing: {rel(sk)}: inline Agent Call Tracing block — use the contracts/x-agentii-trace-header.md pointer")
    if "https://mcp.agentii.ai/mcp/health" in t:
        err(f"ctx-gate-preflight: {rel(sk)}: inline MCP health probe — use the contracts/preflight.md pointer")

# Gate 2 (T024): tool-allowlist closure — already enforced for structured_only in Check 21.
# Here: every document-retrieval tool named in the Protocol/Tool-Fallbacks pointer
# context must be in allowed_tools when the body drives the three-layer protocol.
for sk in SKILL_FILES:
    try:
        _, fm_text, body = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    at = set(meta.get("allowed_tools") or [])
    for tool in DOCUMENT_TOOLS:
        # if the body actively instructs calling the tool (not just a pointer mention)
        if _re.search(rf"`{_re.escape(tool)}`", body) and tool not in at:
            err(f"ctx-gate-tool-closure: {rel(sk)}: body references `{tool}` absent from allowed_tools (FR-060 closure)")

# Gate 3 (T058): no stray 'Write to {ticker}' lines (## Output File is canonical)
for sk in SKILL_FILES:
    if _re.search(r"(?m)^Write to `?\{ticker\}", sk.read_text()):
        err(f"ctx-gate-output-path: {rel(sk)}: stray 'Write to {{ticker}}' line outside ## Output File")

# Gate 4 (T059): progressive disclosure — body word ceiling. Target is < 900;
# content-rich models skills (mandatory Deliverable Chain + Validation Gates) and
# business-model's correctness-critical Data-Source-Priority directive justify the
# 1300 ceiling. This still prevents the pre-optimization 2000-2700-word bloat.
CTX_MAX_BODY_WORDS = 1300
for sk in SKILL_FILES:
    parts = sk.read_text().split("---", 2)
    body = parts[2] if len(parts) == 3 else sk.read_text()
    wc = len(body.split())
    if wc > CTX_MAX_BODY_WORDS:
        err(f"ctx-gate-body-size: {rel(sk)}: body {wc} words exceeds {CTX_MAX_BODY_WORDS} (move detail to references/)")

# Gate 5 (T060): no legacy verbose / agent-only citation literals in skill markdown
for sk in SKILL_FILES:
    t = sk.read_text()
    if "/view?ticker=" in t:
        err(f"ctx-gate-citation: {rel(sk)}: legacy verbose /view?ticker= citation — use https://agentii.ai/v/{{ticker}}/{{citation_id}}/{{N}}")
    if "agentii://" in t:
        err(f"ctx-gate-citation: {rel(sk)}: agent-only agentii:// scheme in markdown — use the clickable /v/ form")

# Gate 6 (T061): contracts/ and references/ md references resolve
for sk in SKILL_FILES:
    t = sk.read_text()
    for ref in set(_re.findall(r"`(contracts/[A-Za-z0-9._/-]+\.md)`", t)):
        if not (ROOT / ref).is_file():
            err(f"ctx-gate-refs: {rel(sk)}: contracts reference `{ref}` does not resolve")
    for ref in set(_re.findall(r"`(references/[A-Za-z0-9._/-]+\.md)`", t)):
        if not (sk.parent / ref).is_file():
            err(f"ctx-gate-refs: {rel(sk)}: references reference `{ref}` does not resolve next to the skill")

# Gate 7 (T062): every skill references the shared memory/snapshot/output-frontmatter includes
for sk in SKILL_FILES:
    t = sk.read_text()
    for req in ("contracts/memory-load.md", "contracts/snapshot-synthesis.md", "contracts/output-frontmatter-schema.md"):
        if req not in t:
            err(f"ctx-gate-memory: {rel(sk)}: missing reference to {req} (FR-090/091/092)")

# Gate 8 (T063): temporal/identity consistency
for sk in SKILL_FILES:
    try:
        _, fm_text, body = sk.read_text().split("---", 2)
        meta = yaml.safe_load(fm_text) or {}
    except (ValueError, yaml.YAMLError):
        continue
    ts = meta.get("temporal_scope") or {}
    dq = ts.get("default_quarters") or 0
    low = body.lower()
    if dq and dq > 1 and ("1 fiscal quarter" in low or "most recent quarter" in low):
        if "insufficient" not in low and "never" not in low and "formerly" not in low:
            err(f"ctx-gate-temporal: {rel(sk)}: single-quarter language contradicts default_quarters={dq}")
    name = meta.get("name", sk.parent.name)
    of = _section(sk.read_text(), "## Output File")
    if name not in of and "_cross/" not in of and "_sector/" not in of:
        err(f"ctx-gate-identity: {rel(sk)}: ## Output File does not reference the skill's own name '{name}'")

# Gate 9 (T064): no double-brace literal placeholders in skills or commands
for f in list(SKILL_FILES) + list(COMMAND_FILES):
    if _re.search(r"\{\{[^}\n]+\}\}", f.read_text()):
        err(f"ctx-gate-placeholder: {rel(f)}: contains {{double-brace}} literal placeholder")

# Gate 10 (T065): citation surfacing — no weak tokens, Final Summary (TUI) present
for sk in SKILL_FILES:
    t = sk.read_text()
    if "{Citations}" in t or "{Source(s)}" in t:
        err(f"ctx-gate-citation-surface: {rel(sk)}: bare {{Citations}}/{{Source(s)}} placeholder in output template")
    if "cite source filing in standard agentii citation format at runtime" in t:
        err(f"ctx-gate-citation-surface: {rel(sk)}: vague _(cite … at runtime)_ hint in output template")
    if "## Final Summary (TUI)" not in t:
        err(f"ctx-gate-citation-surface: {rel(sk)}: missing '## Final Summary (TUI)' Key-Citations instruction")

# Gate 11 (T083): office-output format consistency
for sk in SKILL_FILES:
    t = sk.read_text()
    of = _section(t, "## Output File")
    os_sec = _section(t, "## Output Structure")
    if sk.parent.name == "xlsx-financials" and ".xlsx" not in of:
        err(f"ctx-gate-office-format: {rel(sk)}: xlsx-financials ## Output File must specify a .xlsx primary deliverable")
    if "deliverable is an `.xlsx`" in os_sec and ".xlsx" not in of:
        err(f"ctx-gate-office-format: {rel(sk)}: ## Output Structure claims .xlsx but ## Output File is not .xlsx")

# Gate 12 (T084): no stale abstract office tools in any body
for sk in SKILL_FILES:
    if _re.search(r"xlsx\.build|pptx\.build|pptx\.edit|pptx\.refresh", sk.read_text()):
        err(f"ctx-gate-office-tools: {rel(sk)}: stale abstract office tool (use contracts/office-tooling.md concrete path)")

# Surface for the whole block. Twelve gates re-read the same two collections, so this
# counts each file ONCE — the convention `_mark('9-12. SKILL.md structural checks')` (one
# mark, four sub-checks, 149 files) already established. Counting per traversal would
# report 1,839 here and inflate the gate total without telling a reader anything: the
# question a surface row answers is WHICH files were examined, not how many times.
checked += len({*SKILL_FILES, *COMMAND_FILES})

# --- Check 30: Registry Sync — bijection on-disk skills <-> skill-registry.yaml
#     (spec 039 Part I, FR-011/FR-012). A skill = a skills/agentii/<name>/ dir that
#     contains a SKILL.md (shared dirs like .../agentii/references/ are NOT skills).
REGISTRY_PATH = ROOT / "skill-registry.yaml"
_mark('Check 30: Registry Sync — bijection on-disk skills <-> skill-registry.yaml')
# self-test guard mirroring MIN_EXPECTED_SKILLS (baseline = 41 skills with SKILL.md)
MIN_EXPECTED_REGISTRY = 55
if REGISTRY_PATH.exists():
    checked += 1
    try:
        reg_doc = yaml.safe_load(REGISTRY_PATH.read_text()) or {}
        reg_entries = reg_doc.get("skills", [])
    except yaml.YAMLError as e:
        err(f"registry-sync: skill-registry.yaml: invalid YAML: {e}")
        reg_entries = None
    if reg_entries is not None:
        # schema validation (best-effort; jsonschema already a dependency)
        reg_schema_path = CONTRACTS / "skill-registry.schema.json"
        if reg_schema_path.exists():
            try:
                import jsonschema

                jsonschema.validate(reg_doc, json.loads(reg_schema_path.read_text()))
            except ImportError:
                pass
            except Exception as e:  # noqa: BLE001 - surface schema errors as check failures
                err(f"registry-sync: skill-registry.yaml: schema validation failed: {e}")

        on_disk = {
            sk.parent.name
            for sk in PLUGINS.glob("vertical-plugins/*/skills/agentii/*/SKILL.md")
        }
        registered = {e.get("skill_name") for e in reg_entries}

        if len(registered) < MIN_EXPECTED_REGISTRY:
            err(
                f"check-config: skill-registry.yaml has {len(registered)} entries "
                f"(expected >= {MIN_EXPECTED_REGISTRY}) — Check 30 would be a no-op. "
                f"Run scripts/sync-registry.sh."
            )
        for name in sorted(on_disk - registered):
            err(f"registry-sync: on-disk skill '{name}' has no skill-registry.yaml entry (FR-012); run sync-registry.sh")
        for name in sorted(registered - on_disk):
            err(f"registry-sync: registry entry '{name}' has no skills/agentii/{name}/ dir with SKILL.md (FR-011)")
else:
    err("registry-sync: skill-registry.yaml missing — run scripts/sync-registry.sh (FR-008)")

# --- Check 30b: License boundary — MIT core must not import copyleft (Constitution VIII)
#     Scans data-tools/*.py imports against an AGPL/GPL denylist (see contracts/SOURCES.md).
#     Copyleft sources (OpenBB, wbdata, ...) are reached out-of-process only.
COPYLEFT_DENYLIST = {"openbb", "openbb_terminal", "wbdata"}
DATA_TOOLS = ROOT / "data-tools"
_mark('Check 30b: License boundary — MIT core must not import copyleft (Constitution VIII)')
if DATA_TOOLS.exists():
    _import_re = re.compile(r"^\s*(?:import|from)\s+([a-zA-Z0-9_]+)", re.MULTILINE)
    for py in sorted(DATA_TOOLS.glob("*.py")):
        checked += 1
        for mod in set(_import_re.findall(py.read_text(encoding="utf-8"))):
            if mod in COPYLEFT_DENYLIST:
                err(
                    f"license-boundary: {rel(py)}: imports copyleft package '{mod}' into MIT core "
                    f"(Constitution VIII) — invoke it via subprocess/MCP instead (see contracts/SOURCES.md)"
                )

# --- spec 046 Check 33: taxonomy axis uniqueness (Q76) ----------------------
# Every value lives on exactly one axis. CI fails on a value appearing on two
# axes or on none — the closed-enum discipline that keeps eval corpora comparable.
_taxonomy_path = ROOT / "contracts" / "taxonomy.yaml"
_mark('Check 33: taxonomy axis uniqueness (Q76)')
try:
    _tax = yaml.safe_load(_taxonomy_path.read_text(encoding="utf-8")) or {}
    checked += 1
    _axes = _tax.get("axes") or {}
    _seen: dict[str, str] = {}
    for _axis, _values in _axes.items():
        if not isinstance(_values, list):
            err(f"taxonomy-axes: {rel(_taxonomy_path)}: axis '{_axis}' is not a list")
            continue
        for _v in _values:
            if not isinstance(_v, str) or not _v:
                err(f"taxonomy-axes: {rel(_taxonomy_path)}: axis '{_axis}' has a non-string value")
                continue
            if _v in _seen:
                err(f"taxonomy-axes: value '{_v}' appears on both '{_seen[_v]}' and "
                    f"'{_axis}' — the Q76 one-axis rule (Check 33)")
            _seen[_v] = _axis
except (OSError, yaml.YAMLError) as e:
    err(f"taxonomy-axes: {rel(_taxonomy_path)}: {e}")

# --- spec 046 Check 31: registry ↔ SKILL.md frontmatter sync (Q12) ----------
# Safety-critical, not tidiness: the dispatcher reads gates from the derived
# registry, so a stale registry means an out-of-date gate is silently in force.
_mark('Check 31: registry ↔ SKILL.md frontmatter sync (Q12)')
try:
    import sync_registry  # noqa: E402 — same-directory module

    _disk = {e["skill_name"]: e for e in sync_registry.build_entries()}
    # The surface is the SKILL.md files re-parsed to build the disk side, not the one
    # registry file compared against them — that is where the work and the risk are.
    checked += len(_disk)
    _reg = {s.get("skill_name"): s for s in
            (yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8")) or {}).get("skills", [])}
    for _name, _disk_entry in _disk.items():
        _reg_entry = _reg.get(_name)
        if _reg_entry is None:
            err(f"registry-sync: skill '{_name}' missing from skill-registry.yaml (Check 31 — run scripts/sync-registry.sh)")
            continue
        for _field in ("vertical", "layer_tags", "category_tags", "retrieval_scope",
                       "requires", "role", "essentials_modes", "sectors",
                       "freshness_window", "market_data_stage", "modes"):
            if _disk_entry.get(_field) != _reg_entry.get(_field):
                err(f"registry-sync: skill '{_name}' field '{_field}' diverges — "
                    f"disk={_disk_entry.get(_field)} registry={_reg_entry.get(_field)} "
                    f"(Check 31 — run scripts/sync-registry.sh)")
    for _name in set(_reg) - set(_disk):
        err(f"registry-sync: skill '{_name}' in registry has no SKILL.md on disk (Check 31)")
except (OSError, yaml.YAMLError) as e:
    err(f"registry-sync: {e}")

# --- spec 046 Check 35: tool contract ↔ implementation conformance (Q44/Q43) -
# Fixture-based (deterministic, no network): every ✅-status field in
# get-realtime-quote-tool.md must appear in the ok-envelope the implementation
# actually produces. The live half lives in tests/test_market_data_smoke.py.
_mark('Check 35: tool contract ↔ implementation conformance (Q44/Q43)',
      conditional='contracts/get-realtime-quote-tool.md')
_CONTRACT_FIELD_MAP = {"ticker": "symbol", "last_close": "price",
                       "market_cap": "market_cap", "source": "source",
                       "stale": "stale"}


def _contract_delivered_fields(contract_path: Path) -> set[str]:
    import re as _re

    text = contract_path.read_text(encoding="utf-8")
    delivered: set[str] = set()
    for row in _re.findall(r"^\| `(\w+)` \|.*?\| (✅ today[^|]*?) \|", text,
                           flags=_re.MULTILINE):
        delivered.add(row[0])
    return delivered


try:
    _contract = ROOT / "contracts" / "get-realtime-quote-tool.md"
    _impl = ROOT / "data-tools" / "market_data.py"
    if _contract.is_file() and _impl.is_file():
        import importlib.util as _ilu
        import tempfile

        # 3 = the contract, the implementation, and the cache module it is exercised
        # through. Dormant by construction if the contract is absent (spec 058 T072 owns
        # creating it), which is why the mark names that path as its condition.
        checked += 3

        _spec = _ilu.spec_from_file_location("md_ck", _impl)
        _md = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_md)
        _cache_spec = _ilu.spec_from_file_location("cache_ck", ROOT / "data-tools" / "_cache.py")
        _ck = _ilu.module_from_spec(_cache_spec)
        _cache_spec.loader.exec_module(_ck)
        _delivered = _contract_delivered_fields(_contract)
        # happy path: a pinnable fake provider
        _fake = {"ck35": lambda t: {"symbol": t, "price": 1.0, "market_cap": 1000,
                                    "observed_at": "2026-09-08T16:00:00-04:00",
                                    "price_basis": "close", "data_class": "fast"}}
        _env = _md.get_quote("CK35", providers=_fake)
        _have = dict(_env)
        _have.update(_env.get("data") or {})
        # fallback path: a failing provider + a pre-seeded stale entry → stale: true
        _tmp_cache = _ck.FileCache(root=Path(tempfile.mkdtemp()))
        _tmp_cache.set("market", "quote:CK35F", {"symbol": "CK35F", "price": 9.0,
                                                 "_source": "ck35",
                                                 "observed_at": "2026-09-07T16:00:00-04:00"},
                       ttl=-1)
        _fallback = _md.get_quote("CK35F", providers={"ck35": lambda t: (_ for _ in ()).throw(RuntimeError("down"))},
                                  cache_root=_tmp_cache.root)
        _have_fallback = dict(_fallback)
        _have_fallback.update(_fallback.get("data") or {})
        for _field in _delivered:
            _key = _CONTRACT_FIELD_MAP.get(_field, _field)
            if _key in _have or _key in _have_fallback:
                continue
            err(f"contract-conformance: '{_field}' is ✅ in {rel(_contract)} but "
                f"absent from the implementation envelope (Check 35)")
except Exception as _e:  # noqa: BLE001 — conformance check must not break the linter
    err(f"contract-conformance: could not run the fixture check: {_e}")

# --- spec 046 Check 34: a committed theses/INDEX.md is a proven derivative (Q75)
# Workspaces are runtime artifacts and normally uncommitted; but IF one is
# committed, its generated index must regenerate byte-identically — the Q12
# pattern applied to derived views (a hand-edited index diverges). Dormant until
# the first workspace is committed; active the moment one is.
_mark('Check 34: a committed theses/INDEX.md is a proven derivative (Q75)',
      conditional='theses/INDEX.md')
for _idx in sorted(ROOT.rglob("theses/INDEX.md")):
    if ".tmp" in _idx.name or "node_modules" in _idx.parts:
        continue
    checked += 1
    try:
        import importlib.util as _ilu

        _ts_spec = _ilu.spec_from_file_location("ts_ck34", ROOT / "scripts" / "thesis_status.py")
        _ts = _ilu.module_from_spec(_ts_spec)
        _ts_spec.loader.exec_module(_ts)
        _ws = _idx.parents[1]  # theses/INDEX.md → workspace root
        _regenerated = _ts.render_index(_ts.scan_workspace(_ws))
        if _idx.read_text(encoding="utf-8") != _regenerated:
            err(f"index-derivative: {rel(_idx)} does not regenerate byte-identically "
                f"(Check 34 — DO NOT EDIT generated files; re-run agentii.status)")
    except Exception as _e:  # noqa: BLE001
        err(f"index-derivative: {rel(_idx)}: could not verify regeneration: {_e}")

# --- spec 046 Check 32: no baked harness strings (Q34) ---
# DELEGATES, as of 2026-09-18 (T128). This block used to carry its OWN copy of
# Q34's rule, written in the LITERAL form: `"/agentii-" in text or "/agentii." in
# text`. Spec 046's rule 3 has since been corrected precisely because that form
# is unimplementable — it matches every `https://agentii.ai/...` citation URL, of
# which the kit has 547. Measured: this block scanned 48 files under
# `plugins/vertical-plugins/scenarios/` and reported 0 findings, because the four
# files there containing `agentii.ai` spell it `mcp.agentii.ai` and
# `www.agentii.ai`, which have no preceding `/`.
#
# **It did not fire by luck.** The first `https://agentii.ai/v/...` citation
# added under `scenarios/` would have fired it falsely — and the same rule is
# implemented correctly, URL-aware and verb-aware, in
# scripts/check_no_baked_harness_strings.py. Two implementations of one check is
# what Q12 rule 3 forbids, so the second copy is deleted and this one delegates.
_mark('Check 32: no baked harness strings (Q34) — delegates')
try:
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_no_baked_harness_strings as _q34
    _q34_problems, _q34_scanned = _q34.check_a(_q34._verbs())
    # The delegate prints its own surface ("4,597 files scanned") and now RETURNS it,
    # so this section's row reflects what ran instead of reporting zero — which is
    # what it did until 2026-09-21, when the audit found this block among nine with no
    # row at all and the row ABOVE it absorbing its neighbours' counts.
    checked += _q34_scanned
    for _f in _q34_problems:
        err(f"baked-harness-string: {_f}")
except Exception as _e:                       # noqa: BLE001
    err(f"check 32 could not run: {type(_e).__name__}: {_e} — a check that "
        f"cannot execute must say so, not pass (Q105)")

# --- T114: the build output is verified, not just generated ------------------
# `packaging/targets/` is GITIGNORED build output (.gitignore:18), so nothing
# version-controlled can prove it is current — a stale copy is invisible to git
# and to every gate that reads the repo. Measured before this ran here: 55 of 80
# skills packaged with 40 stale. It is verified by CONTENT HASH against the
# source, and the check reports the surface it examined so a target list that
# silently emptied cannot read as a pass.
_mark('T114: the build output is verified, not just generated',
      conditional='packaging/targets')
try:
    _sources = _q34._sources()
    _build_problems, _build_counts = _q34.check_b(_sources)
    # `total_files` = every (harness, skill) pair the delegate hash-compared. It is 0
    # on a fresh clone, where `packaging/targets/` legitimately does not exist — the
    # conditional above is what distinguishes "not built" from "examined nothing".
    checked += _build_counts.get("total_files", 0)
    for _b in _build_problems:
        err(f"build-output: {_b}")
except Exception as _e:                       # noqa: BLE001
    err(f"build-output verification could not run: {type(_e).__name__}: {_e}")


# --- report ----------------------------------------------------------------
# T128: the surface table. Delta between consecutive marks = that section's
# examined count; the final section runs to the end of the file.
_rows = []
for _i, (_name, _at, _note, _cond) in enumerate(SURFACES):
    _end = SURFACES[_i + 1][1] if _i + 1 < len(SURFACES) else checked
    _rows.append((_name, _end - _at, _note, _cond))

_vacuous = []          # zero surface, undeclared → FAILS (FR-006)
_pending_rows = []     # zero surface, declared pending → reported, and fails at expiry
_cond_rows = []        # zero surface, input absent BY CONSTRUCTION → reported every run
for _name, _n, _note, _cond in _rows:
    if _n != 0:
        continue
    _cov = _pending_covers(_name)
    if _cov:
        _pending_rows.append((_name, _cov))
    elif _cond and not (ROOT / _cond).exists():
        _cond_rows.append((_name, _cond))
    elif _cond:
        # The declaring side is the one that has to be honest here: `conditional` is
        # tolerated only while its input is genuinely missing. If the path is there and
        # the section still read nothing, the marker is silencing a live check.
        err(f"surface: {_name}: declared conditional on {_cond!r}, which EXISTS, yet "
            f"the section examined 0 files — a conditional declaration is honoured only "
            f"while its input is absent (FR-006)")
    else:
        _vacuous.append((_name, _n, _note))

# A pending declaration nothing consults is a declaration that cannot be acted on —
# the same defect FR-040 names for `upstream_stale`. The subject space is exactly
# `check:<n>` (a zero-surface section), because that is the only deferral this gate can
# VERIFY, and an entry it cannot verify would be a falsifiable claim wearing a date.
# Deferrals whose consumer lives elsewhere — an API-repo header contract (T064), an
# owner-run publish or migration (T124, T125) — are NOT expressible here and must not be
# smuggled in: they get a standing notice instead (the `upstream_stale` treatment), and
# each repository that needs the mechanism carries its own `contracts/pending.yaml`
# enforced by its own gate. Stated in contracts/pending.yaml; see the 2026-09-21 audit.
for _subj in sorted(set(PENDING) - _PENDING_CONSULTED):
    err(f"pending: {PENDING[_subj]['id']} declares subject {_subj!r}, which nothing "
        f"consults — a deferral no check reads cannot expire usefully (FR-054). "
        f"Supported subject form: `check:<number>`, matching a section in the surface "
        f"table (`python3 scripts/check.py --surfaces`). For a deferral this gate cannot "
        f"verify, use a standing notice — not an entry here.")

if "-v" in sys.argv or "--surfaces" in sys.argv:
    print("surface_measured — what each check actually examined")
    _pend_by_name = {_n: _e for _n, _e in _pending_rows}
    _cond_by_name = {_n: _c for _n, _c in _cond_rows}
    for _name, _n, _note, _cond in _rows:
        if _n == 0 and _name in _pend_by_name:
            _e = _pend_by_name[_name]
            _tag = (f"PENDING {_e['id']} — no surface yet, owner {_e['owner']}, "
                    f"expires {_e['expires']}")
        elif _n == 0 and _name in _cond_by_name:
            _tag = (f"CONDITIONAL — no input at {_cond_by_name[_name]} "
                    f"(activates when it appears)")
        elif _n == 0:
            _tag = "NO SURFACE REPORTED"
        else:
            _tag = ""
        print(f"  {_n:>5}  {_name}{'  <- ' + _tag if _tag else ''}"
              + (f"   [{_note}]" if _note else ""))
    # Checks 14–17 are reclaimed (spec 058 T003 / FR-007) and deliberately NOT
    # named here: FR-007 says a number that examines nothing must not be counted
    # as a check, and naming them in the inventory is counting them.
    print("  NOTE   attribution is by `checked` delta; every section counts its own "
          f"surface (T001), so each row is that section's examined count. Total: {checked}.")
    if _pending_rows:
        print(f"  NOTE   {len(_pending_rows)} section(s) have no surface yet and are "
              f"declared pending (contracts/pending.yaml, FR-054). Each FAILS the gate "
              f"on its expiry date, and each is resolved by its named owner.")

# Conditional sections are reported on EVERY run, not only under --surfaces. A section
# that is dormant by construction is exactly as invisible as one that forgot to report,
# so it takes the same treatment the `upstream_stale` field gets (FR-040): a standing
# notice, so the condition cannot be forgotten. These are notices, not errors — no owner
# owes them work — but a reader of the gate output learns which checks did not run.
for _name, _cond in _cond_rows:
    warn(f"conditional: {_name} — examined nothing because {_cond} does not exist in "
         f"this repository; it activates when that path appears (FR-006, three states)")

if _vacuous:
    print(f"surface_measured: {len(_vacuous)} of {len(_rows)} section(s) did not "
          f"report a surface. A clean result from an unreported surface is "
          f"indistinguishable from examining nothing — which is Q105's defect, at "
          f"the level of the gate runner itself:", file=sys.stderr)
    for _name, _n, _note in _vacuous:
        print(f"  ! {_name}", file=sys.stderr)
        # FR-006 / T002: a section that examined nothing must FAIL, not warn.
        # Every section now counts its surface (T001), so a zero delta is no
        # longer "did not report" — it means the section walked an empty tree.
        # Either way the gate must not read as clean.
        err(f"surface: {_name}: examined 0 files. A check that examines nothing "
            f"returns the same clean result as one that passes — report the "
            f"surface or remove the check (FR-006).")
    print("", file=sys.stderr)

if notices:
    print(f"NOTICE — {len(notices)} non-fatal item(s):", file=sys.stderr)
    for n in notices:
        print(f"  ~ {n}", file=sys.stderr)
    print("", file=sys.stderr)
if errors:
    print(f"FAIL — {len(errors)} issue(s) across {checked} file examination(s):\n",
          file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    sys.exit(1)
# "examination(s)", not "file(s)": sections overlap by design — the same SKILL.md is
# examined by a dozen of them — so this is the SUM of every section's surface, and
# calling it a file count invited the reading that the kit has this many files. The
# number that must be non-trivial for SC-009 is the section COUNT below it, and since
# 2026-09-21 every row in the table is a section that actually examined something.
print(f"OK — {checked} file examination(s) in {len(_rows)} section(s), 0 issues, "
      f"{len(notices)} notice(s).")
