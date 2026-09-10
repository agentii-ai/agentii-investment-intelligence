#!/usr/bin/env python3
"""render_report.py — the visual QA loop for thesis reports (spec 046 Q47, v0.3.0).

Chrome headless `--print-to-pdf` → `pdfinfo` page-count check → `pdftoppm`
per-page PNGs → `manifest.json`. The LLM READS the PNGs (the only consumer)
and iterates on report/content.html until every page is visually clean — the
template's `@page {size: letter; margin: 0}` + `.page {page-break-after:
always}` makes each `.page` section exactly one letter PDF page, so real
overflow (silently clipped by `overflow: hidden`) becomes visible.

Determinism: PNG bytes are NOT deterministic (font rasterization) — they are
never hashed, pinned or committed; only the LLM's eyes consume them. Pins
(sources_hash / template_version) live on the markdown sources + template;
converge's html_stale is unaffected.

Exit codes: 0 clean · 1 report missing · 2 count/size mismatch or render
failure · 3 Chrome or poppler missing (no silent skip — `assemble
--check-only` remains the estimator fallback).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
_PAGE_ATTR_RE = re.compile(r'data-report-page="(\d+)"')


class RenderError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def chrome_bin() -> Path:
    return Path(os.environ.get("CHROME_BIN", str(DEFAULT_CHROME)))


def png_size(path: Path) -> tuple[int, int]:
    """PNG dimensions from the IHDR chunk — no PIL dependency."""
    data = path.read_bytes()[:24]
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        raise RenderError(2, f"{path.name}: not a readable PNG")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def render(thesis: Path, out: Path | None = None, dpi: int = 192, *,
           keep_pdf: bool = False, verify: bool = False) -> dict:
    """Render the assembled report to per-page PNGs. Returns the manifest dict."""
    thesis = Path(thesis)
    report = thesis / "thesis-report.html"
    if not report.is_file():
        raise RenderError(1, "thesis-report.html not found — run pack → author "
                             "report/content.html → assemble first")
    html_text = report.read_text(encoding="utf-8")
    page_numbers = sorted(int(n) for n in _PAGE_ATTR_RE.findall(html_text))
    expected = list(range(1, len(page_numbers) + 1))
    if page_numbers != expected:
        raise RenderError(2, f"section numbering broken: expected 1..{len(page_numbers)}, "
                             f"found {page_numbers}")
    n_pages = len(page_numbers)

    chrome = chrome_bin()
    pdfinfo = shutil.which("pdfinfo")
    pdftoppm = shutil.which("pdftoppm")
    missing = []
    if not chrome.is_file():
        missing.append(f"Google Chrome ({chrome}) — set CHROME_BIN")
    if not pdfinfo:
        missing.append("poppler `pdfinfo` (brew install poppler)")
    if not pdftoppm:
        missing.append("poppler `pdftoppm` (brew install poppler)")
    if missing:
        raise RenderError(3, "visual render unavailable — missing: "
                             + "; ".join(missing)
                             + ". Fallback: `assemble --check-only` (estimator).")

    tmp = Path(tempfile.mkdtemp(prefix="agentii-render-"))
    pdf = tmp / "thesis-report.pdf"
    try:
        # Chrome writes the PDF quickly but the headless process often lingers
        # on macOS (updater/crashpad IPC) — wait bounded, then kill and validate.
        # stderr goes to a file, never a pipe — Chrome's child processes keep
        # pipes open forever after a kill, which would hang the read.
        err_log = tmp / "chrome-stderr.log"
        with open(err_log, "wb") as err_file:
            proc = subprocess.Popen(
                [str(chrome), "--headless=new", "--disable-gpu", "--disable-vsync",
                 "--no-first-run", "--no-default-browser-check", "--no-pdf-header-footer",
                 f"--print-to-pdf={pdf}", f"--user-data-dir={tmp / 'profile'}",
                 "--virtual-time-budget=10000", report.resolve().as_uri()],
                stdout=subprocess.DEVNULL, stderr=err_file)
        try:
            proc.wait(timeout=45)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            # grace: the PDF may still be flushing — wait for a stable size
            for _ in range(20):
                size = pdf.stat().st_size if pdf.is_file() else 0
                time.sleep(0.5)
                if pdf.is_file() and pdf.stat().st_size == size and size > 0:
                    break
        if not pdf.is_file() or pdf.stat().st_size < 500:
            tail = err_log.read_text(encoding="utf-8", errors="replace")[-400:] \
                if err_log.is_file() else ""
            raise RenderError(2, f"Chrome render failed: {tail}")
        info = subprocess.run([pdfinfo, str(pdf)], capture_output=True, text=True,
                              timeout=30, check=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", info, re.MULTILINE)
        pdf_pages = int(m.group(1)) if m else -1
        if pdf_pages != n_pages:
            raise RenderError(2, f"page-count mismatch: PDF has {pdf_pages} pages, "
                                 f"report has {n_pages} .page sections")

        out_dir = out or (thesis / "report" / "pages")
        out_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run([pdftoppm, "-r", str(dpi), "-png", str(pdf),
                        str(out_dir / "page")], capture_output=True, text=True,
                       timeout=120, check=True)
        pngs = sorted(out_dir.glob("page-*.png"),
                      key=lambda p: int(re.search(r"(\d+)", p.name).group(1)))
        if len(pngs) != n_pages:
            raise RenderError(2, f"PNG count {len(pngs)} != report sections {n_pages}")
        if verify:
            expected_w = round(8.5 * dpi)
            for p in pngs:
                w, _h = png_size(p)
                if abs(w - expected_w) > 1:
                    raise RenderError(2, f"{p.name}: width {w}px, expected "
                                         f"{expected_w}px (8.5in @ {dpi}dpi)")
        width, height = png_size(pngs[0])
        if keep_pdf:
            shutil.copy(pdf, out_dir / "thesis-report.pdf")
        manifest = {
            "page_count": n_pages, "section_count": n_pages, "dpi": dpi,
            "width": width, "height": height,
            "files": [{"page": int(re.search(r"(\d+)", p.name).group(1)),
                       "path": p.name, "width": width, "height": height}
                      for p in pngs],
        }
        (out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return manifest
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="render_report.py",
        description="Visual QA loop: render thesis-report.html to per-page PNGs "
                    "(Chrome headless + poppler) for the LLM's optimize pass")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="render the assembled report to PNGs")
    r.add_argument("--thesis", required=True)
    r.add_argument("--out", default=None, help="output dir (default: <thesis>/report/pages)")
    r.add_argument("--dpi", type=int, default=192)
    r.add_argument("--keep-pdf", action="store_true")
    r.add_argument("--verify", action="store_true",
                   help="also check each PNG is letter-width at the requested dpi")
    args = p.parse_args(argv)
    try:
        manifest = render(Path(args.thesis), out=Path(args.out) if args.out else None,
                          dpi=args.dpi, keep_pdf=args.keep_pdf, verify=args.verify)
        out_dir = Path(args.out) if args.out else (Path(args.thesis) / "report" / "pages")
        print(f"OK {out_dir / 'manifest.json'} pages={manifest['page_count']} "
              f"dpi={manifest['dpi']} ({manifest['width']}x{manifest['height']})")
        return 0
    except RenderError as exc:
        print(exc, file=sys.stderr)
        return exc.code


if __name__ == "__main__":
    sys.exit(main())
