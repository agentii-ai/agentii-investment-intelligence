#!/usr/bin/env python3
"""synthesize_report.py — the single-point HTML generation pipeline (spec 046 Q49/Q50).

Skills emit MARKDOWN only; ONE thesis-report.html per thesis is assembled here at
synthesis time: read thesis markdown artifacts → assemble sections → embed charts
(SVG base64) → run the overflow gate → deliver, or degrade to markdown.

Q50 pins: sources_hash (aggregate hash of the source markdown artifacts) and
template_version are embedded as body data attributes; converge flags html_stale
on mismatch; regeneration is on-demand.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_page_overflow  # noqa: E402
import chart_render  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates" / "thesis-report.html"
TEMPLATE_VERSION = "0.1.0"


def sources_hash(artifacts: list[Path]) -> str:
    h = hashlib.sha256()
    for p in sorted(artifacts):
        h.update(str(p).encode("utf-8"))
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


def assemble_sections(thesis: Path, chart_data: dict | None = None) -> dict[str, str]:
    """Map thesis markdown artifacts into the report's section divs. Charts are
    embedded as base64 SVG data-URIs when chart_data is provided."""
    sections = {"exec-summary": "", "pillars": "", "universe": "",
                "cross-cutting": "", "coverage-gaps": ""}
    for p in sorted((thesis / "artifacts").rglob("*.md")) if (thesis / "artifacts").is_dir() else []:
        text = p.read_text(encoding="utf-8")
        sections["exec-summary"] += f"<p>{p.stem}</p>\n"
        # pillar content: frontmatter wrong_if / claims surfaces as a structured block
        fm = _frontmatter(text)
        if fm.get("entity_claims"):
            rows = "".join(
                f"<tr><td>{c.get('entity')}</td><td>{c.get('metric')}</td>"
                f"<td>{c.get('value')}</td></tr>" for c in fm["entity_claims"]
                if isinstance(c, dict))
            sections["universe"] += f"<table><tr><th>entity</th><th>metric</th>"
            sections["universe"] += f"<th>value</th></tr>{rows}</table>"
    if chart_data:
        for kind, payload in chart_data.items():
            svg = chart_render.to_data_uri(chart_render.render_svg(kind, payload))
            sections["cross-cutting"] += f'<img src="{svg}" alt="{kind}"/>\n'
    return sections


def _frontmatter(text: str) -> dict:
    import g1_gate  # shared parser

    return g1_gate.parse_frontmatter(text)


def synthesize(thesis: Path, *, out_path: Path | None = None,
               chart_data: dict | None = None) -> tuple[Path, str, bool]:
    """Returns (report_path, sources_hash, degraded). Degrades to markdown when
    the overflow gate cannot pass at any font tier (Q47 failure semantics)."""
    template = TEMPLATE.read_text(encoding="utf-8")
    sections = assemble_sections(thesis, chart_data)
    shash = sources_hash(sorted((thesis / "artifacts").rglob("*.md"))
                         if (thesis / "artifacts").is_dir() else [])
    html = template
    for div_id, content in sections.items():
        html = html.replace(f'<div id="{div_id}"><!-- filled by synthesizer --></div>',
                            f'<div id="{div_id}">{content}</div>')
    html = html.replace("<body>", f'<body data-sources-hash="{shash}" '
                        f'data-template-version="{TEMPLATE_VERSION}">', 1)
    report_path = out_path or (thesis / "thesis-report.html")
    degraded = False
    overflow = check_page_overflow.check(html)
    if overflow:
        degraded = True
        md_path = report_path.with_suffix(".md")
        md_path.write_text("# Thesis Report (markdown fallback)\n\n"
                           f"overflow pages: {overflow}\n", encoding="utf-8")
    _atomic_write(report_path, html)
    return report_path, shash, degraded


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, path)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Thesis HTML synthesis (Q49/Q50)")
    p.add_argument("--thesis", required=True)
    args = p.parse_args(argv)
    path, shash, degraded = synthesize(Path(args.thesis))
    print(f"{'DEGRADED' if degraded else 'OK'} {path} sources_hash={shash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
