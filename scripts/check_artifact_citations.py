#!/usr/bin/env python3
"""check_artifact_citations.py — FR-041: a figure without a RESOLVABLE citation fails.

A NEW script, deliberately not an extension of `scripts/validate-citations.py`. That one
enforces the citation *format inside committed SKILL.md files*, where `{placeholder}`
segments are legitimate because the file is an instruction. This one enforces the
citation form in **artifacts**, where a `{placeholder}` is an unexpanded template and a
link that cannot resolve is a citation that does not exist. One rule, one surface, one
implementation — the alternative is the two-implementations-of-one-check defect
`check.py`'s own header calls out (spec 058 T021).

THE ADMITTED FORM, and where it comes from
------------------------------------------
The rule is not invented here. The workspace contract that governs artifacts states it
(`theses/002-evidence-validation/contracts/artifact-frontmatter.yaml`):
`citation_url_wellformed` (level: fail) requires
`^https://agentii\\.ai/v/{TICKER}/{citation_id}/{page}$` with an **uppercase ticker**, and
says in its own words that the ticker-less short form does NOT resolve — the portal route
redirects to `api.agentii.ai/v1/view_document/{ticker}/{citation_id}` and cannot join
without a ticker. The same contract's schema block pins `citation_id` to `^[a-z]+[0-9]+$`
(e.g. `sec8`, `sec109`). Both are implemented here as stated.

WHERE A CITATION LIVES — and what that excludes
-----------------------------------------------
Two positions count: a **markdown link destination** (`](https://agentii.ai/v/...)`) and a
**frontmatter scalar**. Prose that QUOTES the form does not, and that distinction is
load-bearing rather than pedantic: measured 2026-09-21, all three occurrences of the
literal template in the corpus are artifacts *quoting the instruction* while reporting
that it is unsatisfiable for knowledge rows. A gate that flagged those would fail the
three artifacts that are doing the right thing. `tests/test_artifact_citations.py` holds
that case as a fixture, because a rule that cannot tell documentation from a defect is a
rule that gets switched off.

The same measurement found the two conditions this gate DOES fire on: two inline
destinations with the thesis number in the `citation_id` slot (`/v/SPEC/005/958`,
`/v/SPEC/005/435`) and one frontmatter url carrying the platform's internal
`agentii://source/...` identifier nested inside the public path.

WHAT IT CANNOT SEE, stated because an unreported gap reads as coverage
---------------------------------------------------------------------
It does not check that a citation resolves *to the right page* — only that its form is
one the portal can join on. A well-formed link to the wrong page passes, and that is the
defect the workspace's `table_pages_quote_cells_not_prose` rule exists for, one layer up.
Nor does it validate the ticker against a ticker universe: the contract says "uppercase
ticker", so `SPEC` passes the ticker test and is caught by the `citation_id` test instead.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

VIEW_PREFIX = "https://agentii.ai/v/"
# Candidate URLs, anywhere. The verdict decides whether the position is a citation.
# `<…>` and `{…}` placeholders are captured rather than truncated at the bracket: a
# truncated URL in a failure message is a message about a string that does not exist.
VIEW_ANYWHERE = re.compile(r"https://agentii\.ai/v/(?:[^\s)\"'\\>]|<[^>\n]*>|\{[^}\n]*\})+")
# A frontmatter value that IS a citation url: the whole scalar, quotes/space aside.
# The contract's rule is `must match ^…$` — an anchored statement about a value.
_ANCHORED_URL = re.compile(r"\s*https://agentii\.ai/v/\S+\s*")
# A markdown link destination: ](url)
LINK_DEST = re.compile(r"\]\(\s*(https://agentii\.ai/v/[^\s)]+)\s*\)")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def is_artifact_path(p: Path, root: Path) -> bool:
    """Is this file a skill OUTPUT, or workspace scaffolding?

    FR-041 is about artifacts. Measured 2026-09-21: scanning a workspace naively took in
    316 `.md` files, and the largest finding of the run was `report-input.md` — 1,541
    inline links, no `citations` block — which is a *derived input for the report*, not a
    skill's output. A gate whose biggest finding is about a file outside its rule gets
    ignored, and the population is the same trap T043's "19 scripts" fell into.

    An artifact is a file under an `artifacts/` directory, or one in a `_cross/` directory
    (the cross-stock synthesis is also a skill output, spec 046 Q72). Everything else —
    `plan.md`, `report-input.md`, `contracts/`, session histories — is scaffolding.
    """
    # The path's OWN components, not the root-relative ones: a caller who passes the
    # `artifacts/` directory itself as the root would otherwise have every file skipped,
    # because "artifacts" is the root and not a relative part. Found by the corpus test.
    if "artifacts" in p.parts:
        return True
    return p.parent.name == "_cross" or p.name.endswith("_synthesis.md")


def verdict(url: str) -> str | None:
    """`None` when the URL is one the portal can join on, else the reason it cannot.

    The reasons are the contract's, not this script's: each says what the missing piece
    costs, because "malformed URL" tells an analyst nothing about the fix.
    """
    core = url.split("#")[0].split("?")[0].rstrip(".,;:'\"")
    if not core.startswith(VIEW_PREFIX):
        return None
    path = core[len(VIEW_PREFIX):]
    if "://" in path:
        return (
            "a nested URL scheme inside the citation path — the platform's internal "
            "`agentii://source/<uuid>` identifier was pasted into the public form, so "
            "the `citation_id` slot holds a whole URL (FR-041)")
    if "{" in path or "}" in path:
        return (
            "an unexpanded template in a citation position — the link is an instruction "
            "that was never filled in, and resolves to nothing (FR-041)")
    segs = path.split("/")
    if len(segs) == 2:
        return (
            "the ticker-less short form — the portal route redirects to "
            "`api.agentii.ai/v1/view_document/{ticker}/{citation_id}` and cannot join "
            "without a ticker (per the workspace contract's own note)")
    if len(segs) != 3:
        return (
            f"{len(segs)} path segment(s) after `/v/`; the admitted form is "
            f"`/v/{{TICKER}}/{{citation_id}}/{{page}}` (3)")
    ticker, cid, page = segs
    if not re.fullmatch(r"[A-Z][A-Z0-9.\-]*", ticker):
        return f"ticker {ticker!r} is not uppercase — the contract requires one to be present"
    if not re.fullmatch(r"[a-z]+[0-9]+", cid):
        return (
            f"citation_id {cid!r} does not match `[a-z]+[0-9]+` (e.g. `sec8`, `sec109`). "
            f"A bare number is usually a section or thesis reference that was given a "
            f"citation slot it does not belong in")
    if not re.fullmatch(r"\d+", page):
        return f"page {page!r} is not numeric"
    return None


def _frontmatter(text: str) -> dict:
    m = _FRONTMATTER.match(text)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _strings(node) -> list[str]:
    """Every string in a nested structure — frontmatter values, at any depth."""
    out: list[str] = []
    if isinstance(node, str):
        out.append(node)
    elif isinstance(node, dict):
        for v in node.values():
            out.extend(_strings(v))
    elif isinstance(node, list):
        for v in node:
            out.extend(_strings(v))
    return out


def check_text(text: str, *, where: str = "") -> tuple[list[str], dict]:
    """The problems in one artifact's text, plus what was examined.

    Returns `(problems, counts)`. `counts` is returned rather than logged because the
    caller — the baseline, or the CLI's summary — has to be able to tell "found nothing"
    from "examined nothing" (spec 046 Q105's `EXECUTED|VACUOUS`).
    """
    problems: list[str] = []
    fm = _frontmatter(text)
    body = text[len(_FRONTMATTER.match(text).group(0)):] if _FRONTMATTER.match(text) else text

    # Position 1 — frontmatter scalars, at any depth. This is where the workspace
    # contract's rule applies, and where the nested-scheme case lives.
    #
    # ANCHORED, because the contract's rule is anchored: "every `citations[].url` must
    # match ^…$" is a statement about a value, not a substring search inside one.
    # Measured 2026-09-21: an artifact's `basis:` field reads "analogue rows carry
    # citation_url of the form https://agentii.ai/v/cases/<case_id>, which cannot match
    # the workspace URL_RE …" — a SENTENCE documenting the served form. A substring scan
    # fails it; an anchored match does not, and the artifact is right.
    fm_urls: list[str] = []
    fm_mentions = 0
    for s in _strings(fm):
        if _ANCHORED_URL.fullmatch(s):
            fm_urls.append(s.strip())
        elif VIEW_ANYWHERE.search(s):
            fm_mentions += 1          # a URL named inside prose: documentation
    for u in fm_urls:
        why = verdict(u)
        if why:
            problems.append(f"{where}: frontmatter url {u!r} — {why}")

    # Position 2 — markdown link destinations in the body. Prose that quotes the form in
    # a code span or a blockquote is NOT a destination and is not examined.
    body_urls = LINK_DEST.findall(body)
    for u in body_urls:
        why = verdict(u)
        if why:
            problems.append(f"{where}: inline link {u!r} — {why}")

    # FR-041's other half: a figure cited in prose but absent from the record. An artifact
    # whose body links citations while its frontmatter carries no `citations` block is
    # citing in a form nothing can join on later — the links are not addressable.
    citations = fm.get("citations")
    if body_urls and not citations:
        problems.append(
            f"{where}: {len(body_urls)} inline `/v/` link(s) but no non-empty "
            f"`citations` block — the artifact cites in prose and records nothing, so no "
            f"citation is addressable (FR-041)")

    return problems, {
        "frontmatter_urls": len(fm_urls),
        "frontmatter_url_mentions": fm_mentions,
        "inline_links": len(body_urls),
        "citations_block": bool(citations),
    }


def check_artifacts(root: Path, *, artifacts_only: bool = True) -> tuple[list[str], dict]:
    """Every artifact under `root`, recursively.

    `artifacts_only` is the default because that is FR-041's surface; `--all-markdown`
    widens it, and either way the count of files SKIPPED is reported, so a scope choice
    cannot silently shrink the population (the T043 lesson, applied here).
    """
    problems: list[str] = []
    examined = {"artifacts": 0, "frontmatter_urls": 0, "frontmatter_url_mentions": 0,
                "inline_links": 0, "with_citations_block": 0, "skipped_non_artifact": 0}
    for art in sorted(root.rglob("*.md")):
        if artifacts_only and not is_artifact_path(art, root):
            examined["skipped_non_artifact"] += 1
            continue
        examined["artifacts"] += 1
        p, c = check_text(art.read_text(encoding="utf-8", errors="ignore"),
                          where=str(art))
        problems += p
        examined["frontmatter_urls"] += c["frontmatter_urls"]
        examined["frontmatter_url_mentions"] += c["frontmatter_url_mentions"]
        examined["inline_links"] += c["inline_links"]
        examined["with_citations_block"] += int(c["citations_block"])
    return problems, examined


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_artifact_citations.py",
        description="FR-041 — every citation in an artifact must be one the portal can "
                    "join on, and a figure cited must be recorded.")
    ap.add_argument("paths", nargs="+", type=Path,
                    help="artifact files or directories to scan")
    ap.add_argument("--all-markdown", action="store_true",
                    help="scan every .md, not only artifact-shaped paths (artifacts/ and "
                         "_cross/). Widening the scope is allowed; hiding it is not — the "
                         "skipped count is reported either way.")
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    a = ap.parse_args(argv)

    problems: list[str] = []
    examined = {"artifacts": 0, "frontmatter_urls": 0, "frontmatter_url_mentions": 0,
                "inline_links": 0, "with_citations_block": 0, "skipped_non_artifact": 0}
    for p in a.paths:
        if p.is_dir():
            pr, ex = check_artifacts(p, artifacts_only=not a.all_markdown)
        elif p.is_file():
            pr, ex = check_text(p.read_text(encoding="utf-8", errors="ignore"),
                                where=str(p))
            ex = {"artifacts": 1, "frontmatter_urls": ex["frontmatter_urls"],
                  "frontmatter_url_mentions": ex["frontmatter_url_mentions"],
                  "inline_links": ex["inline_links"],
                  "with_citations_block": int(ex["citations_block"])}
        else:
            print(f"FAIL   {p}: not found", file=sys.stderr)
            return 2
        problems += pr
        for k in examined:
            examined[k] += ex.get(k, 0)

    if a.json:
        print(json.dumps({"problems": problems, "examined": examined}, indent=2))
    else:
        for m in problems:
            print(f"FAIL   {m}", file=sys.stderr)
    if examined["artifacts"] == 0:
        # Not the same result as "clean". Unreachable from the CLI with a real path, but
        # the guard belongs here rather than in a caller's memory.
        print("FAIL   no artifact examined — the path matched nothing, which is not a "
              "pass (FR-006's zero-surface rule, one layer up)", file=sys.stderr)
        return 1
    if problems:
        if not a.json:
            print(f"FAIL — {len(problems)} citation problem(s) across "
                  f"{examined['artifacts']} artifact(s) "
                  f"({examined['skipped_non_artifact']} non-artifact .md skipped)",
                  file=sys.stderr)
        return 1
    print(f"OK — {examined['artifacts']} artifact(s), "
          f"{examined['frontmatter_urls']} frontmatter url(s), "
          f"{examined['inline_links']} inline link(s), "
          f"{examined['with_citations_block']} with a citations block, "
          f"{examined['frontmatter_url_mentions']} url mention(s) in prose (documentation, "
          f"not examined), {examined['skipped_non_artifact']} non-artifact .md skipped, "
          f"0 problems")
    return 0


if __name__ == "__main__":
    sys.exit(main())
