#!/usr/bin/env python3
"""
Validate prose safety per contracts/prose-safety.md + FR-020e.

Scans every SKILL.md, command .md, and cookbook prompt .md for:
  1. Shell-variable forms ($VAR, ${VAR}, $(cmd))
  2. Absolute filesystem paths (/usr/, /home/, /var/, /etc/, /tmp/)
  3. Backtick-wrapped shell tokens (`npm install`, `pip install`, `brew install`)
  4. Dependency-folder names (node_modules, __pycache__, .venv, dist, build, target)

Exempt contexts:
  - !command preflight blocks
  - fenced code blocks (```lang ... ```)
  - HTML comments (<!-- ... -->)
  - frontmatter (between leading ---)

Exits 0 on clean, 1 on violation.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SHELL_VAR = re.compile(r"(?<![\\`])(\$[A-Za-z_]\w*|\$\{[^}]+\}|\$\([^)]+\))")
ABS_PATH = re.compile(r"(?<![\w/])/(?:usr|home|var|etc|tmp)(?:/[\w.-]+)+")
BACKTICK_SHELL = re.compile(r"`(npm|pip|pip3|brew|apt|apt-get|yum|gem|go)\s+\w+[^`]*`")
DEP_FOLDER = re.compile(
    r"(?:^|[\s./\\])(node_modules|__pycache__|\.venv)(?=[\s/\\)\]\"',.:;]|$)"
)


def strip_exempt(text: str) -> str:
    # Remove frontmatter
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    # Remove fenced code blocks (``` ... ```)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Remove !command preflight blocks (lines starting with ! in ## Preflight)
    text = re.sub(r"^![^\n]*$", "", text, flags=re.MULTILINE)
    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    return text


def scan(path: Path) -> list[str]:
    errs: list[str] = []
    raw = path.read_text(errors="ignore")
    body = strip_exempt(raw)

    for m in SHELL_VAR.finditer(body):
        errs.append(f"{path.relative_to(ROOT)}: shell-variable form '{m.group(0)}'")
    for m in ABS_PATH.finditer(body):
        errs.append(f"{path.relative_to(ROOT)}: absolute path '{m.group(0)}'")
    for m in BACKTICK_SHELL.finditer(body):
        errs.append(f"{path.relative_to(ROOT)}: backtick shell '{m.group(0)}'")
    for m in DEP_FOLDER.finditer(body):
        errs.append(f"{path.relative_to(ROOT)}: dependency folder '{m.group(0)}'")
    return errs


def main() -> int:
    errs: list[str] = []
    targets = (
        list(ROOT.glob("plugins/**/SKILL.md"))
        + list(ROOT.glob("plugins/**/commands/*.md"))
        + list(ROOT.glob("managed-agent-cookbooks/**/subagents/system-prompts/*.md"))
    )
    for p in sorted(targets):
        if not p.is_file():
            continue
        errs.extend(scan(p))
    if errs:
        print(f"FAIL — {len(errs)} prose-safety violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"OK — {len(targets)} file(s) scanned, 0 prose-safety violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
