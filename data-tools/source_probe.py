#!/usr/bin/env python3
"""source_probe.py — multi-source live-price probe harness.

A MEASUREMENT INSTRUMENT, not a provider. Nothing here is wired into
`market_data.py`; the purpose is to answer, per source and per ticker: did it
respond, what did it return, how fast, and does it agree with the others.

Why this exists
---------------
The package has exactly one implemented market provider (yfinance) and no
failover, so a single source's failure is a total outage — which is what
happened. Diagnosis also went wrong the first time: the failure was recorded as
a rate limit when it is in fact a geographic block, and `yfinance` reports both
through the same `YFRateLimitError`. Documentation cannot settle questions like
this; only probing can.

Two properties are therefore first-class results rather than error paths:

1. **Reachability.** HTTP status, latency, and whether the body is real data or
   a block/bot page. A 403 with an HTML block page and a 200 with valid JSON are
   different outcomes that a naive client collapses into "no data".
2. **Cross-source agreement.** For each ticker, closes from every source that
   succeeded are compared. Disagreement is the only signal that catches a
   silent field-order or encoding bug — a parser that swaps close and high
   produces perfectly plausible numbers.

Every source failure returns a structured `CODE:`-prefixed refusal
(`refusal.py` convention) so a failure is never mistaken for missing data.

License: MIT-only imports (stdlib + the package's own modules). No copyleft.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _envelope  # noqa: E402

CATEGORY = "probe"
DEFAULT_TIMEOUT = 20

# The 19 tickers named in a thesis §2 universe table.
THESIS_TICKERS = [
    "ADI", "AEVA", "AMBA", "AMZN", "CAT", "CGNX", "DE", "EMR", "ETN", "F",
    "GE", "HON", "ISRG", "NVDA", "ON", "PH", "QCOM", "SPCX", "TSLA",
]

# Secured sources declare their env vars here; a source without its keys is
# skipped rather than failed (the zero-key path must always work).
KEYLESS = "keyless"


# --------------------------------------------------------------------------
# HTTP layer
# --------------------------------------------------------------------------

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# Signatures of a block/bot page rather than data. A 200 carrying one of these
# is NOT a success — this is the trap that made the original diagnosis wrong.
BLOCK_MARKERS = (
    "no longer be accessible from mainland china",
    "too many requests",
    "noindex,nofollow",
    "access denied",
    "captcha",
    "proof-of-work",
)


def _http_get(url: str, *, headers: dict | None = None, encoding: str | None = None,
              timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Fetch a URL and classify the outcome. Never raises on a network error.

    Returns {status, body, text, latency_ms, error, blocked}. `status` is the
    HTTP code or None; `blocked` flags a bot/geo block served as a 200."""
    hdrs = {"User-Agent": BROWSER_UA, "Accept": "*/*"}
    hdrs.update(headers or {})
    started = time.monotonic()
    try:
        req = urllib.request.Request(url, headers=hdrs)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            code = resp.getcode()
    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        code = e.code
    except Exception as e:  # noqa: BLE001 — DNS, TLS, timeout, connection reset
        return {"status": None, "body": b"", "text": "", "latency_ms": None,
                "error": f"{type(e).__name__}: {e}", "blocked": False}
    latency = round((time.monotonic() - started) * 1000)

    try:
        text = raw.decode(encoding or "utf-8", errors="replace")
    except LookupError:  # unknown codec name
        text = raw.decode("utf-8", errors="replace")

    low = text[:4000].lower()
    blocked = any(m in low for m in BLOCK_MARKERS) or low.lstrip().startswith(
        ("<!doctype html", "<html"))
    return {"status": code, "body": raw, "text": text, "latency_ms": latency,
            "error": None, "blocked": blocked}


