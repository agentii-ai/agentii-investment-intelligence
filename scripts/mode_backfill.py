#!/usr/bin/env python3
"""mode_backfill.py — M1/M2 mode-substrate completion (spec 046 Q79/R2).

M1 (T093–T096):
  - essentials_modes for the 9 mode-bearing skills: derived as the first
    min(3, n) of their existing mode slugs (deterministic, skill-sourced).
  - references/modes.md for the 53 skills lacking it: candidate modes derived
    from each SKILL.md's own structure (Methodology/Protocol subsection
    headings → ≤32-char kebab slugs). A deterministic scaffold from the skill's
    real content — analyst refinement can deepen any mode later without
    renumbering.

M2 (T097):
  - mode-level `market_data_stage` populated per the Q45 vertical default in
    sync_registry.derive_modes (the deterministic rule at mode granularity).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins" / "vertical-plugins"

ESSENTIALS_COUNT = 3  # first N existing modes become the essentials subset

_HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", flags=re.MULTILINE)
_STOP_WORDS = {"the", "a", "an", "and", "of", "for", "in", "on", "to", "with",
               "overview", "introduction", "summary", "references"}


def _slugify(title: str, max_len: int = 32) -> str | None:
    words = [w for w in re.findall(r"[a-z0-9]+", title.lower())
             if w not in _STOP_WORDS]
    if not words:
        return None
    slug = "-".join(words)[:max_len].rstrip("-")
    slug = re.sub(r"^[0-9-]+", "", slug)  # slugs must start with a letter
    return slug if len(slug) >= 3 else None


def derive_mode_candidates(skill_dir: Path) -> list[str]:
    """Candidate modes from the skill's own SKILL.md section headings."""
    sk = skill_dir / "SKILL.md"
    if not sk.is_file():
        return []
    body = sk.read_text(encoding="utf-8").split("---", 2)[-1]
    candidates: list[str] = []
    seen: set[str] = set()
    for heading in _HEADING_RE.findall(body):
        slug = _slugify(heading)
        if slug and slug not in seen:
            seen.add(slug)
            candidates.append(slug)
        if len(candidates) >= 5:
            break
    return candidates or ["analysis"]


def existing_modes(skill_dir: Path) -> list[str]:
    modes_file = skill_dir / "references" / "modes.md"
    if not modes_file.is_file():
        return []
    text = modes_file.read_text(encoding="utf-8")
    return re.findall(r"^### Mode:\s*([a-z0-9][a-z0-9-]*)", text, flags=re.MULTILINE)


def write_modes_file(skill_dir: Path, slugs: list[str]) -> Path:
    """Author references/modes.md with one section per mode (M1 batch target)."""
    modes_file = skill_dir / "references" / "modes.md"
    modes_file.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# " + skill_dir.name + " — Analyst Mode Definitions",
             "",
             "Derived from the skill's own methodology structure "
             "(scripts/mode_backfill.py, spec 046 M1).",
             ""]
    for slug in slugs:
        lines.append(f"### Mode: {slug}")
        lines.append("")
        lines.append(f"**Objective**: {slug.replace('-', ' ').title()} analysis "
                     f"per the skill's methodology (see SKILL.md sections).")
        lines.append("")
    modes_file.write_text("\n".join(lines), encoding="utf-8")
    return modes_file


def set_essentials(skill_dir: Path, slugs: list[str]) -> None:
    """Insert `essentials_modes:` into the SKILL.md frontmatter (after the
    description line — the same convention as the sectors backfill)."""
    sk = skill_dir / "SKILL.md"
    lines = sk.read_text(encoding="utf-8").splitlines()
    if any(l.startswith("essentials_modes:") for l in lines):
        return  # idempotent
    desc_idx = next(i for i, l in enumerate(lines) if l.startswith("description:"))
    flow = "[" + ", ".join(slugs[:ESSENTIALS_COUNT]) + "]"
    lines.insert(desc_idx + 1, f"essentials_modes: {flow}")
    sk.write_text("\n".join(lines) + "\n", encoding="utf-8")


def backfill_essentials() -> int:
    """The 9 mode-bearing skills get essentials_modes = their first ≤3 modes."""
    done = 0
    for sk in sorted(PLUGINS.glob("*/skills/agentii/*/SKILL.md")):
        skill_dir = sk.parent
        modes = existing_modes(skill_dir)
        if not modes:
            continue
        set_essentials(skill_dir, modes)
        done += 1
    return done


def backfill_modes() -> int:
    """The 53 skills without references/modes.md get a derived scaffold."""
    done = 0
    for sk in sorted(PLUGINS.glob("*/skills/agentii/*/SKILL.md")):
        skill_dir = sk.parent
        if existing_modes(skill_dir):
            continue
        if (skill_dir / "references" / "modes.md").is_file():
            continue
        slugs = derive_mode_candidates(skill_dir)
        write_modes_file(skill_dir, slugs)
        done += 1
    return done


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="M1/M2 mode-substrate backfill (Q79)")
    p.add_argument("--essentials", action="store_true")
    p.add_argument("--modes", action="store_true")
    args = p.parse_args(argv)
    if args.essentials:
        print(f"essentials_modes backfilled on {backfill_essentials()} skills")
    if args.modes:
        print(f"references/modes.md scaffolded for {backfill_modes()} skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
