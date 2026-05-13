#!/usr/bin/env python3
"""
Validate mode syntax across SKILL.md files.

Checks (FR-052b):
  1. Every '## Mode: <slug>' heading has a valid slug (lowercase, hyphen-separated,
     no non-alphanumeric).
  2. No slug equals 'all' (reserved keyword).
  3. Every essentials_modes entry in frontmatter resolves to an actual '## Mode:' heading.
  4. Steering-examples invocation strings parse against the mode-addressability syntax.

Exits 0 on clean, 1 on any violation.
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
MODE_RE = re.compile(r"^## Mode:\s*([a-z0-9][a-z0-9-]*)\s*$", flags=re.MULTILINE)
SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
RESERVED_SLUGS = {"all"}

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


def scan_skill(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text()
    meta = parse_frontmatter(text)
    modes: list[str] = MODE_RE.findall(text)
    slugs = set(modes)
    for s in slugs:
        if not SLUG_RE.match(s):
            errs.append(f"{path.relative_to(ROOT)}: invalid slug '{s}'")
        if s in RESERVED_SLUGS:
            errs.append(f"{path.relative_to(ROOT)}: reserved slug '{s}' (FR-052b)")
    for em in meta.get("essentials_modes", []) or []:
        if em not in slugs:
            errs.append(
                f"{path.relative_to(ROOT)}: essentials_modes '{em}' has no matching ## Mode: heading"
            )
    return errs


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
    skills = list(ROOT.glob("plugins/**/skills/*/SKILL.md"))
    for sk in sorted(skills):
        errs.extend(scan_skill(sk))
    for ex in sorted(ROOT.glob("managed-agent-cookbooks/*/steering-examples.json")):
        errs.extend(scan_steering_examples(ex))
    if errs:
        print(f"FAIL — {len(errs)} mode-syntax violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"OK — {len(skills)} skill(s) scanned, 0 mode-syntax violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
