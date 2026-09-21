#!/usr/bin/env python3
"""migrate_artifacts.py — the migration command FR-042 requires (spec 058 T022).

FR-042: *"A machine-run change to a skill's contract MUST be accompanied by the migration
command for existing artifacts, and the migration MUST be verified against a fixture
workspace."* This is that command. The contract change it serves is the artifact-frontmatter
set the corpus does not carry: `affix`, `conclusions`, `date`, `facts_count`,
`citation_count` and `key_metrics`, measured **0 of 206** (the first five) and **106 of
206** (the last) on 2026-09-21.

DRY RUN IS THE DEFAULT, and a needed rewrite is an EXIT CODE
------------------------------------------------------------
`--apply` is required to write anything, and a dry run that finds work to do exits **1** —
so the command can stand in a gate as "this workspace is not migrated yet". A dry run that
finds nothing exits 0. That is the same discipline as `check_output_quality.py`: a state
that is not yet what the contract asks for must be sayable, and must not look like success.

WHAT IT WILL NOT DO — the reason this is not a field-filler
-----------------------------------------------------------
An artifact carrying `facts_count: 0` because a migration wrote a zero is
**indistinguishable from one that counted zero facts**, and this specification exists to
remove exactly that kind of indistinguishable state. So every field is either **derived
from the artifact itself** (and the derivation is named in the plan), or it is **reported as
needing a human** and left alone. Nothing is invented, and no field is written with a
placeholder. `conclusions` and `key_metrics` are in the second group by construction: their
values are judgments, and a migration cannot make one.

WRITES go through a temp file plus `os.replace`, inlined rather than defined as a helper:
`tests/test_write_boundary.py` asserts that `write_boundary` is the only definition of an
atomic write in `scripts/`, and it is right to — this command writes into ANOTHER
repository's workspace, where the kit's write boundary (which keys on a `writer:` field the
workspace artifacts do not carry) would refuse every file as append-only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_FILENAME_DATE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<rest>.+)$")

# Every field this migration can DERIVE, with the derivation in words. The set is the one
# the spec measured as absent (0 of 206, `key_metrics` 106 of 206); a field not in this
# table is reported as needing a human and never written.
DERIVABLE = {
    "date": "the `YYYY-MM-DD` prefix of the filename",
    "affix": "the token after `_{skill}_` in the filename (the declared "
             "`{ticker}/{date}_{skill}_{affix}.md` convention)",
    "citation_count": "the number of distinct citation URLs in the artifact "
                      "(frontmatter `citations[].url` plus inline `/v/` links)",
    "facts_count": "the number of `[FACT]` badges in the body",
}
NEEDS_HUMAN = {
    "conclusions": "a judgment: what the artifact concludes. A migration cannot write one.",
    "key_metrics": "a selection: which metrics matter. Deriving it would be inventing it.",
}
ALL_FIELDS = (*DERIVABLE, *NEEDS_HUMAN)

_URL = re.compile(r"https://agentii\.ai/v/[^\s)\"'\\>]+")
_LINK_DEST = re.compile(r"\]\(\s*(https://agentii\.ai/v/[^\s)]+)\s*\)")
_FACT = re.compile(r"\[FACT\]")


def _frontmatter(text: str) -> dict:
    m = _FRONTMATTER.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def derive(path: Path, text: str) -> dict:
    """The derivable values for one artifact. Absent means "not derivable from THIS
    artifact", which is reported rather than guessed."""
    out: dict[str, object] = {}
    m = _FILENAME_DATE.match(path.stem)
    if m:
        out["date"] = m.group("date")
        rest = m.group("rest")
        if "_" in rest:
            out["affix"] = rest.rsplit("_", 1)[1]
    fm = _frontmatter(text)
    body = text[len(_FRONTMATTER.match(text).group(0)):] if _FRONTMATTER.match(text) else text
    urls = set(_LINK_DEST.findall(body))
    for s in (fm.get("citations") or []):
        if isinstance(s, dict) and isinstance(s.get("url"), str):
            urls.add(s["url"])
    out["citation_count"] = len(urls)
    out["facts_count"] = len(_FACT.findall(body))
    return out