def _num(value: Any) -> Optional[float]:
    """Parse a price that may carry '$', thousands separators, or be '--'."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).strip().replace("$", "").replace(",", "")
    if cleaned in ("", "--", "N/A", "None", "-"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _quote(ticker: str, source: str, *, price=None, open_=None, high=None, low=None,
           volume=None, observed_at=None, currency="USD", extra=None) -> dict:
    """Build the normalized quote payload every adapter returns."""
    data = {
        "ticker": ticker, "price": price, "open": open_, "high": high, "low": low,
        "volume": volume, "observed_at": observed_at, "currency": currency,
        "price_basis": "close", "data_class": "fast", "source": source,
    }
    if extra:
        data.update(extra)
    return data


# --------------------------------------------------------------------------
# Adapters — one per source. Signature: (ticker) -> envelope dict
# --------------------------------------------------------------------------

def probe_nasdaq(ticker: str) -> dict:
    """api.nasdaq.com — keyless daily OHLCV. Verified working."""
    today = datetime.now(timezone.utc).date()
    start = today.replace(year=today.year - 1)
    url = ("https://api.nasdaq.com/api/quote/"
           f"{urllib.parse.quote(ticker)}/historical?assetclass=stocks"
           f"&fromdate={start}&todate={today}&limit=5")
    r = _http_get(url, headers={"Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="nasdaq")
    if r["status"] != 200 or r["blocked"]:
        return _envelope.error(
            f"SOURCE_UNAVAILABLE: HTTP {r['status']}"
            f"{' (block page)' if r['blocked'] else ''}", source="nasdaq")
    try:
        payload = json.loads(r["text"])
        rows = ((payload.get("data") or {}).get("tradesTable") or {}).get("rows") or []
    except (ValueError, AttributeError) as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="nasdaq")
    if not rows:
        return _envelope.error("NOT_FOUND: no rows for ticker", source="nasdaq")

    newest = rows[0]  # Nasdaq returns newest-first
    stamp = newest.get("date")
    try:
        iso = datetime.strptime(stamp, "%m/%d/%Y").replace(
            tzinfo=timezone.utc).isoformat() if stamp else None
    except ValueError:
        iso = stamp
    return _envelope.ok(_quote(
        ticker, "nasdaq", price=_num(newest.get("close")), open_=_num(newest.get("open")),
        high=_num(newest.get("high")), low=_num(newest.get("low")),
        volume=int(_num(newest.get("volume")) or 0) or None, observed_at=iso,
        extra={"bar_count": len(rows), "latency_ms": r["latency_ms"]}), source="nasdaq")


def probe_sina(ticker: str) -> dict:
    """hq.sinajs.cn — keyless realtime quote. GBK-encoded; requires Referer."""
    url = f"https://hq.sinajs.cn/list=gb_{ticker.lower()}"
    r = _http_get(url, headers={"Referer": "https://finance.sina.com.cn"},
                  encoding="gbk")
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="sina")
    if r["status"] != 200 or r["blocked"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="sina")
    if '="' not in r["text"]:
        return _envelope.error("NOT_FOUND: empty quote payload", source="sina")

    body = r["text"].split('="', 1)[1].rstrip('";\n')
    f = body.split(",")
    if len(f) < 11:
        return _envelope.error(f"SCHEMA_MISMATCH: {len(f)} fields", source="sina")
    # Field map (verified against Nasdaq+Tencent to the cent):
    # 1=price 2=chg% 3=timestamp 4=change 5=open 6=high 7=low 8=52wHi 9=52wLo
    # 10=volume 12=market_cap
    return _envelope.ok(_quote(
        ticker, "sina", price=_num(f[1]), open_=_num(f[5]), high=_num(f[6]),
        low=_num(f[7]), volume=int(_num(f[10]) or 0) or None,
        observed_at=f[3].strip() or None,
        extra={"change_pct": _num(f[2]), "market_cap": _num(f[12]),
               "name": f[0].strip(), "latency_ms": r["latency_ms"]}), source="sina")


def probe_tencent(ticker: str) -> dict:
    """qt.gtimg.cn — keyless realtime quote. GBK-encoded, `~`-delimited.

    NOTE: Tencent's KLINE endpoint is positional with close as the THIRD field,
    not the fourth. Only the quote endpoint is used here; the kline endpoint
    returned 2 bars across three parameter forms when probed.
    """
    url = f"https://qt.gtimg.cn/q=us{ticker.upper()}"
    r = _http_get(url, headers={"Referer": "https://gu.qq.com/"}, encoding="gbk")
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="tencent")
    if r["status"] != 200 or r["blocked"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="tencent")
    if '="' not in r["text"]:
        return _envelope.error("NOT_FOUND: empty quote payload", source="tencent")

    body = r["text"].split('="', 1)[1].rstrip('";\n')
    f = body.split("~")
    if len(f) < 6:
        return _envelope.error(f"SCHEMA_MISMATCH: {len(f)} fields", source="tencent")
    return _envelope.ok(_quote(
        ticker, "tencent", price=_num(f[3]), open_=_num(f[5]) if len(f) > 5 else None,
        extra={"name": f[1].strip() if len(f) > 1 else None,
               "change_pct": _num(f[32]) if len(f) > 32 else None,
               "latency_ms": r["latency_ms"]}), source="tencent")


def probe_yahoo(ticker: str) -> dict:
    """NEGATIVE CONTROL. Yahoo geo-blocks this network; must refuse cleanly."""
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{urllib.parse.quote(ticker)}?range=5d&interval=1d")
    r = _http_get(url, headers={"Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="yahoo")
    if r["status"] != 200 or r["blocked"]:
        kind = "GEO_BLOCK" if r["blocked"] and r["status"] == 403 else "SOURCE_UNAVAILABLE"
        return _envelope.error(f"{kind}: HTTP {r['status']}", source="yahoo")
    try:
        payload = json.loads(r["text"])
        result = (payload.get("chart") or {}).get("result") or []
        if not result:
            return _envelope.error("NOT_FOUND: empty chart result", source="yahoo")
        meta = result[0].get("meta") or {}
        return _envelope.ok(_quote(
            ticker, "yahoo", price=_num(meta.get("regularMarketPrice")),
            observed_at=str(meta.get("regularMarketTime")) if meta.get("regularMarketTime") else None,
            extra={"latency_ms": r["latency_ms"]}), source="yahoo")
    except (ValueError, AttributeError, IndexError) as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="yahoo")


def _probe_alpaca(ticker: str) -> dict:
    """Alpaca Markets — free paper key, 200 req/min, true one-call batching."""
    key = os.environ.get("ALPACA_API_KEY")
    secret = os.environ.get("ALPACA_SECRET_KEY")
    if not (key and secret):
        return _envelope.error("DEP_MISSING: ALPACA_API_KEY/ALPACA_SECRET_KEY unset",
                               source="alpaca")
    url = ("https://data.alpaca.markets/v2/stocks/bars"
           f"?symbols={urllib.parse.quote(ticker)}&timeframe=1Day&limit=5")
    r = _http_get(url, headers={"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret,
                                "Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="alpaca")
    if r["status"] == 401:
        return _envelope.error("DEP_MISSING: alpaca rejected the key (401)", source="alpaca")
    if r["status"] != 200:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="alpaca")
    try:
        bars = ((json.loads(r["text"]).get("bars") or {}).get(ticker) or [])
    except (ValueError, AttributeError) as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="alpaca")
    if not bars:
        return _envelope.error("NOT_FOUND: no bars", source="alpaca")
    last = bars[-1]
    return _envelope.ok(_quote(
        ticker, "alpaca", price=_num(last.get("c")), open_=_num(last.get("o")),
        high=_num(last.get("h")), low=_num(last.get("l")), volume=last.get("v"),
        observed_at=last.get("t"), extra={"bar_count": len(bars),
                                          "latency_ms": r["latency_ms"]}), source="alpaca")


def _probe_tiingo(ticker: str) -> dict:
    """Tiingo — free token. Billing is per HTTP request, not per ticker."""
    token = os.environ.get("TIINGO_API_KEY")
    if not token:
        return _envelope.error("DEP_MISSING: TIINGO_API_KEY unset", source="tiingo")
    url = f"https://api.tiingo.com/tiingo/daily/{urllib.parse.quote(ticker.lower())}/prices?token={token}"
    r = _http_get(url, headers={"Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="tiingo")
    if r["status"] in (401, 403):
        return _envelope.error(f"DEP_MISSING: tiingo rejected the token ({r['status']})",
                               source="tiingo")
    if r["status"] != 200:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="tiingo")
    try:
        rows = json.loads(r["text"])
    except ValueError as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="tiingo")
    if not isinstance(rows, list) or not rows:
        return _envelope.error("NOT_FOUND: no price rows", source="tiingo")
    last = rows[-1]
    return _envelope.ok(_quote(
        ticker, "tiingo", price=_num(last.get("close")), open_=_num(last.get("open")),
        high=_num(last.get("high")), low=_num(last.get("low")),
        volume=last.get("volume"), observed_at=last.get("date"),
        extra={"bar_count": len(rows), "latency_ms": r["latency_ms"]}), source="tiingo")


def _probe_massive(ticker: str) -> dict:
    """Massive (ex-Polygon.io) — free key. `api.polygon.io` serves the same API."""
    key = os.environ.get("POLYGON_API_KEY") or os.environ.get("MASSIVE_API_KEY")
    if not key:
        return _envelope.error("DEP_MISSING: POLYGON_API_KEY/MASSIVE_API_KEY unset",
                               source="massive")
    url = (f"https://api.massive.com/v2/aggs/ticker/{urllib.parse.quote(ticker)}"
           f"/prev?adjusted=true&apiKey={key}")
    r = _http_get(url, headers={"Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="massive")
    if r["status"] in (401, 403):
        return _envelope.error(f"DEP_MISSING: massive rejected the key ({r['status']})",
                               source="massive")
    if r["status"] != 200:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="massive")
    try:
        payload = json.loads(r["text"])
        results = payload.get("results") or []
    except (ValueError, AttributeError) as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="massive")
    if not results:
        return _envelope.error("NOT_FOUND: no results", source="massive")
    bar = results[0]
    ts = bar.get("t")
    iso = (datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
           if isinstance(ts, (int, float)) else None)
    return _envelope.ok(_quote(
        ticker, "massive", price=_num(bar.get("c")), open_=_num(bar.get("o")),
        high=_num(bar.get("h")), low=_num(bar.get("l")), volume=bar.get("v"),
        observed_at=iso, extra={"latency_ms": r["latency_ms"]}), source="massive")


def _probe_fmp(ticker: str) -> dict:
    """Financial Modeling Prep — free key, 250 req/day."""
    key = os.environ.get("FMP_API_KEY")
    if not key:
        return _envelope.error("DEP_MISSING: FMP_API_KEY unset", source="fmp")
    url = (f"https://financialmodelingprep.com/api/v3/quote/"
           f"{urllib.parse.quote(ticker)}?apikey={key}")
    r = _http_get(url, headers={"Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="fmp")
    if r["status"] in (401, 403):
        return _envelope.error(f"DEP_MISSING: fmp rejected the key ({r['status']})", source="fmp")
    if r["status"] != 200:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="fmp")
    try:
        rows = json.loads(r["text"])
    except ValueError as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="fmp")
    if not isinstance(rows, list) or not rows:
        return _envelope.error("NOT_FOUND: no quote row", source="fmp")
    row = rows[0]
    return _envelope.ok(_quote(
        ticker, "fmp", price=_num(row.get("price")), open_=_num(row.get("open")),
        high=_num(row.get("dayHigh")), low=_num(row.get("dayLow")),
        volume=row.get("volume"), extra={"market_cap": _num(row.get("marketCap")),
                                         "pe": _num(row.get("pe")),
                                         "latency_ms": r["latency_ms"]}), source="fmp")


def _probe_finnhub(ticker: str) -> dict:
    """Finnhub — free key. Expected to serve QUOTES only; free tier excludes
    US OHLC history, and the ToS forbids business use even internally."""
    key = os.environ.get("FINNHUB_API_KEY")
    if not key:
        return _envelope.error("DEP_MISSING: FINNHUB_API_KEY unset", source="finnhub")
    url = (f"https://finnhub.io/api/v1/quote?symbol={urllib.parse.quote(ticker)}"
           f"&token={key}")
    r = _http_get(url, headers={"Accept": "application/json"})
    if r["error"]:
        return _envelope.error(f"SOURCE_UNAVAILABLE: {r['error']}", source="finnhub")
    if r["status"] in (401, 403):
        return _envelope.error(f"DEP_MISSING: finnhub rejected the key ({r['status']})",
                               source="finnhub")
    if r["status"] != 200:
        return _envelope.error(f"SOURCE_UNAVAILABLE: HTTP {r['status']}", source="finnhub")
    try:
        row = json.loads(r["text"])
    except ValueError as e:
        return _envelope.error(f"SCHEMA_MISMATCH: {e}", source="finnhub")
    price = _num(row.get("c"))
    if not price:
        return _envelope.error("NOT_FOUND: quote has no current price", source="finnhub")
    return _envelope.ok(_quote(
        ticker, "finnhub", price=price, open_=_num(row.get("o")), high=_num(row.get("h")),
        low=_num(row.get("l")), observed_at=str(row.get("t")) if row.get("t") else None,
        extra={"quote_only": True, "latency_ms": r["latency_ms"]}), source="finnhub")


# name -> (adapter, keyless-or-env spec)
SOURCES: dict[str, dict] = {
    "nasdaq":    {"fn": probe_nasdaq,    "auth": KEYLESS, "license": "unofficial"},
    "sina":      {"fn": probe_sina,      "auth": KEYLESS, "license": "unofficial"},
    "tencent":   {"fn": probe_tencent,   "auth": KEYLESS, "license": "unofficial"},
    "yahoo":     {"fn": probe_yahoo,     "auth": KEYLESS, "license": "Apache-2.0 (geo-blocked)"},
    "alpaca":    {"fn": _probe_alpaca,   "auth": ["ALPACA_API_KEY", "ALPACA_SECRET_KEY"],
                  "license": "Apache-2.0", "batch": True},
    "tiingo":    {"fn": _probe_tiingo,   "auth": ["TIINGO_API_KEY"], "license": "MIT",
                  "batch": True},
    "massive":   {"fn": _probe_massive,  "auth": ["POLYGON_API_KEY"], "license": "MIT",
                  "batch": True},
    "fmp":       {"fn": _probe_fmp,      "auth": ["FMP_API_KEY"], "license": "BSD-3-Clause"},
    "finnhub":   {"fn": _probe_finnhub,  "auth": ["FINNHUB_API_KEY"], "license": "Apache-2.0"},
}


def source_available(name: str) -> tuple[bool, str]:
    """(available, reason). Keyless sources are always available; keyed ones need
    their env vars. A missing key is a skip, never a failure — the zero-key path
    must always work."""
    spec = SOURCES[name]
    if spec["auth"] == KEYLESS:
        return True, ""
    missing = [v for v in spec["auth"] if not os.environ.get(v)]
    if missing:
        return False, f"{name} skipped — unset: {', '.join(missing)}"
    return True, ""


# --------------------------------------------------------------------------
# Probing + agreement
# --------------------------------------------------------------------------

def probe_source(name: str, ticker: str) -> dict:
    """Run one adapter with a hard guarantee: it returns an envelope, always."""
    try:
        env = SOURCES[name]["fn"](ticker)
    except Exception as e:  # noqa: BLE001 — an adapter must never kill the run
        return _envelope.error(f"INTERNAL: {type(e).__name__}: {e}", source=name)
    if not isinstance(env, dict) or "status" not in env:
        return _envelope.error(f"SCHEMA_MISMATCH: adapter returned {type(env).__name__}",
                               source=name)
    return env


def _close_of(env: dict) -> Optional[float]:
    data = env.get("data") if isinstance(env.get("data"), dict) else None
    return _num(data.get("price")) if data else None


def cross_source_agreement(results: dict[str, dict], *, tolerance: float = 0.001) -> dict:
    """Compare same-day closes across sources and flag divergence.

    Disagreement is the only signal that catches a silent parse bug — a parser
    that swaps close and high yields plausible-looking numbers, so nothing else
    would flag it.

    Two design choices, both learned the hard way:

    **Tolerance is tight (0.1%), not loose.** Independent sources report the same
    official close for the same session, so genuine agreement is exact to the
    cent. A loose 0.5% tolerance was silently passing a deliberately-corrupted
    fixture whose close was 0.92% off — it reported "agree" for two sources that
    plainly disagreed.

    **A two-source comparison cannot identify which one is wrong.** With n=2 the
    median is the midpoint between them, so each sits equidistant from the anchor
    and neither can be exonerated. The result says so rather than naming a
    culprit. Three or more sources give the median a real majority to anchor on.
    """
    priced = {n: c for n, env in results.items()
              if env.get("status") == "ok" and (c := _close_of(env))}
    n = len(priced)
    if n < 2:
        return {"comparable": n, "agree": None, "divergent": {}, "values": priced}

    ordered = sorted(priced.values())
    mid = n // 2
    median = (ordered[mid] if n % 2
              else (ordered[mid - 1] + ordered[mid]) / 2)
    spread_pct = ((ordered[-1] - ordered[0]) / median * 100) if median else 0.0

    base = {"comparable": n, "median_close": median, "spread_pct": round(spread_pct, 4),
            "values": priced}

    if spread_pct <= tolerance * 100:
        return {**base, "agree": True, "divergent": {}}

    if n == 2:
        # Both are equally suspect; the spread is real but the culprit is not
        # identifiable from two points.
        divergent = {name: {"close": close, "median": median, "suspect": "unresolved (n=2)"}
                     for name, close in priced.items()}
    else:
        divergent = {}
        for name, close in priced.items():
            dev = abs(close - median) / median if median else 0
            if dev > tolerance:
                divergent[name] = {"close": close, "median": median,
                                   "deviation_pct": round(dev * 100, 4)}
    return {**base, "agree": False, "divergent": divergent}


def probe_ticker(ticker: str, sources: list[str]) -> dict:
    """Probe every available source for one ticker and check agreement."""
    results, skipped = {}, {}
    for name in sources:
        ok, reason = source_available(name)
        if not ok:
            skipped[name] = reason
            continue
        results[name] = probe_source(name, ticker)
    return {
        "ticker": ticker,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "skipped": skipped,
        "agreement": cross_source_agreement(results),
    }


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def _fmt(value: Any, width: int = 6) -> str:
    if value is None:
        return "—".rjust(width)
    if isinstance(value, float):
        return f"{value:.2f}".rjust(width)
    return str(value)[:width].rjust(width)


def reachability_matrix(sources: list[str]) -> list[dict]:
    """Probe each source once, on a reference ticker, to classify reachability."""
    rows = []
    for name in sources:
        ok, reason = source_available(name)
        if not ok:
            rows.append({"source": name, "available": False, "reason": reason,
                         "status": None, "latency_ms": None, "blocked": None,
                         "outcome": "SKIPPED"})
            continue
        started = time.monotonic()
        env = probe_source(name, "AAPL")
        elapsed = round((time.monotonic() - started) * 1000)
        data = env.get("data") if isinstance(env.get("data"), dict) else {}
        row = {
            "source": name, "available": True, "status": env.get("status"),
            "latency_ms": data.get("latency_ms", elapsed),
            "price": _num(data.get("price")) if data else None,
            "error": env.get("error"),
            "outcome": "OK" if env.get("status") == "ok" else "FAIL",
        }
        rows.append(row)
    return rows


def render_reachability(rows: list[dict]) -> str:
    lines = ["| source | outcome | price | latency | detail |", "|---|---|---:|---:|---|"]
    for r in rows:
        detail = r.get("reason") or r.get("error") or ""
        lines.append(f"| `{r['source']}` | {r['outcome']} | {_fmt(r.get('price'))} | "
                     f"{_fmt(r.get('latency_ms'))}ms | {str(detail)[:70]} |")
    return "\n".join(lines)


def render_agreement(report: dict) -> str:
    lines = ["| ticker | sources ok | values | agreement |", "|---|---:|---|---|"]
    for t in report["tickers"]:
        agr = t["agreement"]
        if agr["agree"] is None:
            verdict = f"insufficient ({agr['comparable']} priced)"
        elif agr["agree"]:
            verdict = f"**agree** (n={agr['comparable']})"
        else:
            verdict = "**DIVERGENT**: " + ", ".join(
                f"{k} {v['deviation_pct']}%" for k, v in agr["divergent"].items())
        vals = " ".join(f"{k}={v:.2f}" for k, v in sorted(agr["values"].items()))
        ok = sum(1 for e in t["results"].values() if e.get("status") == "ok")
        lines.append(f"| `{t['ticker']}` | {ok}/{len(t['results'])} | {vals[:60]} | {verdict} |")
    return "\n".join(lines)


def write_outputs(workspace: Path, report: dict) -> None:
    """Per-ticker lines into `{TICKER}-live/sources.ndjson`, plus a summary."""
    for ticker in report["tickers"]:
        folder = workspace / f"{ticker['ticker']}-live"
        folder.mkdir(parents=True, exist_ok=True)
        with open(folder / "sources.ndjson", "a", encoding="utf-8") as f:
            for name, env in ticker["results"].items():
                f.write(json.dumps({
                    "ticker": ticker["ticker"], "source": name,
                    "checked_at": ticker["checked_at"], "status": env.get("status"),
                    "price": _close_of(env), "error": env.get("error"),
                    "latency_ms": (env.get("data") or {}).get("latency_ms")
                    if isinstance(env.get("data"), dict) else None,
                }) + "\n")

    summary = [
        "# Live Price Source Probe",
        "",
        f"- **generated**: {report['generated']}",
        f"- **tickers**: {len(report['tickers'])}",
        f"- **sources probed**: {', '.join(report['sources'])}",
        "",
        "## Reachability",
        "",
        render_reachability(report["reachability"]),
        "",
        "## Cross-source agreement",
        "",
        render_agreement(report),
        "",
    ]
    (workspace / "SOURCE-PROBE.md").write_text("\n".join(summary), encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Multi-source live-price probe harness")
    p.add_argument("--workspace", type=Path, required=True)
    p.add_argument("--tickers", default=",".join(THESIS_TICKERS))
    p.add_argument("--sources", default=",".join(SOURCES))
    p.add_argument("--reachability-only", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    workspace = args.workspace.expanduser().resolve()
    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    sources = [s.strip() for s in args.sources.split(",") if s.strip() in SOURCES]
    if not sources:
        print("ERROR: no known sources selected", file=sys.stderr)
        return 2

    report = {"generated": datetime.now(timezone.utc).isoformat(),
              "sources": sources, "reachability": reachability_matrix(sources)}

    if args.reachability_only:
        print(render_reachability(report["reachability"]))
        return 0

    report["tickers"] = [probe_ticker(t, sources) for t in tickers]
    write_outputs(workspace, report)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(render_reachability(report["reachability"]))
        print()
        print(render_agreement(report))

    agree = sum(1 for t in report["tickers"] if t["agreement"].get("agree"))
    priced = sum(1 for t in report["tickers"] if t["agreement"]["comparable"] >= 1)
    print(f"\n{priced}/{len(tickers)} tickers priced · {agree}/{len(tickers)} multi-source agree"
          f"\nwrote per-ticker sources.ndjson + SOURCE-PROBE.md under {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
