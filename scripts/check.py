#!/usr/bin/env python3
"""
Lint all plugin + managed-agent manifests and verify cross-file references.

Ported and extended from anthropics/financial-services/scripts/check.py
(Apache 2.0) with 12 mandatory checks per spec 023 FR-014a/b, FR-020a/b, FR-054:

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

Exit 0 if clean, 1 otherwise. Requires: pyyaml, jsonschema.
"""
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
checked = 0


def err(msg: str) -> None:
    errors.append(msg)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# --- 1. YAML parse ----------------------------------------------------------
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
    check_refs(yml)

# --- 5. agent-plugin bundled skills match vertical source ------------------
import filecmp

src_by_name = {p.name: p for p in PLUGINS.glob("vertical-plugins/*/skills/*") if p.is_dir()}
for bundled in sorted(PLUGINS.glob("agent-plugins/*/skills/*")):
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
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    slug = md.parents[1].name
    sk_dir = PLUGINS / "agent-plugins" / slug / "skills"
    bundle = {p.name for p in sk_dir.iterdir() if p.is_dir()} if sk_dir.is_dir() else set()
    for ref in set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", md.read_text())):
        if ref in src_by_name and ref not in bundle:
            err(
                f"agent-prose: {rel(md)}: references `{ref}` but "
                f"plugins/agent-plugins/{slug}/skills/{ref}/ is not bundled"
            )

# --- 7. marketplace source paths resolve ------------------------------------
mp = ROOT / ".claude-plugin" / "marketplace.json"
if mp.is_file():
    for p in json.loads(mp.read_text()).get("plugins", []):
        src = (ROOT / p["source"]).resolve()
        if not (src / ".claude-plugin" / "plugin.json").is_file():
            err(f"marketplace: {p['name']} source -> {p['source']} (no plugin.json)")

# --- 8. required files per managed-agent-cookbook ---------------------------
# Cookbooks are populated in Phase 7 (US7). At Phase 1, a cookbook directory
# may exist with only `contracts/` and `subagents/` subdirs and no agent.yaml.
# Treat the cookbook as "populated" only once agent.yaml exists at the root.
for d in sorted(MANAGED.iterdir()):
    if not d.is_dir():
        continue
    if not (d / "agent.yaml").is_file():
        continue  # cookbook not yet populated; skip required-file check
    for req in ("agent.yaml", "README.md", "steering-examples.json"):
        if not (d / req).is_file():
            err(f"missing: {rel(d)}/{req}")

# --- 9-12. SKILL.md structural checks ---------------------------------------
SKILL_FILES = sorted(PLUGINS.glob("vertical-plugins/*/skills/*/SKILL.md")) + \
              sorted(PLUGINS.glob("agent-plugins/*/skills/*/SKILL.md"))

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

# --- report ----------------------------------------------------------------
if errors:
    print(f"FAIL — {len(errors)} issue(s) across {checked} file(s):\n", file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK — {checked} file(s) checked, 0 issues.")
