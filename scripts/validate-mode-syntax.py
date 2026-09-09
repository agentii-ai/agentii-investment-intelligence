#!/usr/bin/env python3
"""
Validate mode syntax (spec 039 FR-052b + spec 046 M0/R2).

Canonical layout (spec 046 M0 — matches reality, verified 2026-09-08):
  modes live in references/modes.md as '### Mode: <slug>' headings, with an optional
  trailing parenthetical ('### Mode: foo (1_1 — anchor)'). The previous layout
  assumption ('## Mode:' in SKILL.md) matched zero files — the validator checked a
  layout nothing used (plan R2).

Checks:
  1. Every '### Mode: <slug>' heading has a valid slug (lowercase, hyphen-separated).
  2. No slug equals 'all' (reserved keyword).
  3. Every essentials_modes frontmatter entry resolves to an actual mode heading.
  4. Steering-examples invocation strings parse against the mode-addressability syntax.

M0 forward rule: slugs > 32 chars are reported as WARNINGS (not errors) — the
slug/title split for the existing long prose slugs lands with M1; failing CI on the
current corpus would turn the validator into a red-every-day test (Q71 lesson).

Exits 0 on clean, 1 on any error-level violation. Warnings do not fail.
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
# '### Mode: <slug>' with an optional trailing parenthetical (real-world format).
MODE_RE = re.compile(
    r"^### Mode:\s*([a-z0-9][a-z0-9-]*)\s*(?:\(.*\))?\s*$", flags=re.MULTILINE
)
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
RESERVED_SLUGS = {"all"}
MAX_SLUG_LEN = 32  # M0 forward rule — warnings only until M1

INVOCATION_RE = re.compile(
    r"^/agentii:(?P<cmd>[a-z][a-z0-9-]*)\s+(?P<ticker>[A-Z]{1,5})"
    r"(?:\s+--mode=(?P<mode>[a-z0-9][a-z0-9-]*))?"
    r"(?:\s+--peers=(?P<peers>[A-Z,]+))?"
    r"(?:\s+--[a-z-]+=[^\s]+)*\s*$"
)


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
        return yaml.safe_load(fm) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def scan_skill(path: Path) -> tuple[list[str], list[str]]:
    """Returns (errors, warnings) for one SKILL.md + its references/modes.md."""
    errs: list[str] = []
    warns: list[str] = []
    text = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    modes_file = path.parent / "references" / "modes.md"
    slugs: list[str] = []
    if modes_file.is_file():
        mtext = modes_file.read_text(encoding="utf-8")
        slugs = MODE_RE.findall(mtext)
    for s in slugs:
        if not SLUG_RE.match(s):
            errs.append(f"{modes_file.relative_to(ROOT)}: invalid slug '{s}'")
        if s in RESERVED_SLUGS:
            errs.append(f"{modes_file.relative_to(ROOT)}: reserved slug '{s}' (FR-052b)")
        if len(s) > MAX_SLUG_LEN:
            warns.append(
                f"{modes_file.relative_to(ROOT)}: slug '{s}' is {len(s)} chars "
                f"(M0 target ≤{MAX_SLUG_LEN} — slug/title split lands with M1)"
            )
    for em in meta.get("essentials_modes", []) or []:
        if em not in slugs:
            errs.append(
                f"{path.relative_to(ROOT)}: essentials_modes '{em}' has no matching "
                f"'### Mode:' heading in references/modes.md"
            )
    return errs, warns


def scan_steering_examples(path: Path) -> list[str]:
    errs: list[str] = []
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return [f"{path.relative_to(ROOT)}: invalid JSON"]
    if isinstance(data, dict):
        data = data.get("examples", [])
    if not isinstance(data, list):
        return errs
    for i, ex in enumerate(data):
        inv = ex.get("invocation") if isinstance(ex, dict) else None
        if inv and not INVOCATION_RE.match(inv):
            errs.append(
                f"{path.relative_to(ROOT)}: steering example {i}: "
                f"invocation '{inv}' does not match mode syntax"
            )
    return errs


def main() -> int:
    errs: list[str] = []
    warns: list[str] = []
    skills = sorted(ROOT.glob("plugins/vertical-plugins/*/skills/agentii/*/SKILL.md"))
    for sk in skills:
        e, w = scan_skill(sk)
        errs.extend(e)
        warns.extend(w)
    for ex in sorted(ROOT.glob("managed-agent-cookbooks/*/steering-examples.json")):
        errs.extend(scan_steering_examples(ex))
    for w in warns:
        print(f"  ⚠ {w}", file=sys.stderr)
    if errs:
        print(f"FAIL — {len(errs)} mode-syntax violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"OK — {len(skills)} skill(s) scanned, 0 mode-syntax violations, "
          f"{len(warns)} M0 long-slug warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
