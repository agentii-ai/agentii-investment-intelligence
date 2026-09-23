#!/usr/bin/env python3
"""Bring every skill's `## Preflight` tracing line up to v1.1 (spec 060, 2026-09-23).

**Why this exists.** The shipped skills were migrated to *pointers* by
`scripts/dev/ctx_opt_us2_preflight.py` (US2, T016+T017), and that migration was right — the Phase 28
gates forbid inlining the tracing block (`scripts/check.py:1274-1280`). What it left behind was a
pointer that names the header but not **the carry**: the run id is minted once at `initialize`, arrives
as `_run_id` in every `tools/call` result, and the *caller* sends it on every subsequent call. Measured
2026-09-23 across the 70 skills in scope: **zero** mentioned `_run_id`, `parent=` or `instance=`, and
four different pointer shapes were in use. An agent that reads "include the header per
contracts/…" and nothing else has no instruction to carry the id — which is how one conversation
fragments into several runs as soon as the proxy's instance changes, and how the call tree stays flat.

**What it does** — inside each `## Preflight` section only:

  * strips a prose pre-flight sentence (any wording) whose pointer is `contracts/preflight.md`,
    because `ctx_opt_us2_preflight.py` has already inserted the canonical one-liner under the heading
    and a second copy is what a re-run of that script would otherwise duplicate;
  * replaces the tracing sentence — the `Include the …X-Agentii-Trace…` form (including the one file
    where it wraps across two lines) and the `Propagate X-Agentii-Trace per …` form — with `TRACE_PTR`;
  * keeps everything else on the line, so a skill-specific clause riding beside the pointer
    (`Confirm ticker resolution via search_companies before catalyst queries.`) survives.

Idempotent: a file already carrying `TRACE_PTR` and no superseded sentence is left untouched.

After `--apply`, propagate (the repository's own rules, `README.md` § Making It Yours):

    python3 scripts/sync-agent-skills.py          # → plugins/agent-plugins/*/skills/agentii/*
    bash scripts/assemble-agentii-namespace.sh    # symlinks; no text change, run for completeness
    python3 packaging/export.py                   # → packaging/targets/ (T114 byte-compares)

Usage:
    python3 scripts/dev/trace_instruction_v1_1.py            # dry run — prints what would change
    python3 scripts/dev/trace_instruction_v1_1.py --apply
"""
import argparse
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILES = sorted(glob.glob(str(ROOT / "plugins/vertical-plugins/**/skills/agentii/*/SKILL.md"), recursive=True))

TRACE_PTR = "Include the `X-Agentii-Trace` header on every tool call per `contracts/x-agentii-trace-header.md` — carry the `_run_id` from your first tool result and name yourself (and your parent, if you were spawned)."

# The canonical pre-flight one-liner, in the wording `ctx_opt_us2_preflight.py` already inserted.
PREFLIGHT_PTR = "Run canonical pre-flight per `contracts/preflight.md`."

# The two superseded forms. Both are sentence-level so a skill-specific clause on the same line lives.
SUPERSEDED_TRACE = [
    re.compile(r"Include the `X-Agentii-Trace` header on every tool call per\s*"
               r"`contracts/x-agentii-trace-header\.md`\."),
    re.compile(r"Propagate X-Agentii-Trace(?: header)? per `contracts/x-agentii-trace-header\.md`\."),
]

# A prose pre-flight sentence in any wording — replaced by the canonical one-liner at the heading.
SUPERSEDED_PREFLIGHT = re.compile(r"Run (?:the )?canonical pre-flight.*?`contracts/preflight\.md`\.")

PREFLIGHT_HEADING = re.compile(r"^## Preflight\s*$", re.MULTILINE)
NEXT_H2 = re.compile(r"^## ", re.MULTILINE)


def migrate(text: str) -> str:
    head = PREFLIGHT_HEADING.search(text)
    if not head:
        return text
    after = NEXT_H2.search(text, head.end())
    end = after.start() if after else len(text)
    block, rest = text[head.end():end], text[end:]

    if TRACE_PTR in block and PREFLIGHT_PTR in block \
            and not any(r.search(block) for r in SUPERSEDED_TRACE) \
            and not any(SUPERSEDED_PREFLIGHT.search(ln) and PREFLIGHT_PTR not in ln
                        for ln in block.split("\n")):
        return text                                   # already converged

    # Sentence-level surgery, so a skill-specific clause riding on the same line survives — and only
    # the lines actually touched lose their outer whitespace (an indented continuation line, or a
    # nested bullet, is content and must keep its indentation).
    #
    # The trace substitution runs on the **block**, not line by line, because one shipped file wraps
    # the old pointer across two lines (`…on every tool call per` / `` `contracts/…md`. ``) and a
    # line-based pass cannot see a sentence split in half — which is how that one file survived the
    # first run of this script and was caught by Check 18 instead.
    for r in SUPERSEDED_TRACE:
        block = r.sub(TRACE_PTR, block)

    lines = []
    for ln in block.split("\n"):
        line, touched = ln, False
        if SUPERSEDED_PREFLIGHT.search(line) and PREFLIGHT_PTR not in line:
            line = SUPERSEDED_PREFLIGHT.sub("", line)
            touched = True
        lines.append(line.lstrip().rstrip() if touched else line)

    body = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    # The heading keeps one canonical pre-flight pointer beside the tracing line (US2 inserted it for
    # some skills and not others; one shape is the point).
    if PREFLIGHT_PTR not in body:
        body = f"\n\n{PREFLIGHT_PTR}" + body
    return text[:head.end()] + body + rest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = ap.parse_args()

    changed = []
    for f in FILES:
        p = Path(f)
        before = p.read_text(encoding="utf-8")
        after = migrate(before)
        if after == before:
            continue
        changed.append(p.relative_to(ROOT))
        if args.apply:
            p.write_text(after, encoding="utf-8")

    verb = "updated" if args.apply else "would update"
    for rel in changed:
        print(f"  {verb} {rel}")
    print(f"{verb} {len(changed)} of {len(FILES)} files")
    if changed and not args.apply:
        print("\ndry run — re-run with --apply, then:")
        print("  python3 scripts/sync-agent-skills.py && bash scripts/assemble-agentii-namespace.sh"
              " && python3 packaging/export.py")


if __name__ == "__main__":
    main()
