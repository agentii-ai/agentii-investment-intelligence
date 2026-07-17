#!/usr/bin/env python3
"""Bootstrap / refresh skill-registry.yaml from on-disk skills (spec 039 A1, FR-008/FR-009).

Walks plugins/vertical-plugins/*/skills/agentii/*/SKILL.md, parses frontmatter
(same convention as check.py), and emits one registry entry per skill. Existing
quality scores + enrichment history are PRESERVED across re-syncs (only structural
fields are refreshed from disk).

Invoked by sync-registry.sh. Derivations:
- vertical: from the on-disk path (plugins/vertical-plugins/<vertical>/...)
- retrieval_scope: from frontmatter (present on all current skills)
- layer_tags: inferred from retrieval_scope when no explicit frontmatter (see LAYER_BY_SCOPE);
  defaults to [L2]. Explicit frontmatter layer_tags/category_tags win when present.
- has_knowledge_frameworks: references/knowledge-frameworks.md existence
- spec_037_references: count of citation_id-bearing rows in that file (0 if absent)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _registry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS = REPO_ROOT / "plugins"

# Layer inference when a skill has no explicit layer_tags frontmatter.
# L1 structured lookups, L2 document analysis, L4 technical setups.
LAYER_BY_SCOPE = {
    "structured_only": ["L1"],
    "simple_lookup": ["L1"],
    "single_document": ["L2"],
    "unstructured_document_search": ["L2"],
}
# /v/ citation links carry a citation_id path segment; count rows that reference one.
_CITATION_RE = re.compile(r"/v/[^/\s)]+/[A-Za-z0-9_-]+/")


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
        return yaml.safe_load(fm) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def _count_spec037_refs(skill_dir: Path) -> int:
    kf = skill_dir / "references" / "knowledge-frameworks.md"
    if not kf.is_file():
        return 0
    return len(set(_CITATION_RE.findall(kf.read_text(encoding="utf-8"))))


def build_entries() -> list[dict]:
    entries = []
    for sk in sorted(PLUGINS.glob("vertical-plugins/*/skills/agentii/*/SKILL.md")):
        skill_dir = sk.parent
        # path: plugins/vertical-plugins/<vertical>/skills/agentii/<name>/SKILL.md
        vertical = sk.relative_to(PLUGINS / "vertical-plugins").parts[0]
        meta = _parse_frontmatter(sk.read_text(encoding="utf-8"))
        name = meta.get("name", skill_dir.name)
        scope = meta.get("retrieval_scope")
        layer_tags = meta.get("layer_tags") or LAYER_BY_SCOPE.get(scope, ["L2"])
        kf_exists = (skill_dir / "references" / "knowledge-frameworks.md").is_file()
        entries.append(
            {
                "skill_name": name,
                "vertical": vertical,
                "layer_tags": layer_tags,
                "category_tags": meta.get("category_tags") or [],
                "retrieval_scope": scope,
                "has_knowledge_frameworks": kf_exists,
                "spec_037_references": _count_spec037_refs(skill_dir),
            }
        )
    return entries


def sync(path: Path | None = None) -> int:
    target = path or _registry.DEFAULT_REGISTRY_PATH
    prev = {s.get("skill_name"): s for s in _registry.load_registry(target).get("skills", [])}
    entries = build_entries()
    for e in entries:
        old = prev.get(e["skill_name"], {})
        # Preserve enrichment/scoring history; refresh structural fields from disk.
        e["quality_score"] = old.get("quality_score")
        e["quality_score_prev"] = old.get("quality_score_prev")
        e["last_enriched"] = old.get("last_enriched")
        e["enrichment_workflows_applied"] = old.get("enrichment_workflows_applied", [])
    doc = {
        "version": "1.0.0",
        "generated_by": "scripts/sync-registry.sh",
        "skills": entries,
    }
    _registry.save_registry(doc, target)
    return len(entries)


if __name__ == "__main__":
    n = sync()
    print(f"OK — skill-registry.yaml written with {n} entries.")
