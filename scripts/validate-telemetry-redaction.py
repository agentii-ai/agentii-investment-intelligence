#!/usr/bin/env python3
"""
Static analysis: scan codebase for forbidden telemetry field references (FR-053b).

Forbidden fields (MUST NEVER appear in any telemetry emission point):
  ticker, symbol, tickers, symbols,
  prompt, user_prompt, system_prompt,
  model_response, llm_response, completion,
  evidence_pack,
  xlsx_spec, pptx_spec,
  file_path, absolute_path,
  citation_uri, citation,
  document_chunk_id, chunk_id, page_content,
  email, user_id, username,
  api_key, apiKey, x-api-key

Only scans files under scripts/ and a future telemetry/ emission layer; skill
prose is exempt (skill bodies routinely use 'ticker' and 'prompt' in
documentation/methodology). Emission-layer scoping is by file path prefix.

Exits 0 on clean, 1 on violation.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = [
    "ticker", "tickers", "symbol", "symbols",
    "prompt", "user_prompt", "system_prompt",
    "model_response", "llm_response", "completion",
    "evidence_pack",
    "xlsx_spec", "pptx_spec",
    "file_path", "absolute_path",
    "citation_uri",
    "document_chunk_id", "chunk_id", "page_content",
    "email", "user_id", "username",
    "api_key", "apiKey", "x-api-key",
]

# Match: "<field>": ... or <field>=... as telemetry event payload keys.
PATTERNS = [
    re.compile(rf'[\'"]({f})[\'"]\s*:') for f in FORBIDDEN
]

# Scope: only files that claim to emit telemetry events.
TELEMETRY_MARKERS = [
    "telemetry.log_event",
    "emit_event",
    "record_event",
    "Telemetry.",
]


def is_emission_file(path: Path) -> bool:
    if path.suffix not in (".py", ".ts", ".js"):
        return False
    if any(part in {"node_modules", "dist", ".git", ".venv"} for part in path.parts):
        return False
    # Self-exclude: this script and its sibling validators are scanners, not emitters.
    if path.name.startswith("validate-") or path.name == "check.py":
        return False
    text = path.read_text(errors="ignore")
    return any(marker in text for marker in TELEMETRY_MARKERS)


def scan(path: Path) -> list[str]:
    errs: list[str] = []
    text = path.read_text(errors="ignore")
    for i, line in enumerate(text.splitlines(), start=1):
        for pat, field in zip(PATTERNS, FORBIDDEN):
            if pat.search(line):
                errs.append(
                    f"{path.relative_to(ROOT)}:{i}: forbidden telemetry field '{field}' "
                    f"(FR-053b)"
                )
    return errs


def main() -> int:
    errs: list[str] = []
    scanned = 0
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if not is_emission_file(p):
            continue
        scanned += 1
        errs.extend(scan(p))
    if errs:
        print(f"FAIL — {len(errs)} forbidden-field reference(s) in {scanned} emission file(s):",
              file=sys.stderr)
        for e in errs:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1
    print(f"OK — {scanned} emission file(s) scanned, 0 redaction violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
