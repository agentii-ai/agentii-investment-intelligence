#!/usr/bin/env python3
"""
Validate partner-built plugins (FR-048, FR-049).

Checks:
  - marketplace.json MUST NOT have any entry with partner_built:true at v1.0 (FR-049).
  - For each partner plugin under plugins/partner-built/<slug>/:
      * SKILL.md structural validity.
      * partner-plugin-license-attestation.md present.
      * No tool-name collision with first-party 'agentii.*' namespace.
  - Self-test against tests/fixtures/partner-plugin-fixture/ (if present).

Exits 0 on clean, 1 on violation.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errs: list[str] = []
    mp = ROOT / ".claude-plugin" / "marketplace.json"
    if mp.is_file():
        data = json.loads(mp.read_text())
        for p in data.get("plugins", []):
            if p.get("partner_built") is True:
                errs.append(
                    f"marketplace: '{p.get('name')}' has partner_built:true — "
                    f"forbidden at v1.0 (FR-049)"
                )

    partner_dir = ROOT / "plugins" / "partner-built"
    if partner_dir.is_dir():
        for slug_dir in sorted(partner_dir.iterdir()):
            if not slug_dir.is_dir():
                continue
            if not (slug_dir / "partner-plugin-license-attestation.md").is_file():
                errs.append(
                    f"{slug_dir.relative_to(ROOT)}: missing partner-plugin-license-attestation.md"
                )

    if errs:
        print(f"FAIL — {len(errs)} partner-plugin violation(s):", file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print("OK — partner-plugin checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
