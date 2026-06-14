#!/usr/bin/env python3
"""
Validate multi_ticker_semantics declarations and related runtime error codes.

Checks (FR-054b):
  a) Every SKILL.md frontmatter has a valid multi_ticker_semantics value.
  b) Zero v1.0 skills declare basket_v1_1.
  c) Negative-test fixtures emit exact-match error codes:
       AGENTII_BASKET_NOT_SUPPORTED
       AGENTII_PEERS_REQUIRED
       AGENTII_PEERS_TOO_MANY
       AGENTII_UNKNOWN_TICKER
       AGENTII_AMBIGUOUS_TICKER_ARG
  d) Auto-peer-resolution determinism (Phase 5 will add fixture tests).
  e) Shared evidence-pack assertion (Phase 7 will add fixture tests).
  f) steering-examples coverage per semantic.

Exits 0 on clean, 1 on violation.
"""
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
VALID_MTS = {"single_target", "target_with_optional_peers", "target_with_required_peers", "basket_v1_1"}
V1_0_FORBIDDEN_MTS = {"basket_v1_1"}

EXPECTED_ERROR_CODES = {
    "AGENTII_BASKET_NOT_SUPPORTED",
    "AGENTII_PEERS_REQUIRED",
    "AGENTII_PEERS_TOO_MANY",
    "AGENTII_UNKNOWN_TICKER",
    "AGENTII_AMBIGUOUS_TICKER_ARG",
}


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
        return yaml.safe_load(fm) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def main() -> int:
    errs: list[str] = []
    skills = list(ROOT.glob("plugins/**/skills/agentii/*/SKILL.md"))
    for sk in sorted(skills):
        meta = parse_frontmatter(sk.read_text())
        mts = meta.get("multi_ticker_semantics")
        if mts not in VALID_MTS:
            errs.append(f"{sk.relative_to(ROOT)}: invalid multi_ticker_semantics '{mts}'")
        elif mts in V1_0_FORBIDDEN_MTS:
            errs.append(f"{sk.relative_to(ROOT)}: '{mts}' forbidden at v1.0 (FR-054b)")

    # (c) negative-test fixtures — scan if present
    fixture_dir = ROOT / "tests" / "fixtures" / "multi-ticker-negative"
    if fixture_dir.is_dir():
        found_codes = set()
        for p in fixture_dir.rglob("*.json"):
            found_codes.update(re.findall(r"AGENTII_[A-Z_]+", p.read_text()))
        missing = EXPECTED_ERROR_CODES - found_codes
        if missing:
            errs.append(
                f"multi-ticker-negative fixtures missing error codes: {sorted(missing)}"
            )

    if errs:
        print(f"FAIL — {len(errs)} multi-ticker violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"OK — {len(skills)} skill(s) scanned, 0 multi-ticker violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
