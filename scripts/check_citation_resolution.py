#!/usr/bin/env python3
"""check_citation_resolution.py — do the citations actually resolve? (spec 062 `T083`, live)

THE ONE THING BOTH STRUCTURAL INSTRUMENTS DECLARE THEY CANNOT SEE. `scripts/check_output.py`'s own
docstring says it cannot see *"whether the links resolve [or] whether they are the right page"*, and
`evidence/output-rubric.md` §6 repeats it. Everything else in this repository can be checked offline;
this is the part that needs the live service.

**WHAT "RESOLVES" MEANS HERE, measured 2026-09-25 and not assumed:**

  · `https://agentii.ai/v/{ticker}/{citation_id}/{N}` — the form the standard writes into every
    artifact — **issues two redirects to `agentii.ai/signin/password_signin`**, with AND without a
    bearer token. Measured on three citations including one that does not exist (`PH/sec1/1`), all
    three landing on the sign-in page with a 200 and the same 45,336 bytes. **For a signed-out reader
    the clickable citation in a deliverable does not open the filing.**
  · `https://api.agentii.ai/v1/view_document/{ticker}/{citation_id}` — what the contract says the
    `/v/` route redirects TO — answers **200 with the full combined HTML, no auth required**, and
    `x-credits-used: 0`. An unknown citation id answers **404 `DOCUMENT_NOT_FOUND`**.
  · The body carries `<!-- PAGE_MARKER:{citation_id}_page{N}_START -->`, so **the page a citation
    names can be checked, not only the document** (measured: `AMZN/sec131` carries 79 of them).

So this script verifies against the `api` endpoint, and reports the `/v/` finding separately because it
is a property of the standard rather than of the corpus.

**COST, AND WHY IT IS SMALLER THAN IT LOOKS.** Measured over both workspaces: **6,530 citations map to
133 distinct documents** — citations cluster inside a filing. Caching by `(ticker, citation_id)` turns
6,530 requests into **133**, and the rate limit is **20 per minute** (`x-ratelimit-limit: 20`, a
~60-second window). `--top N` bounds a first pass; the top 20 documents cover 64.5% of all citations,
the top 30 cover 76.6%.

**AND THE FIRST FULL RUN DID NOT FINISH IN ANY ESTIMATED TIME**, which is why there is a deadline. It
stalled eight minutes on a single request — socket ESTABLISHED, 0.63s of CPU over five minutes, so
blocked on I/O rather than spinning. Combined filing HTML runs past 5 MB and one document never
completed. `MAX_FETCH_SECONDS` bounds each document, a truncated body is **not** cached, and it is
reported as its own verdict (`fetch_timeout`) so the result can say how many documents were *not*
checked — a document that silently disappears reads as one that passed.

Documents are cached on disk, so a re-run costs nothing and a later full pass reuses an earlier batch.

Usage:
    export AGENTII_API_KEY=...          # from .env.local; never written by this script
    python3 scripts/check_citation_resolution.py <artifact.md ...> [--top N] [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_output as lint  # noqa: E402 — LINK_RX, one copy

API = "https://api.agentii.ai/v1/view_document/{ticker}/{citation_id}"
CACHE = pathlib.Path(os.environ.get("AGENTII_CITATION_CACHE", "/tmp/agentii-citation-cache"))
# The page-marker pattern is NOT a constant here: it is built at the call site from `re.escape(cid)`,
# because the citation id is part of the pattern. A module-level `MARKER` constant used to sit on this
# line and nothing read it — the same defect as `_FIGURE` in `check_output_quality.py`, where a
# constant with no reader is a claim with no check.


def citations_in(paths: list[str]) -> dict[tuple[str, str], set[str]]:
    """`{(ticker, citation_id): {page_no, ...}}` over every artifact given."""
    out: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    for p in paths:
        text = pathlib.Path(p).read_text(encoding="utf-8", errors="replace")
        _fm, body, _l = lint.split_frontmatter(text)
        for ticker, cid, n in lint.LINK_RX.findall(body):
            out[(ticker, cid)].add(str(n))
    return out


def _wait_for_window(headers: dict) -> None:
    """Respect the service's own rate limit rather than discovering it by being refused."""
    remaining = int(headers.get("x-ratelimit-remaining", "20"))
    reset = int(headers.get("x-ratelimit-reset", "0"))
    if remaining <= 1 and reset:
        nap = max(0, reset - int(time.time())) + 2
        if nap:
            print(f"    rate limit reached — sleeping {nap}s", file=sys.stderr)
            time.sleep(nap)


