#!/usr/bin/env python3
r"""
Validate every citation in committed SKILL.md files matches the v1.0 citation format.

Canonical regex per FR-050 v1.0:
    \[📄 <ticker> <form> p\.<N>\]\(agentii://source/<uuid>\?accession=<acc>&page=<N>\)

Also scans for un-rewritten upstream citation patterns and fails on any hit:
  - [Daloopa Source N]
  - [FactSet]
  - legacy tuple [📄](id-row) syntax
  - [S&P Global ...]

Exits 0 on clean scan, 1 on any violation. Scaffold-safe: skips empty files.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Two canonical forms are accepted:
#   1. v1.0 link:   [📄 <ticker> <form> p.<N>](agentii://source/<uuid>?accession=<acc>&page=<N>)
#   2. path-based (current canonical, skill-methodology-template.md §"Citation Link Format"):
#                   [📄 <ticker> <form> p.<N>](https://agentii.ai/v/<ticker>/<citation_id>[/<N>])
# Both allow {placeholder} segments used in instructional "Citation link format" examples.
CANONICAL_RE = re.compile(
    r"\[📄 [^\]]+ p\.[\w{}]+\]\("
    r"(?:agentii://source/[a-f0-9{}-]+\?accession=[\d{}-]+&page=[\w{}]+"
    r"|https://agentii\.ai/v/[\w{}-]+/[\w{}-]+(?:/[\w{}-]+)?)"
    r"\)"
)

FORBIDDEN_PATTERNS = [
    (re.compile(r"\[Daloopa Source \d+\]"), "upstream-daloopa"),
    (re.compile(r"\[FactSet[^\]]*\]"), "upstream-factset"),
    (re.compile(r"\[S&P Global[^\]]*\]"), "upstream-spglobal"),
    (re.compile(r"\[Bloomberg[^\]]*\]"), "upstream-bloomberg"),
    (re.compile(r"\[📄\]\([\w-]+-row\)"), "legacy-tuple-row"),
]

# Matches "citation-like" chunks that SHOULD be FR-050 but might not be.
# Anything starting with the 📄 emoji that doesn't match CANONICAL_RE.
LOOSE_CITATION_RE = re.compile(r"\[📄[^\]]*\]\([^)]*\)")


def scan(path: Path) -> list[str]:
    text = path.read_text()
    errs: list[str] = []
    for pat, name in FORBIDDEN_PATTERNS:
        for m in pat.finditer(text):
            errs.append(f"{path.relative_to(ROOT)}: forbidden {name}: '{m.group(0)}'")
    # Loose 📄 citations that don't match canonical
    for m in LOOSE_CITATION_RE.finditer(text):
        if not CANONICAL_RE.fullmatch(m.group(0)):
            errs.append(
                f"{path.relative_to(ROOT)}: non-conforming citation "
                f"(does not match v1.0 citation format regex): '{m.group(0)}'"
            )
    return errs


def main() -> int:
    errs: list[str] = []
    # System prompts and agent system files contain template/placeholder citations
    # (e.g., `<TICKER> <filing_type> <filing_year>`) — exempt from validation.
    def is_exempt(path: Path) -> bool:
        rp = str(path.relative_to(ROOT))
        return "/system-prompts/" in rp or "/agents/" in rp

    targets = (
        list(ROOT.glob("plugins/**/*.md"))
        + list(ROOT.glob("managed-agent-cookbooks/**/*.md"))
        + list(ROOT.glob("tests/fixtures/**/*.md"))
    )
    count = 0
    for p in sorted(targets):
        if not p.is_file():
            continue
        if is_exempt(p):
            continue
        count += 1
        errs.extend(scan(p))
    if errs:
        print(f"FAIL — {len(errs)} citation violation(s) across {count} file(s):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"OK — {count} file(s) scanned, 0 citation violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
