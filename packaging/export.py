#!/usr/bin/env python3
"""export.py — multi-platform skill export (spec 039 US7, T083).

Emits per-platform variants from a canonical spec-023 SKILL.md WITHOUT regressing the
already-supported hosts (Claude Code is the source of truth; others are derived).
Native + deterministic (diff-clean re-runs) — does not vendor Skill Seekers, but the
config layout mirrors it so an external Skill Seekers run can substitute later.

Invariants:
- `~~category` placeholders preserved verbatim (connector-agnostic; C1).
- Envelope semantics untouched (bodies copied, not rewritten).
- Reproducible: sorted keys, stable formatting, no timestamps.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]

TARGETS = ["claude-code", "codex", "cowork", "generic-cli"]


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    try:
        import yaml

        _, fm, body = text.split("---", 2)
        return (yaml.safe_load(fm) or {}), body
    except Exception:  # noqa: BLE001
        return {}, text


def _export_one(sk_dir: Path, target: str, out_root: Path) -> None:
    name = sk_dir.name
    text = (sk_dir / "SKILL.md").read_text(encoding="utf-8")
    meta, _body = _parse_frontmatter(text)
    dest = out_root / target / name
    dest.mkdir(parents=True, exist_ok=True)

    # SKILL.md is copied verbatim for every target (placeholders + envelope semantics intact).
    (dest / "SKILL.md").write_text(text, encoding="utf-8")

    if target == "codex":
        # Codex expects a plugin.json manifest alongside the skill markdown.
        manifest = {
            "name": name,
            "description": meta.get("description", ""),
            "entrypoint": "SKILL.md",
            "tools": meta.get("allowed_tools", []),
        }
        (dest / "plugin.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif target == "cowork":
        # Cowork uses a lightweight metadata sidecar.
        meta_out = {"name": name, "description": meta.get("description", ""),
                    "retrieval_scope": meta.get("retrieval_scope")}
        (dest / "metadata.json").write_text(
            json.dumps(meta_out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # claude-code + generic-cli: SKILL.md alone is the artifact.


def export_skill(sk_dir: Path, out_root: Path, targets: Optional[list[str]] = None) -> list[str]:
    targets = targets or TARGETS
    done = []
    for t in targets:
        if t not in TARGETS:
            raise ValueError(f"unknown target '{t}' (known: {TARGETS})")
        _export_one(Path(sk_dir), t, Path(out_root))
        done.append(t)
    return done


def export_all(targets: Optional[list[str]] = None, out_root: Optional[Path] = None) -> int:
    out_root = out_root or (REPO_ROOT / "packaging" / "targets")
    skills = sorted((REPO_ROOT / "plugins" / "vertical-plugins").glob("*/skills/agentii/*/SKILL.md"))
    n = 0
    for sk in skills:
        export_skill(sk.parent, out_root, targets)
        n += 1
    return n


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="multi-platform skill export (spec 039 US7)")
    p.add_argument("--target", default=",".join(TARGETS),
                   help="comma-separated targets: " + ",".join(TARGETS))
    p.add_argument("--out", type=Path, default=REPO_ROOT / "packaging" / "targets")
    p.add_argument("--skill", type=Path, help="export a single skill dir (else all)")
    args = p.parse_args(argv)

    targets = [t.strip() for t in args.target.split(",") if t.strip()]
    if args.skill:
        export_skill(args.skill, args.out, targets)
        print(f"exported {args.skill.name} → {targets}")
    else:
        n = export_all(targets, args.out)
        print(f"exported {n} skills → {targets} under {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
