#!/usr/bin/env python3
"""live_snapshot.py — per-ticker live-price capture into `{ticker}-live/` folders.

This is a CAPTURE INSTRUMENT, not a provider fix. It calls the existing
`market_data.get_quote` / `get_price_history` entry points and writes whatever
comes back — success envelopes and refusal envelopes with equal fidelity. That
symmetry is deliberate: when the provider is rate-limited or blocked, the
absence is the finding, and a success-only harness would hide it.

Layout written under `--workspace`:

    {workspace}/{TICKER}-live/
      quote_latest.json    most recent quote envelope, verbatim
      history_1y_1d.json   bars, when obtainable
      attempts.ndjson      append-only fetch log — every attempt, success or failure
      INDEX.md             human-readable rollup

`LIVE-INDEX.md` is written at the workspace root and is the committed summary.

Every write is atomic (tmp + fsync + os.replace), matching data-tools/workspace_cache.py.

License: MIT-only imports (stdlib) — no copyleft.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import market_data  # noqa: E402

# The 19 tickers named in a thesis §2 universe table (see testing-plan.md §A).
THESIS_TICKERS = [
    "ADI", "AEVA", "AMBA", "AMZN", "CAT", "CGNX", "DE", "EMR", "ETN", "F",
    "GE", "HON", "ISRG", "NVDA", "ON", "PH", "QCOM", "SPCX", "TSLA",
]

HISTORY_PERIOD = "1y"
HISTORY_INTERVAL = "1d"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _summarise(env: Optional[dict], kind: str) -> dict:
    """Flatten one envelope into an index row. Never raises on a malformed envelope:
    a harness that crashes on the failure case cannot report the failure case."""
    env = env or {}
    data = env.get("data") if isinstance(env.get("data"), dict) else {}
    row = {
        "kind": kind,
        "status": env.get("status"),
        "source": env.get("source"),
        "cache_hit": env.get("cache_hit"),
        "error": env.get("error"),
        "observed_at": data.get("observed_at") if data else None,
        "retrieved_at": data.get("retrieved_at") if data else None,
        "price_basis": data.get("price_basis") if data else None,
        "data_class": data.get("data_class") if data else None,
        "cache_age_seconds": data.get("cache_age_seconds") if data else None,
    }
    if kind == "quote":
        row["price"] = data.get("price") if data else None
        row["market_cap"] = data.get("market_cap") if data else None
    else:
        bars = data.get("bars") if data else None
        row["bar_count"] = len(bars) if isinstance(bars, list) else None
        row["last_close"] = (
            bars[-1].get("close") if isinstance(bars, list) and bars else None
        )
    return row


def capture_ticker(workspace: Path, ticker: str, *,
                   cache_root: Optional[Path] = None,
                   providers: Optional[dict] = None) -> dict:
    """Fetch quote + history for one ticker and write its `{ticker}-live/` folder.

    `providers` is injectable so the folder contract can be tested against fakes
    without the network. Returns the per-ticker summary dict."""
    folder = workspace / f"{ticker}-live"
    folder.mkdir(parents=True, exist_ok=True)

    quote_env = market_data.get_quote(ticker, providers=providers, cache_root=cache_root)
    hist_env = market_data.get_price_history(
        ticker, period=HISTORY_PERIOD, interval=HISTORY_INTERVAL,
        providers=providers, cache_root=cache_root
    )

    _atomic_write(folder / "quote_latest.json", json.dumps(quote_env, indent=2) + "\n")
    _atomic_write(folder / "history_1y_1d.json", json.dumps(hist_env, indent=2) + "\n")

    quote_row = _summarise(quote_env, "quote")
    hist_row = _summarise(hist_env, "history")
    fetched_at = _now_iso()

    # Append-only attempt log: the record of what happened, not just what worked.
    with open(folder / "attempts.ndjson", "a", encoding="utf-8") as f:
        for row in (quote_row, hist_row):
            f.write(json.dumps({"ticker": ticker, "fetched_at": fetched_at, **row}) + "\n")

    summary = {
        "ticker": ticker,
        "folder": folder.name,
        "fetched_at": fetched_at,
        "quote": quote_row,
        "history": hist_row,
    }
    _atomic_write(folder / "INDEX.md", _render_ticker_index(summary))
    return summary


def _fmt(value: Any) -> str:
    return "—" if value is None else str(value)


def _render_ticker_index(summary: dict) -> str:
    q, h = summary["quote"], summary["history"]
    lines = [
        f"# {summary['ticker']} — live price capture",
        "",
        f"- **captured**: {summary['fetched_at']}",
        f"- **quote status**: `{_fmt(q['status'])}`",
        f"- **history status**: `{_fmt(h['status'])}`",
        "",
        "> Rebuildable, per-machine, gitignored. Produced by",
        "> `data-tools/live_snapshot.py`; see `testing-plan.md`.",
        "",
        "## Quote",
        "",
        "| field | value |",
        "|---|---|",
        f"| price | {_fmt(q.get('price'))} |",
        f"| market_cap | {_fmt(q.get('market_cap'))} |",
        f"| observed_at | {_fmt(q['observed_at'])} |",
        f"| retrieved_at | {_fmt(q['retrieved_at'])} |",
        f"| price_basis | {_fmt(q['price_basis'])} |",
        f"| data_class | {_fmt(q['data_class'])} |",
        f"| cache_age_seconds | {_fmt(q['cache_age_seconds'])} |",
        f"| source | {_fmt(q['source'])} |",
        f"| cache_hit | {_fmt(q['cache_hit'])} |",
        f"| error | {_fmt(q['error'])} |",
        "",
        "## History (1y / 1d)",
        "",
        "| field | value |",
        "|---|---|",
        f"| bars | {_fmt(h.get('bar_count'))} |",
        f"| last_close | {_fmt(h.get('last_close'))} |",
        f"| observed_at | {_fmt(h['observed_at'])} |",
        f"| source | {_fmt(h['source'])} |",
        f"| error | {_fmt(h['error'])} |",
        "",
    ]
    return "\n".join(lines)


def render_workspace_index(summaries: list[dict]) -> str:
    """The committed rollup. Deliberately reports status counts first — the headline
    is how much of the universes actually resolved, not a list of what did."""
    ok_quotes = sum(1 for s in summaries if s["quote"]["status"] == "ok")
    ok_hist = sum(1 for s in summaries if s["history"]["status"] == "ok")
    n = len(summaries)
    lines = [
        "# Live Price Capture — workspace index",
        "",
        f"- **tickers**: {n}",
        f"- **quote ok**: {ok_quotes}/{n}",
        f"- **history ok**: {ok_hist}/{n}",
        f"- **generated**: {_now_iso()}",
        "",
        "> Per-ticker folders (`{TICKER}-live/`) are gitignored and rebuildable.",
        "> This summary is committed. Harness: `data-tools/live_snapshot.py`.",
        "",
        "| ticker | quote | price | observed_at | history | bars | last_close |",
        "|---|---|---:|---|---|---:|---:|",
    ]
    for s in summaries:
        q, h = s["quote"], s["history"]
        lines.append(
            f"| `{s['ticker']}` | {_fmt(q['status'])} | {_fmt(q.get('price'))} | "
            f"{_fmt(q['observed_at'])} | {_fmt(h['status'])} | "
            f"{_fmt(h.get('bar_count'))} | {_fmt(h.get('last_close'))} |"
        )
    errors = sorted({str(s["quote"]["error"]) for s in summaries if s["quote"]["error"]})
    if errors:
        lines += ["", "## Distinct quote errors observed", ""]
        lines += [f"- {e}" for e in errors]
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Capture live prices into {ticker}-live/ folders")
    p.add_argument("--workspace", required=True, type=Path)
    p.add_argument("--tickers", default=",".join(THESIS_TICKERS),
                   help="Comma-separated tickers (default: the 19 thesis names)")
    p.add_argument("--cache-root", default=None, type=Path,
                   help="Override the FileCache root (default: ~/.agentii/cache)")
    args = p.parse_args(argv)

    workspace = args.workspace.expanduser().resolve()
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    if not tickers:
        print("ERROR: no tickers given", file=sys.stderr)
        return 2

    summaries = []
    for ticker in tickers:
        summary = capture_ticker(workspace, ticker, cache_root=args.cache_root)
        summaries.append(summary)
        print(f"{ticker:<6} quote={summary['quote']['status']:<9} "
              f"history={summary['history']['status']:<9} "
              f"error={summary['quote']['error']}")

    _atomic_write(workspace / "LIVE-INDEX.md", render_workspace_index(summaries))
    ok = sum(1 for s in summaries if s["quote"]["status"] == "ok")
    print(f"\n{ok}/{len(summaries)} quotes ok — wrote {len(summaries)} "
          f"*-live/ folders + LIVE-INDEX.md under {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
