#!/usr/bin/env python3
"""check_page_overflow.py — the build-time letter-page overflow gate (spec 046 Q47).

The BLOCKING authority (the runtime JS overlay warns only). HTML has no layout
engine available here, so heights are ESTIMATED per element type (±5% tolerance):
text by line-height × lines, images by declared dimensions, tables by row count.
Any .page over the letter height × 1.05 fails with the page list.

Failure semantics (Q47): 3-tier font-size fallback → retry once → still failing
⇒ `page_overflow_unresolved` + markdown fallback. Deterministic and re-runnable.
"""
from __future__ import annotations

import argparse
import html.parser
import re
import sys
from pathlib import Path

LETTER_HEIGHT_PX = 1056.0  # 279.4mm @ 96dpi (screen approximation; print uses mm)
TOLERANCE = 1.05
FONT_TIERS = [11.0, 10.0, 9.0]  # pt


def _flush_words(buf: list[str]) -> float:
    """Paragraph/cell height from a text buffer: (words / 11) × 16px line + 4px."""
    words = sum(len(t.split()) for t in buf)
    return (words / 11.0) * 16.0 + 4.0


class _Estimator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.pages: list[dict] = []
        self._current = None
        self._text_buf: list[str] = []
        self._row_max = 0.0  # tallest cell of the current table row

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "page" in (attrs.get("class") or ""):
            self._current = {"height": 0.0, "index": len(self.pages)}
            self.pages.append(self._current)
        if self._current is None:
            return
        if tag == "img":
            # chart tokens carry an explicit data-height → the assembler renders
            # <img height="N">; honour it, then style="height:Npx", else default.
            h = attrs.get("height") or ""
            style = attrs.get("style") or ""
            m = re.search(r"height\s*:\s*(\d+)px", style)
            if h.isdigit():
                self._current["height"] += float(h)
            elif m:
                self._current["height"] += float(m.group(1))
            else:
                self._current["height"] += 120.0  # typical embedded chart block
        elif tag in ("h1",):
            self._current["height"] += 44.0
        elif tag in ("h2",):
            self._current["height"] += 30.0
        elif tag in ("h3",):
            self._current["height"] += 26.0
        elif tag in ("hr",):
            self._current["height"] += 10.0

    def handle_data(self, data):
        if self._current is not None and data.strip():
            self._text_buf.append(data)

    def handle_endtag(self, tag):
        if self._current is None:
            return
        if tag in ("td", "th"):
            # table rows: height is the tallest cell, not the sum (v0.2.0 fix —
            # the old flat +22/tr fee double-counted cell text and made every
            # real table overflow the gate).
            self._row_max = max(self._row_max, _flush_words(self._text_buf))
            self._text_buf = []
        elif tag == "tr":
            self._current["height"] += self._row_max + 4.0  # border/padding
            self._row_max = 0.0
            self._text_buf = []
        elif tag in ("p", "li"):
            self._current["height"] += _flush_words(self._text_buf)
            self._text_buf = []
        elif tag in ("div", "section"):
            # flush residual direct text (a plain div with text, or a page's
            # trailing text that never closed a <p>) — never bleeds across pages.
            if self._text_buf:
                self._current["height"] += _flush_words(self._text_buf)
                self._text_buf = []
        elif tag == "table":
            self._current["height"] += self._row_max + 4.0  # malformed tail row
            self._row_max = 0.0


def estimate_heights(html_text: str) -> list[dict]:
    est = _Estimator()
    est.feed(html_text)
    return est.pages


def check(html_text: str, *, font_tier: int = 0) -> list[int]:
    """Returns the list of overflowing page indexes (1-based)."""
    base = FONT_TIERS[font_tier]
    pages = estimate_heights(html_text)
    over = [p["index"] + 1 for p in pages
            if p["height"] > LETTER_HEIGHT_PX * TOLERANCE * (FONT_TIERS[0] / base)]
    return over


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Letter-page overflow gate (Q47)")
    p.add_argument("--html", required=True)
    args = p.parse_args(argv)
    text = Path(args.html).read_text(encoding="utf-8")
    for tier in range(len(FONT_TIERS)):
        over = check(text, font_tier=tier)
        if not over:
            print(f"PASS — no page overflow (font tier {tier})")
            return 0
        if tier < len(FONT_TIERS) - 1:
            print(f"retry: {len(over)} page(s) overflow at tier {tier} — "
                  f"falling back to tier {tier + 1}", file=sys.stderr)
    print(f"FAIL — page_overflow_unresolved: pages {over} overflow at the "
          f"smallest font tier — degrade to markdown output", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
