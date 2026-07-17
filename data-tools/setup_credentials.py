#!/usr/bin/env python3
"""setup_credentials.py — opt-in credential wizard (spec 039 US5, T061).

Zero-key-first: nothing here is required to use the tools. This helps a user set
their OWN free API keys / email for higher rate limits. No central store — keys go
to the user's local .env only. Secrets are never logged or echoed back.

- `--check`            passive, non-interactive: report present/missing vars (CI-safe).
- (no flag)            interactive wizard: prompt per source, open signup URL, write .env.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Optional

# Known free data-source credentials (var, human name, signup URL, required?).
KNOWN_VARS = [
    {"var": "FRED_API_KEY", "name": "FRED (macro)", "url": "https://fredaccount.stlouisfed.org/apikeys", "required": False},
    {"var": "FMP_API_KEY", "name": "Financial Modeling Prep (earnings est.)", "url": "https://site.financialmodelingprep.com/developer/docs", "required": False},
    {"var": "FINNHUB_API_KEY", "name": "Finnhub (market/calendar)", "url": "https://finnhub.io/register", "required": False},
    {"var": "YFINANCE_EMAIL", "name": "Yahoo Finance email (optional)", "url": "https://finance.yahoo.com", "required": False},
]


def check_credentials() -> dict:
    present, missing = [], []
    for spec in KNOWN_VARS:
        (present if os.environ.get(spec["var"]) else missing).append(spec["var"])
    return {"present": present, "missing": missing,
            "zero_key_ok": True,  # all sources have a zero-key path
            "detail": [{"var": s["var"], "name": s["name"], "set": bool(os.environ.get(s["var"]))}
                       for s in KNOWN_VARS]}


def write_env(values: dict[str, str], path: Path | str) -> None:
    """Idempotently upsert KEY=VALUE lines into a .env file (preserve other lines)."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    keys = set(values)
    out, seen = [], set()
    for line in lines:
        k = line.split("=", 1)[0].strip() if "=" in line else None
        if k in keys:
            out.append(f"{k}={values[k]}")
            seen.add(k)
        else:
            out.append(line)
    for k, v in values.items():
        if k not in seen:
            out.append(f"{k}={v}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def _interactive(env_path: Path) -> int:
    print("agentii credential wizard — all sources work zero-key; set keys only for higher limits.\n")
    collected: dict[str, str] = {}
    for spec in KNOWN_VARS:
        if os.environ.get(spec["var"]):
            print(f"  ✓ {spec['var']} already set — skipping")
            continue
        ans = input(f"Set {spec['name']} [{spec['var']}]? (y/N/open) ").strip().lower()
        if ans == "open":
            webbrowser.open(spec["url"])
            ans = input(f"  paste value for {spec['var']} (blank to skip): ").strip()
            if ans:
                collected[spec["var"]] = ans
        elif ans == "y":
            val = input(f"  paste value for {spec['var']} (blank to skip): ").strip()
            if val:
                collected[spec["var"]] = val
    if collected:
        write_env(collected, env_path)
        # never echo the values — only the keys touched
        print(f"\nWrote {len(collected)} key(s) to {env_path}: {sorted(collected)}")
    else:
        print("\nNo keys entered — you're all set with zero-key mode.")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="opt-in credential wizard (spec 039 US5)")
    p.add_argument("--check", action="store_true", help="non-interactive: report present/missing")
    p.add_argument("--json", action="store_true")
    p.add_argument("--env-path", type=Path, default=Path(".env"))
    args = p.parse_args(argv)

    if args.check:
        report = check_credentials()
        if args.json:
            print(json.dumps(report))
        else:
            print("Present:", ", ".join(report["present"]) or "(none)")
            print("Missing:", ", ".join(report["missing"]) or "(none)")
            print("Zero-key mode works without any of these.")
        return 0 if not report["missing"] else 1
    return _interactive(args.env_path)


if __name__ == "__main__":
    raise SystemExit(main())
