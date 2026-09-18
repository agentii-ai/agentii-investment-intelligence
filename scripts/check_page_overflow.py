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
import os
import re
import subprocess
import sys
import tempfile
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
        self._skip = False  # inside assembler chrome (sheet head/foot, reg marks)
        self._skip_tag: str | None = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "page" in (attrs.get("class") or ""):
            self._current = {"height": 0.0, "index": len(self.pages)}
            self.pages.append(self._current)
        if self._current is None:
            return
        classes = (attrs.get("class") or "").split()
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
        elif tag == "div" and "stat-row" in classes:
            # v0.3.0 KPI tile row (tile text still counted via its inner divs)
            self._current["height"] += 72.0
        elif tag in ("div", "span") and "sec-kicker" in classes:
            self._current["height"] += 16.0
        elif tag == "div" and "tl-item" in classes:
            self._current["height"] += 10.0  # rail-node spacing; text still counted
        # Assembler chrome lives in the padding zone — never counted.
        if ((tag in ("div", "span") and {"sheet-head", "sheet-foot"} & set(classes))
                or (tag == "i" and any("reg" in c for c in classes))):
            self._skip = True
            self._skip_tag = tag

    def handle_data(self, data):
        if self._current is not None and not self._skip and data.strip():
            self._text_buf.append(data)

    def handle_endtag(self, tag):
        if self._current is None:
            return
        if tag == self._skip_tag:
            # chrome elements (and their inner spans/buttons) never count —
            # clear only when the element that set the skip closes
            self._skip = False
            self._skip_tag = None
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


# ── Q99: the real layout engine, with the estimator demoted to a stamped fallback ──
#
# The ±5% estimator was the gate until it was measured: it passed **five genuinely
# overflowing pages**. A tolerance calibrated on prose cannot see a table that
# overflows by 3%, and a gate that reports "fits" for a page that does not is
# worse than no gate, because the overflow then ships.
#
# The estimator is kept, not deleted — it is the only thing that works with no
# browser — but it now STAMPS which check ran (`data-overflow-check`), so a
# report can never claim a precision it did not have. That is Q105's discipline
# applied to this gate: an un-run check must say it has not run.

OVERFLOW_PROBE_ID = "__overflow_probe__"
DEFAULT_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

_PROBE_JS = """
(function () {
  var out = [];
  document.querySelectorAll('.page').forEach(function (pg, i) {
    out.push((i + 1) + ':' + (pg.scrollHeight - pg.clientHeight));
  });
  var el = document.createElement('div');
  el.id = '%s';
  el.textContent = out.join(',');
  document.body.appendChild(el);
})();
""" % OVERFLOW_PROBE_ID


def chrome_bin() -> Path:
    return Path(os.environ.get("CHROME_BIN", str(DEFAULT_CHROME)))


def engine_available() -> bool:
    """Whether the real engine can run. Cheap, so the assembler can stamp the
    mode BEFORE building the html (the stamp lives in the html itself)."""
    return chrome_bin().is_file()


def check_engine(html_text: str, *, font_tier: int = 0) -> list[int] | None:
    """Per-page `scrollHeight - clientHeight` in headless Chrome. None on failure.

    Chrome's `--print-to-pdf` yields a PDF, not layout metrics, so the probe is
    evaluated IN the page and read back out of the dumped DOM — the same trick
    render_report.py uses to get pixels out of Chrome without a CDP client."""
    chrome = chrome_bin()
    if not chrome.is_file():
        return None
    probe = html_text.replace("</body>", "<script>%s</script></body>" % _PROBE_JS)
    with tempfile.TemporaryDirectory() as d:
        page = Path(d) / "probe.html"
        page.write_text(probe, encoding="utf-8")
        try:
            out = subprocess.run(
                [str(chrome), "--headless", "--disable-gpu", "--no-sandbox",
                 "--virtual-time-budget=4000", "--dump-dom", page.as_uri()],
                capture_output=True, text=True, timeout=120).stdout
        except (subprocess.SubprocessError, OSError):
            return None
    m = re.search(r'id="%s"[^>]*>([^<]*)<' % re.escape(OVERFLOW_PROBE_ID), out)
    if not m:
        return None
    over: list[int] = []
    for pair in m.group(1).split(","):
        if ":" not in pair:
            continue
        idx, _, delta = pair.partition(":")
        try:
            if float(delta) > 0.5:      # sub-pixel noise is not an overflow
                over.append(int(idx))
        except ValueError:
            return None
    return over


def check_with_mode(html_text: str, *, font_tier: int = 0) -> tuple[list[int], str]:
    """(overflowing page indexes, which check produced them)."""
    over = check_engine(html_text, font_tier=font_tier)
    if over is not None:
        return over, "engine"
    base = FONT_TIERS[font_tier]
    pages = estimate_heights(html_text)
    return ([p["index"] + 1 for p in pages
             if p["height"] > LETTER_HEIGHT_PX * TOLERANCE * (FONT_TIERS[0] / base)],
            "approximate")


def check(html_text: str, *, font_tier: int = 0) -> list[int]:
    """Returns the list of overflowing page indexes (1-based)."""
    return check_with_mode(html_text, font_tier=font_tier)[0]


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