#: A HARD WALL-CLOCK BOUND PER DOCUMENT, and it is not paranoia: the first full run stalled **8 minutes
#: on one request** with the socket ESTABLISHED and CPU at 0.63s over 5 minutes — blocked on I/O, not
#: spinning. `urlopen(timeout=)` bounds each socket operation, NOT the transfer, so a server that keeps
#: the connection alive without finishing is unbounded by it. Some filings are 5 MB+ of combined HTML
#: and one of them never completed.
MAX_FETCH_SECONDS = float(os.environ.get("AGENTII_FETCH_DEADLINE", "120"))


def _read_within_deadline(r, deadline: float) -> tuple[bytes, bool]:
    """`(body, completed)`. Reads in chunks and gives up at the deadline rather than hanging."""
    chunks, start = [], time.monotonic()
    while True:
        if time.monotonic() - start > deadline:
            return b"".join(chunks), False
        chunk = r.read(1 << 20)
        if not chunk:
            return b"".join(chunks), True
        chunks.append(chunk)


def fetch(ticker: str, cid: str) -> tuple[int, str, dict]:
    """`(status, body, headers)`; cached on disk. Never sends a credential it was not given."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{ticker}__{cid}.html"
    meta = CACHE / f"{ticker}__{cid}.status"
    if f.is_file() and meta.is_file():
        return int(meta.read_text().strip()), f.read_text(errors="replace"), {}

    url = API.format(ticker=ticker, citation_id=cid)
    req = urllib.request.Request(url)
    key = os.environ.get("AGENTII_API_KEY")
    if key:
        req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw, completed = _read_within_deadline(r, MAX_FETCH_SECONDS)
            body, status, hdrs = raw.decode("utf-8", "replace"), r.status, dict(r.headers)
    except urllib.error.HTTPError as e:
        body, status, hdrs = e.read().decode("utf-8", "replace"), e.code, dict(e.headers)
        completed = True
    except Exception as e:                                     # network, timeout, DNS
        return 0, str(e), {}

    if not completed:
        # A TRUNCATED BODY IS NOT CACHED, and its status is recorded as its own number so the report
        # can say how many documents were NOT checked. A silently missing document reads as a document
        # that passed — the same failure this whole specification is about.
        return -1, f"deadline {MAX_FETCH_SECONDS:.0f}s exceeded after {len(body)} bytes", {}

    f.write_text(body, errors="replace")
    meta.write_text(str(status))
    _wait_for_window(hdrs)
    return status, body, hdrs


def check(paths: list[str], top: int | None) -> dict:
    by_doc = citations_in(paths)
    docs = sorted(by_doc.items(), key=lambda kv: -len(kv[1]))
    if top:
        docs = docs[:top]

    rows, pages = [], {}
    for (ticker, cid), wanted in docs:
        status, body, _h = fetch(ticker, cid)
        present = set(re.findall(rf"PAGE_MARKER:{re.escape(cid)}_page(\d+)_START", body))
        pages[f"{ticker}/{cid}"] = sorted(int(x) for x in present)
        for n in sorted(wanted, key=int):
            verdict = ("document_missing" if status == 404 else
                       "fetch_timeout" if status == -1 else
                       "fetch_error" if status != 200 else
                       "resolves" if n in present else "page_missing")
            rows.append({"ticker": ticker, "citation_id": cid, "page": int(n),
                         "document_status": status, "verdict": verdict,
                         "document_pages": len(present)})
    tally = collections.Counter(r["verdict"] for r in rows)
    return {
        "documents_requested": len(docs), "documents_in_corpus": len(by_doc),
        # NOT "citations": `by_doc` holds a SET of page numbers per document, so these are DISTINCT
        # (document, page) references. Measured 2026-09-25: 6,530 citations in the two corpora are
        # 987 distinct page references — the same page is cited by many artifacts, which is the
        # clustering the cache exists for. The first version of this line called them citations.
        "page_refs_checked": len(rows),
        "page_refs_in_corpus": sum(len(v) for v in by_doc.values()),
        "verdicts": dict(tally), "rows": rows, "document_page_counts": pages,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifacts", nargs="+")
    ap.add_argument("--top", type=int, default=None, help="only the N most-cited documents")
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args(argv)

    if not os.environ.get("AGENTII_API_KEY"):
        print("ERROR: AGENTII_API_KEY is not set (source .env.local). "
              "This script never writes it anywhere.", file=sys.stderr)
        return 2

    r = check(args.artifacts, args.top)
    print(f"documents: {r['documents_requested']} of {r['documents_in_corpus']}  |  "
          f"distinct page refs: {r['page_refs_checked']} of {r['page_refs_in_corpus']}")
    for k, v in sorted(r["verdicts"].items(), key=lambda kv: -kv[1]):
        pct = v / r["page_refs_checked"] if r["page_refs_checked"] else 0
        print(f"  {k:18} {v:>5}  {pct:6.1%}")
    if args.json:
        args.json.write_text(json.dumps(r, indent=2))
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
