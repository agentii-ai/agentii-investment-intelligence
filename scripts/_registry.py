#!/usr/bin/env python3
"""Skill registry access API (spec 039 Part I, A1 / FR-008..FR-012, FR-027).

Process-internal helpers over ``skill-registry.yaml`` — NOT a network service.
Writes are atomic (temp file + ``os.replace``) so a crash mid-write never
corrupts the registry. Consumed by enhance-skill.py, quality-scan.py, and
sync-registry.sh.

Path note (spec 039 impl): Python data scripts live under ``data-tools/``; the
registry itself lives at the package root as ``skill-registry.yaml``.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError as e:  # pragma: no cover - environment guard
    raise SystemExit("ERROR: _registry.py requires pyyaml (pip install pyyaml)") from e

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "skill-registry.yaml"


class _NoAliasDumper(yaml.SafeDumper):
    """Emit every entry expanded. PyYAML de-duplicates repeated objects into
    anchors/aliases (&id001 / *id001), which would make several skills share one
    mutable list — editing one entry's layer_tags would silently edit the others.
    """

    def ignore_aliases(self, data: Any) -> bool:  # noqa: D102
        return True


def _resolve(path: Optional[Path | str]) -> Path:
    return Path(path) if path is not None else DEFAULT_REGISTRY_PATH


def load_registry(path: Optional[Path | str] = None) -> dict[str, Any]:
    """Load the registry document. Returns an empty skeleton if absent."""
    p = _resolve(path)
    if not p.exists():
        return {"version": "1.0.0", "generated_by": "unknown", "skills": []}
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    doc.setdefault("skills", [])
    return doc


def save_registry(doc: dict[str, Any], path: Optional[Path | str] = None) -> None:
    """Atomically write the registry: serialize to a temp file in the same dir,
    then ``os.replace`` over the target. An existing file is left untouched if
    anything fails before the replace.
    """
    p = _resolve(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.dump(
        doc, Dumper=_NoAliasDumper, sort_keys=False, allow_unicode=True, width=100,
        default_flow_style=False,
    )
    fd, tmp_name = tempfile.mkstemp(dir=str(p.parent), prefix=".skill-registry.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, p)
    except BaseException:
        # Clean up the temp file; the original target is never partially written.
        try:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _skills(path: Optional[Path | str]) -> list[dict[str, Any]]:
    return load_registry(path).get("skills", [])


def get_skill(name: str, path: Optional[Path | str] = None) -> Optional[dict[str, Any]]:
    for s in _skills(path):
        if s.get("skill_name") == name:
            return s
    return None


def list_by_vertical(vertical: str, path: Optional[Path | str] = None) -> list[dict[str, Any]]:
    return [s for s in _skills(path) if s.get("vertical") == vertical]


def list_by_layer(layer: str, path: Optional[Path | str] = None) -> list[dict[str, Any]]:
    return [s for s in _skills(path) if layer in (s.get("layer_tags") or [])]


def get_enrichment_candidates(
    path: Optional[Path | str] = None,
    *,
    vertical: Optional[str] = None,
    layer: Optional[str] = None,
    max_score: float = 7.0,
) -> list[dict[str, Any]]:
    """Return skills eligible for enrichment (score below ``max_score``),
    optionally filtered by vertical/layer. A null/missing score counts as 0.
    """
    out = []
    for s in _skills(path):
        if vertical and s.get("vertical") != vertical:
            continue
        if layer and layer not in (s.get("layer_tags") or []):
            continue
        score = s.get("quality_score")
        score = 0.0 if score is None else float(score)
        if score < max_score:
            out.append(s)
    return out


def upsert_skill(entry: dict[str, Any], path: Optional[Path | str] = None) -> None:
    """Insert or replace a skill entry by ``skill_name`` and persist atomically."""
    doc = load_registry(path)
    skills = doc.setdefault("skills", [])
    for i, s in enumerate(skills):
        if s.get("skill_name") == entry.get("skill_name"):
            skills[i] = entry
            break
    else:
        skills.append(entry)
    save_registry(doc, path)
