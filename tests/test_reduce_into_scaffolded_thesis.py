"""test_reduce_into_scaffolded_thesis.py — the seam between the two writers.

`thesis.md` has two writers and they were tested independently, so the seam between
them was covered by nothing:

  * `agentii_cmd.specify()` scaffolds it — markdown, `# Thesis: <slug>` at byte 0,
    no `---` frontmatter, and **not routed through the write boundary**.
  * `reduce_journals.reduce()` writes it — JSON, through the boundary, declaring
    `writer='reduce_journals'`.

The boundary's second-writer refusal keys on a `writer:` field in the document's own
`---` frontmatter (`write_boundary.declared_writer`). The scaffold has none, so
`declared_writer` returns `None`, the JSON is not an append of the markdown, and the
verdict is **`refuse-append-only`** — a BLOCKING refusal. `write()` returns without
writing, and `reduce()` discards the `Result` and returns `doc`.

So the reducer is a **no-op that reports success**: `main()` prints
`REDUCED N entries → <path>` and exits 0 while `thesis.md` stays the scaffold.

Every existing test of `reduce()` hands it a path that does not pre-exist — so the
verdict is `allow` ("new file") and the refusal never fires. `test_write_boundary.py`'s
`test_undeclared_writer_is_append_only` even asserts that this refusal is CORRECT.
Both halves pass; nobody checked that `specify()` produces a document satisfying it.

This file is that check.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import agentii_cmd  # noqa: E402
import journal  # noqa: E402
import reduce_journals  # noqa: E402
import write_boundary  # noqa: E402


def _ratify(ws, name="Test Fund"):
    """Scaffold a workspace and fill it in, the way a human ratifying would.

    Copied from `test_commands_s4.py`, which is the canonical version: Q108 made
    ratification reject EVERY bracketed placeholder case-insensitively, so a fixture
    wanting a ratified workspace has to author one rather than substitute a token."""
    import re as _re
    agentii_cmd.constitution_scaffold(ws)
    p = ws / "constitution.md"
    t = p.read_text(encoding="utf-8")

    def fill(segment):
        return _re.sub(r"\[[A-Za-z][A-Za-z0-9_ -]{2,40}\]",
                       lambda m: name if "WORKSPACE" in m.group(0) else "authored",
                       segment)

    parts = _re.split(r"(<!--.*?-->|`[^`\n]*`)", t, flags=_re.S)
    p.write_text("".join(i % 2 and s or fill(s) for i, s in enumerate(parts)),
                 encoding="utf-8")
    return ws


def _shards(thesis: Path, n: int = 3) -> Path:
    shard_dir = thesis / "shards"
    shard_dir.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        journal.append_entry(
            shard_dir / f"a{i}.ndjson",
            journal.make_entry("recent-quarter", "NVDA", "default", "001-mvp", [],
                               observed_at="2026-09-08T16:00:00-04:00"))
    return shard_dir


def test_reduce_into_a_scaffolded_thesis_writes_the_reduce_file(tmp_path):
    """THE regression. A reduce into an existing scaffolded thesis.md must land.

    Before the fix this fails: the boundary refuses (`refuse-append-only`), nothing is
    written, and `reduce()` reports success anyway.
    """
    ws = _ratify(tmp_path / "ws")
    thesis = agentii_cmd.specify(ws, "mvp")
    assert (thesis / "thesis.md").is_file(), "the scaffold must exist for this test"

    doc = reduce_journals.reduce(_shards(thesis), thesis / "thesis.md")

    assert doc["mechanical"]["entry_count"] == 3
    reduce_path = thesis / "thesis.reduce.json"
    assert reduce_path.is_file(), (
        "the reduce document was not written — the boundary refused and reduce() "
        "discarded the result")


def test_reduce_into_a_scaffolded_thesis_leaves_the_prose_untouched(tmp_path):
    """The scaffold's prose is the HUMAN's file. A reduce must not overwrite it.

    This is the other half of the seam, and the direction that actually caused damage
    in the field: commit `cdc5ce3` overwrote a thesis.md's markdown scaffold with a
    526-byte empty reduce, which was then copied byte-identically into a snapshot.
    """
    ws = _ratify(tmp_path / "ws")
    thesis = agentii_cmd.specify(ws, "mvp")
    before = (thesis / "thesis.md").read_text(encoding="utf-8")

    reduce_journals.reduce(_shards(thesis), thesis / "thesis.md")

    assert (thesis / "thesis.md").read_text(encoding="utf-8") == before, (
        "the reduce rewrote thesis.md — the prose belongs to the scaffold's writer")


def test_the_scaffolded_thesis_declares_its_writer(tmp_path):
    """A document that declares no writer is APPEND-ONLY, and that fail-safe is what
    turned the reducer into a silent no-op. Declaring it is what makes the refusal
    decidable rather than accidental."""
    ws = _ratify(tmp_path / "ws")
    thesis = agentii_cmd.specify(ws, "mvp")
    text = (thesis / "thesis.md").read_text(encoding="utf-8")

    assert text.startswith("---"), (
        "thescaffold must begin with `---` at byte 0 — `declared_writer` can read "
        "nothing else, and neither can g1_gate.parse_frontmatter")
    assert write_boundary.declared_writer(text) == "agentii.specify", (
        f"declared writer is {write_boundary.declared_writer(text)!r}")


def test_a_refused_reduce_does_not_report_success(tmp_path, capsys):
    """The failure must be LOUD. `main()` printing `REDUCED N entries` over a write
    that never happened is the defect, not the symptom."""
    ws = _ratify(tmp_path / "ws")
    thesis = agentii_cmd.specify(ws, "mvp")
    _shards(thesis)

    # Claim the reduce path for a different writer, so this reduce is refused.
    reduce_path = thesis / "thesis.reduce.json"
    reduce_path.write_text(
        '{\n  "writer": "someone-else",\n  "judgment": {}\n}\n', encoding="utf-8")
    before = reduce_path.read_text(encoding="utf-8")

    rc = reduce_journals.main(["--shard-dir", str(thesis / "shards"),
                               "--thesis", str(thesis / "thesis.md")])
    out = capsys.readouterr()

    assert rc != 0, "a refused reduce must not exit 0"
    assert reduce_path.read_text(encoding="utf-8") == before, "a refusal means UNCHANGED"
    assert "REDUCED" not in out.out, (
        f"a refused reduce printed its success line:\n{out.out}")


# ── the C2 case: JSON declares its own writer, or the split moves the bug ────

def test_a_json_document_declares_its_writer():
    """JSON cannot contain `---` frontmatter, so the same field lives at top level.

    Without this, a reduce file declares nothing — and "declares nothing" means
    APPEND-ONLY, so the SECOND reduction is refused exactly as the first one was
    before the split. The fix would have reproduced the bug on a new path, which is
    why this assertion exists separately from the markdown one.
    """
    assert write_boundary.declared_writer('{"writer": "reduce_journals"}') == "reduce_journals"
    assert write_boundary.declared_writer('{"writer": "someone-else"}') == "someone-else"
    # absent is absent, in either carrier
    assert write_boundary.declared_writer('{"judgment": {}}') is None
    # and a malformed or non-object document declares nothing rather than raising
    assert write_boundary.declared_writer('{ broken') is None
    assert write_boundary.declared_writer('[1, 2]') is None
    assert write_boundary.declared_writer('# markdown, no frontmatter') is None


def test_the_same_json_writer_may_write_twice(tmp_path):
    """The C2 regression. If this fails, the split did not fix anything."""
    p = tmp_path / "thesis.reduce.json"
    first = '{\n  "writer": "reduce_journals",\n  "reduced_at": "2026-09-19T00:00:00"\n}\n'
    assert write_boundary.write(p, first, producer="r", kind="json",
                                writer="reduce_journals").ok()
    second = '{\n  "writer": "reduce_journals",\n  "reduced_at": "2026-09-19T01:00:00"\n}\n'
    r = write_boundary.write(p, second, producer="r", kind="json",
                             writer="reduce_journals")
    assert r.ok(), r.describe()
    assert p.read_text(encoding="utf-8") == second


def test_a_different_writer_is_still_refused_on_the_json_file(tmp_path):
    p = tmp_path / "thesis.reduce.json"
    first = '{"writer": "reduce_journals"}\n'
    write_boundary.write(p, first, producer="r", kind="json", writer="reduce_journals")
    r = write_boundary.write(p, '{"writer": "someone-else"}\n', producer="x",
                             kind="json", writer="someone-else")
    assert r.verdict == "refused", r.describe()
    assert p.read_text(encoding="utf-8") == first, "refused means UNCHANGED"


def test_an_undeclared_json_file_is_append_only(tmp_path):
    """The fail-safe must survive the new carrier, or the new carrier is a hole."""
    p = tmp_path / "notes.json"
    write_boundary.write(p, '{"a": 1}\n', producer="x", kind="json")
    r = write_boundary.write(p, '{"a": 2}\n', producer="x", kind="json")
    assert r.verdict == "refused", r.describe()
    assert "APPEND-ONLY" in " ".join(r.reasons)


# ── read_machine: the four shapes on disk, and never raising ────────────────

def test_read_machine_precedence_and_legacy(tmp_path):
    """Precedence: the reduce file, then a legacy JSON thesis.md, then nothing.

    The `source` is the point. Every reader used to collapse all three into `[]`, so
    "no machine state" and "machine state that says nothing" were the same answer —
    which is how a file in a shape nothing could read went unnoticed.
    """
    import thesis_doc

    d = tmp_path / "001-mvp"
    d.mkdir()

    assert thesis_doc.read_machine(d) == ({}, "none")                    # empty
    (d / "thesis.md").write_text("# Thesis: mvp\n", encoding="utf-8")
    assert thesis_doc.read_machine(d) == ({}, "none")                    # prose only
    (d / "thesis.md").write_text('{"judgment": {"claims": []}}', encoding="utf-8")
    assert thesis_doc.read_machine(d)[1] == "legacy"                     # pre-split
    (d / thesis_doc.MACHINE_NAME).write_text('{"writer": "reduce_journals"}',
                                             encoding="utf-8")
    doc, src = thesis_doc.read_machine(d)
    assert src == "reduce" and doc["writer"] == "reduce_journals"        # reduce wins
    (d / thesis_doc.MACHINE_NAME).write_text("{ broken", encoding="utf-8")
    assert thesis_doc.read_machine(d)[1] == "legacy"                     # falls back


def test_read_machine_accepts_every_path_that_names_a_thesis(tmp_path):
    """`reduce(shard_dir, thesis / "thesis.md")` must keep working — callers pass a
    FILE path, and changing that would touch every one of them."""
    import thesis_doc

    d = tmp_path / "001-mvp"
    d.mkdir()
    for path in (d, d / "thesis.md", d / thesis_doc.MACHINE_NAME):
        assert thesis_doc.machine_path(path) == d / thesis_doc.MACHINE_NAME, path
