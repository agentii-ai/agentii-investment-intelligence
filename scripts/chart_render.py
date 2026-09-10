#!/usr/bin/env python3
"""chart_render.py — static SVG chart rendering for the print-first report (Q48).

The standard thesis chart set: football field (valuation range), scenario tree,
KPI trends, ROIC-WACC scatter, peer comparison bars. Rendered by Python →
SVG → base64 inline. No CDN, no runtime JS dependency — the report must print
offline at any DPI. (Dashboard interactivity is a SEPARATE template family.)
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")  # headless
    import matplotlib.pyplot as plt
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False


def render_svg(chart_kind: str, data: dict) -> str:
    """Returns an SVG string for one of the standard chart kinds. When matplotlib
    is unavailable (thin environments), falls back to a minimal hand-built SVG so
    the pipeline degrades gracefully rather than failing the report."""
    if HAVE_MPL:
        return _mpl(chart_kind, data)
    return _fallback_svg(chart_kind, data)


def _mpl(kind: str, data: dict) -> str:
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    if kind == "football_field":
        labels, lows, highs = data["labels"], data["lows"], data["highs"]
        for i, (lo, hi) in enumerate(zip(lows, highs)):
            ax.barh(i, hi - lo, left=lo, height=0.5, color="#dcaf3e")
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels, fontsize=8)
    elif kind == "peer_bars":
        ax.bar(data["labels"], data["values"], color="#1e2a4a")
        ax.tick_params(axis="x", rotation=45, labelsize=7)
    elif kind == "kpi_trend":
        ax.plot(data["x"], data["y"], color="#1e2a4a")
    elif kind == "scatter":
        ax.scatter(data["x"], data["y"], s=18, color="#dcaf3e")
    elif kind == "scenario_tree":
        for parent, child in data.get("edges", []):
            ax.annotate("", xy=child, xytext=parent,
                        arrowprops={"arrowstyle": "->", "color": "#1e2a4a"})
    else:
        raise ValueError(f"unknown chart kind: {kind}")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    import io

    buf = io.BytesIO()
    fig.savefig(buf, format="svg")
    plt.close(fig)
    return buf.getvalue().decode("utf-8")


def _fallback_svg(kind: str, data: dict) -> str:
    """Minimal deterministic SVG — the report still renders offline without matplotlib."""
    w, h = 600, 220
    bars = ""
    if kind == "peer_bars":
        n = len(data.get("labels", []))
        step = w / max(n, 1)
        for i, label in enumerate(data.get("labels", [])):
            v = data.get("values", [0] * n)[i]
            height = min(180, abs(v) * 3)
            bars += (f'<rect x="{i * step + 8}" y="{200 - height}" width="{step - 16}" '
                     f'height="{height}" fill="#1e2a4a"/>'
                     f'<text x="{i * step + step / 2}" y="215" text-anchor="middle" '
                     f'font-size="9">{label}</text>')
    elif kind == "kpi_trend":
        xs = data.get("x", []) or []
        ys = [float(v) for v in data.get("y", []) or []]
        if xs and len(ys) == len(xs) and len(xs) >= 2:
            lo, hi = min(ys), max(ys)
            span = max(hi - lo, 1e-9)
            pad_x, top, bottom = 20, 20, 200
            step = (w - 2 * pad_x) / (len(xs) - 1)
            pts = [(pad_x + i * step,
                    bottom - (v - lo) / span * (bottom - top - 20))
                   for i, v in enumerate(ys)]
            poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
            dots = "".join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#dcaf3e"/>'
                           for px, py in pts)
            labels = "".join(f'<text x="{px:.1f}" y="215" text-anchor="middle" '
                             f'font-size="9" fill="#1e2a4a">{x}</text>'
                             for (px, _py), x in zip(pts, xs))
            bars = (f'<polyline points="{poly}" fill="none" stroke="#1e2a4a" '
                    f'stroke-width="2.5"/>{dots}{labels}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#f0ede3"/>'
            f'{bars}</svg>')


def to_data_uri(svg: str) -> str:
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="Static SVG chart renderer (Q48)")
    p.add_argument("--kind", required=True)
    p.add_argument("--data", required=True, help="JSON payload for the chart kind")
    args = p.parse_args(argv)
    svg = render_svg(args.kind, json.loads(args.data))
    print(to_data_uri(svg) if "--data-uri" in (argv or []) else svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