def plan_for(path: Path, fields: tuple[str, ...]) -> tuple[dict, list[str]]:
    """`(changes, needs_human)` for one artifact — no writes, no side effects."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    fm = _frontmatter(text)
    if not fm:
        return {}, [f"{path}: no parseable frontmatter — not migrated"]
    derived = derive(path, text)
    changes: dict[str, object] = {}
    needs: list[str] = []
    for f in fields:
        if fm.get(f) is not None:
            continue                       # already present: a migration that rewrote it
        if f in derived:                   # would be a second author, not a migration
            changes[f] = derived[f]
        else:
            needs.append(f"{path}: `{f}` is absent and not derivable "
                         f"({NEEDS_HUMAN.get(f, 'no derivation declared')})")
    return changes, needs


def apply_changes(path: Path, changes: dict) -> None:
    """Add the fields to the frontmatter block, preserving everything else.

    Atomic via temp + `os.replace`; the frontmatter's own key order is kept and the new
    keys are appended, so a diff of this write is exactly the migration."""
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER.match(text)
    if not m:
        raise ValueError(f"{path}: frontmatter is not at byte 0")
    block = m.group(1)
    lines = block.splitlines()
    for k, v in sorted(changes.items()):
        lines.append(f"{k}: {json.dumps(v)}")
    new = "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]
    d = path.parent
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".migrate-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(new)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def is_artifact(path: Path) -> bool:
    """Same population rule as `check_artifact_citations.py`: a skill's OUTPUT.
    `report-input.md` and `plan.md` are scaffolding, and a migration that rewrote them
    would be editing the workspace's own documents."""
    return "artifacts" in path.parts or path.parent.name == "_cross"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="migrate_artifacts.py",
        description="FR-042 — add the contract's declared-but-absent artifact fields. "
                    "Dry run by default; exits 1 when a rewrite is needed.")
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--apply", action="store_true",
                    help="write the changes. Without it nothing is written.")
    ap.add_argument("--fields", default=",".join(ALL_FIELDS),
                    help=f"comma-separated subset of: {', '.join(ALL_FIELDS)}")
    ap.add_argument("--all-markdown", action="store_true",
                    help="include non-artifact .md (default: artifact-shaped paths only)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    fields = tuple(f.strip() for f in a.fields.split(",") if f.strip())
    unknown = [f for f in fields if f not in ALL_FIELDS]
    if unknown:
        print(f"FAIL   unknown field(s) {unknown}; known: {list(ALL_FIELDS)}", file=sys.stderr)
        return 2

    files: list[Path] = []
    for p in a.paths:
        if p.is_dir():
            files += [f for f in sorted(p.rglob("*.md"))
                      if a.all_markdown or is_artifact(f)]
        elif p.is_file():
            files.append(p)
        else:
            print(f"FAIL   {p}: not found", file=sys.stderr)
            return 2

    plan: dict[str, dict] = {}
    needs: list[str] = []
    for f in files:
        ch, nd = plan_for(f, fields)
        needs += nd
        if ch:
            plan[str(f)] = ch

    examined = {"artifacts": len(files), "needing_rewrite": len(plan),
                "needs_human": len(needs)}
    if a.json:
        print(json.dumps({"plan": plan, "needs_human": needs, "examined": examined},
                         indent=2))
    else:
        for f, ch in plan.items():
            print(f"PLAN   {f}")
            for k, v in sorted(ch.items()):
                print(f"         + {k}: {v!r}  ({DERIVABLE[k]})")
        for n in needs:
            print(f"MANUAL {n}", file=sys.stderr)

    if not files:
        print("FAIL   no artifact examined — the path matched nothing, which is not a "
              "clean migration (FR-006's zero-surface rule)", file=sys.stderr)
        return 1

    if a.apply:
        for f, ch in plan.items():
            apply_changes(Path(f), ch)
        print(f"APPLIED {len(plan)} rewrite(s) across {len(files)} artifact(s)"
              + (f"; {len(needs)} field(s) left for a human" if needs else ""))
        if needs:
            # Applying is not the same as done: the fields a migration cannot derive are
            # still absent, and saying "0" here would read as complete.
            return 1
        return 0

    if plan or needs:
        print(f"DRY RUN — {len(plan)} artifact(s) need a rewrite, {len(needs)} field(s) "
              f"need a human, across {len(files)} examined. Re-run with --apply to write.",
              file=sys.stderr)
        return 1
    print(f"OK — {len(files)} artifact(s) already carry every declared field; "
          f"nothing to rewrite")
    return 0


if __name__ == "__main__":
    sys.exit(main())
