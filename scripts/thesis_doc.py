#!/usr/bin/env python3
"""thesis_doc.py — where a thesis keeps its machine-readable state (spec 046).

A thesis has TWO files, with one writer each:

    theses/{nnn}-{slug}/thesis.md            prose + `---` frontmatter at byte 0
                                             writer: agentii.specify
                                             read by humans and by g1_gate
    theses/{nnn}-{slug}/thesis.reduce.json   JSON object, top-level "writer"
                                             writer: reduce_journals
                                             read by dispatch / converge /
                                             portfolio_aggregate / thesis_status

**Why two files rather than one.** `g1_gate.parse_frontmatter` requires the text to
begin with `---` at byte 0, and `json.loads` requires it to begin with `{`. No single
document is both, and no reader has a fallback — so before this split, `thesis.md`
could satisfy one family or the other and never both.

**How it went wrong, recorded here because the shape of the mistake repeats.**
`agentii_cmd.specify()` scaffolded `thesis.md` as `# Thesis: <slug>` plus a fenced
```yaml block, which NEITHER reader can read — while `reduce_journals` wrote JSON to
the SAME PATH through the write boundary. The boundary's second-writer refusal keys on
a `writer:` field in the document's own frontmatter; the scaffold declared none, so
the file was append-only and the reducer's write was refused as
`refuse-append-only` — blocking — leaving the file at its scaffold. The reducer
discarded the `Result` and printed `REDUCED N entries → <path>` anyway.

Nothing raised. Measured across the two live workspaces: **24 of 26 `thesis.md` are
`# H1` + fenced yaml**, a shape no reader can read, and the tools above return empty
for all of them — so `converge` reports `{"status": "converged", "findings": 0}` and
an empty portfolio is indistinguishable from "no positions".

**The legacy read path is an accommodation, not a licence.** A `thesis.md` that parses
as a JSON object is still read (source `legacy`) so workspaces written before the
split keep working. No writer may produce that form; `contracts/thesis.md` says so.
"""
from __future__ import annotations

import json
from pathlib import Path

MACHINE_NAME = "thesis.reduce.json"
LEGACY_NOTE = "prose + `---` frontmatter; a JSON `thesis.md` is read but never written"


def thesis_dir(path: Path | str) -> Path:
    """The thesis directory, from any of the three paths that name a thesis.

    Accepts a thesis directory, a `thesis.md` path, or a reduce path. This is what
    lets `reduce(shard_dir, thesis / "thesis.md")` keep its signature — callers
    already pass a file path, and changing that would touch every one of them for
    no gain."""
    p = Path(path)
    if p.is_dir():
        return p
    return p.parent


def machine_path(path: Path | str) -> Path:
    """Where the reducer writes, given any path that names the thesis."""
    return thesis_dir(path) / MACHINE_NAME


def legacy_json(text: str) -> dict | None:
    """The pre-split form: a `thesis.md` whose whole body is a JSON object.

    Strict on both halves — it must LOOK like JSON and PARSE to an object. A JSON
    array, a scalar, or a malformed document all return None, because treating any
    of those as thesis state would be the guessing this module exists to remove."""
    if text.lstrip()[:1] != "{":
        return None
    try:
        doc = json.loads(text)
    except (ValueError, TypeError):
        return None
    return doc if isinstance(doc, dict) else None


def _load(path: Path) -> dict | None:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    return doc if isinstance(doc, dict) else None


def read_machine(path: Path | str) -> tuple[dict, str]:
    """(document, source) where source ∈ {"reduce", "legacy", "none"}. Never raises.

    Precedence: the reduce file, then a legacy JSON `thesis.md`, then nothing.

    **Returning `source` is the point, not a convenience.** Every reader used to
    `except: return []`, so "this thesis has no machine state" and "this thesis has
    machine state that says nothing" produced the same empty answer — which is why a
    file in a shape nothing could read went unnoticed for so long. A caller that
    receives `"none"` can say so; Q105's discipline is that an un-run gate must
    report that it did not run, and this is the same rule one layer down."""
    d = thesis_dir(path)
    doc = _load(d / MACHINE_NAME)
    if doc is not None:
        return doc, "reduce"
    legacy = d / "thesis.md"
    if legacy.is_file():
        try:
            text = legacy.read_text(encoding="utf-8")
        except OSError:
            return {}, "none"
        doc = legacy_json(text)
        if doc is not None:
            return doc, "legacy"
    return {}, "none"


def no_machine_reason(path: Path | str) -> str:
    """The one-line explanation a reader prints on `source == "none"`."""
    d = thesis_dir(path)
    return (f"no machine state for {d.name} — neither {MACHINE_NAME} nor a JSON "
            f"thesis.md was found ({LEGACY_NOTE}); see contracts/thesis.md")
