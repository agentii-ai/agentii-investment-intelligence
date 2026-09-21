#!/usr/bin/env python3
"""check_gate_fields.py — every artifact-frontmatter field a gate reads must be declared.

spec 058 FR-037 / T015. Called from `check.py` (which delegates rather than reimplements,
the pattern Check 32 established), and runnable standalone.

THE RULE
--------
`contracts/artifact-frontmatter.yaml` declares the fields. This script reads the gate
sources and fails on any field they read that the contract does not declare. The defect
it removes: `entity_claims` was read by five gates and absent from 128 artifacts, and
nothing compared the reading against a declaration, so every cross-run contradiction
check in theses 001–003 was vacuous and silent.

WHAT IT CANNOT SEE, stated because an unreported gap reads as coverage
---------------------------------------------------------------------
A detector that only understood `fm.get("literal")` would miss all five pins —
`g1_gate.py` reads them as `for pin in FIVE_PINS: fm.get(pin)`, so the field name is a
loop variable, never a literal. That is this specification's defect applied to its own
enforcement, so loop reads are resolved from the contract's `pin_tuple`, and anything
still unresolvable is REPORTED rather than passed over:

  * `fm.get(<variable>)` where the variable is not a known loop constant
  * `fm.get(<f-string>)` / computed keys
  * a gate importing frontmatter from somewhere this script does not scan

`unresolved` in the returned counts is non-zero exactly when something was skipped. A
zero there means every read was accounted for, not that none were found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "artifact-frontmatter.yaml"

# Not gates: the runner that delegates to this module, and this module. Named, printed in
# the counts, and never pattern-matched — an exclusion nobody can see is how a population
# check stops being one.
RUNNERS = {"check.py", "check_gate_fields.py"}

# `fm.get("field")`, `fm["field"]`, and the loop form `for pin in FIVE_PINS: fm.get(pin)`.
_LITERAL_GET = re.compile(r"\bfm\s*\.get\(\s*[\"']([a-z_][a-z0-9_]*)[\"']")
_LITERAL_IDX = re.compile(r"\bfm\s*\[\s*[\"']([a-z_][a-z0-9_]*)[\"']\s*\]")
_DYNAMIC_GET = re.compile(r"\bfm\s*\.get\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[,)]")
# `for X in CONST:` / `for X in mod.CONST:` / `for X in ("a", "b"):` / and the same
# inside a generator (`any(fm.get(p) for p in CONST)`). The generator form is not a
# `for` STATEMENT, so an anchored regex misses it — which is how four reads stayed
# unresolved while looking like they had been handled.
_FOR_IN = re.compile(
    r"\bfor\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,\s*[a-zA-Z_][a-zA-Z0-9_]*\s*)?in\s+"
    r"((?:[a-z_][a-z0-9_]*\.)?(?:[A-Z_][A-Z0-9_]*|\([^)]*\)))",
)
_ITEMS = re.compile(r"for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*\s+in\s+([a-z_][a-zA-Z0-9_]*)\.items\(\)")
_TUPLE = re.compile(r"^([A-Z_][A-Z0-9_]*)\s*=\s*\(([^)]*)\)", re.M)
_STR = re.compile(r"[\"']([a-z_][a-z0-9_]*)[\"']")


def contract() -> dict:
    return yaml.safe_load(CONTRACT.read_text()) or {}


def declared(doc: dict) -> set[str]:
    names = {f["name"] for f in doc.get("fields") or []}
    names |= set((doc.get("pin_tuple") or {}).get("fields") or [])
    return names


def loop_constants(doc: dict) -> dict[str, set[str]]:
    """Tuple constants that carry field names, resolved from their defining script.

    Declared in the contract rather than guessed: the contract names the constant and
    its file, and this reads the actual tuple so the two cannot drift apart silently.
    """
    out: dict[str, set[str]] = {}
    pt = doc.get("pin_tuple") or {}
    src = ROOT / "scripts" / pt.get("defined_in", "")
    if not src.is_file():
        return out
    for m in _TUPLE.finditer(src.read_text(encoding="utf-8")):
        if m.group(1) == pt.get("const"):
            out[m.group(1)] = set(_STR.findall(m.group(2)))
    return out


def reads_in(path: Path, consts: dict[str, set[str]]) -> tuple[set[str], list[str], list[str]]:
    """(fields read, unresolved patterns, caller-supplied patterns) for one gate script.

    Loop variables resolve through every binding they have in the file, because one
    variable can carry more than one: `dispatch.py` reads `pin` both in
    `any(... for pin in g1_five.FIVE_PINS)` (resolvable) and in
    `for pin, current in current_pins.items()` (caller-supplied). Keeping only one
    binding per name — as the first version did — mis-classifies both.

    Two earlier versions of this function were wrong in ways worth preserving:
    the first SKIPPED `pin` as a presumed-harmless loop variable, dropping exactly the
    five fields `pin_tuple` exists to cover; the second missed generator expressions
    because it anchored on `for` statements, and missed inline tuple literals
    (`for field in ("facts_count", ...)`), which left four real artifact fields
    undeclared while the check reported them as merely unresolved.
    """
    text = path.read_text(encoding="utf-8")
    found = set(_LITERAL_GET.findall(text)) | set(_LITERAL_IDX.findall(text))

    bindings: dict[str, list[str]] = {}
    for var, expr in _FOR_IN.findall(text):
        bindings.setdefault(var, []).append(expr)
    items_vars = {var: src for var, src in _ITEMS.findall(text)}

    unresolved: list[str] = []
    caller: list[str] = []
    for var in _DYNAMIC_GET.findall(text):
        exprs = bindings.get(var)
        resolved = False
        if exprs:
            for expr in exprs:
                bare = expr.split(".")[-1]
                if expr.startswith("("):
                    found |= set(_STR.findall(expr))       # inline tuple literal
                    resolved = True
                elif bare in consts:
                    found |= consts[bare]                  # named constant
                    resolved = True
        if var in items_vars:
            caller.append(
                f"{path.name}: fm.get({var}) — iterates {items_vars[var]}.items(), "
                f"whose keys the caller supplies"
            )
        if not resolved and var not in items_vars:
            unresolved.append(
                f"{path.name}: fm.get({var}) — no resolvable binding: not a known "
                f"constant, no inline tuple, no `for {var} in <CONST>` or "
                f"`for {var}, _ in <dict>.items()` in this file"
            )
    return found, unresolved, caller


def check_a() -> tuple[list[str], dict]:
    """Undeclared reads. Returns (problems, counts)."""
    doc = contract()
    dec = declared(doc)
    consts = loop_constants(doc)
    problems: list[str] = []
    read_anywhere: set[str] = set()
    scanned = 0
    unresolved: list[str] = []
    caller_supplied: list[str] = []

    for name in doc.get("gates") or []:
        p = ROOT / "scripts" / name
        if not p.is_file():
            problems.append(f"{name}: declared as a gate but not found in scripts/")
            continue
        scanned += 1
        f, u, caller = reads_in(p, consts)
        read_anywhere |= f
        unresolved += u
        caller_supplied += caller
        for field in sorted(f - dec):
            problems.append(
                f"{name}: reads artifact frontmatter field '{field}', which "
                f"contracts/artifact-frontmatter.yaml does not declare (FR-037)"
            )

    # The pin tuple must be non-empty: if it resolved to nothing, the five loop-read
    # fields are invisible and every check above is passing over a blind spot.
    if not consts:
        problems.append(
            f"the pin tuple {(doc.get('pin_tuple') or {}).get('const')!r} did not resolve "
            f"in {(doc.get('pin_tuple') or {}).get('defined_in')!r} — five fields read in a "
            f"loop are invisible to this check, so it cannot report them (FR-037)"
        )

    # A read whose field names the workspace supplies is DECLARED, not unknown: the
    # contract names the path and its source. Matching it here keeps `unresolved`
    # meaningful — it must mean "nobody has accounted for this", not "I gave up".
    dyn = {(d.get("script"), d.get("var")): d for d in doc.get("dynamic_reads") or []}
    declared_dynamic: list[str] = []
    still_unknown: list[str] = []
    # Deduplicate: one read pattern can occur at several call sites, and repeating the
    # same explanation once per site buries the distinct findings.
    #
    # The declared-dynamic entries get their OWN wording, added 2026-09-21. The first
    # version re-used the `unresolved` string verbatim and merely filed it under a
    # different heading — so the output read "workspace-declared read path … no
    # resolvable binding: not a known constant, no inline tuple, no `for field in
    # <CONST>` in this file", i.e. a path that IS accounted for, described in the words
    # reserved for one that is not. A reader could not tell the two states apart, which
    # is the distinction `unresolved: 0` is supposed to carry.
    for u in dict.fromkeys(unresolved + caller_supplied):
        hit = next((d for (s, v), d in dyn.items()
                    if u.startswith(f"{s}: fm.get({v})")), None)
        if hit:
            declared_dynamic.append(
                f"{hit.get('script')}: fm.get({hit.get('var')}) — ACCOUNTED FOR as "
                f"dynamic_reads ({hit.get('at')}); the field names come from outside this "
                f"kit, so there is nothing here to enumerate (see the contract entry's "
                f"`consequence` for what that costs)")
        else:
            still_unknown.append(u)

    # FR-037's population, DERIVED rather than declared. The `gates:` list above is
    # hand-maintained, so a new gate that reads artifact frontmatter is invisible to every
    # check in this file until someone remembers to add it — a rule whose coverage is
    # asserted by its own config. The population is mechanical: the shared parser is the
    # boundary. A script calling `g1_gate.parse_frontmatter` or `parse_frontmatter_strict`
    # reads ARTIFACT frontmatter; a script with its own `_parse_frontmatter`
    # (`sync_registry`, `validate_*`) reads SKILL.md frontmatter, which this contract
    # deliberately scopes out.
    readers: set[str] = set()
    script_files = sorted((ROOT / "scripts").glob("*.py"))
    for p in script_files:
        if re.search(r"\bg1_gate\.parse_frontmatter\(|\bparse_frontmatter_strict\(",
                     p.read_text(encoding="utf-8")):
            readers.add(p.name)
    for name in sorted(readers - set(doc.get("gates") or []) - RUNNERS):
        problems.append(
            f"{name}: reads artifact frontmatter through the shared parser but is not "
            f"declared in contracts/artifact-frontmatter.yaml `gates:` — add it there and "
            f"declare the fields it reads (FR-037)")
    problems = list(dict.fromkeys(problems))

    unread = sorted(d for d in dec if d not in read_anywhere)
    # `unread:` entries are fields the CORPUS carries that no gate reads. FR-040: a
    # field recording a condition must trigger an action or be removed — a field that
    # every artifact carries and no process reads is a comment, not a control. The kit
    # cannot remove them (the workspace declares them), so it does the one thing it can:
    # reports them on every run, so the condition cannot be forgotten.
    unread_corpus = [
        f"{u.get('name')} — {u.get('read_by', 'read by nothing')}"
        for u in doc.get("unread") or []
    ]
    return problems, {
        "gates_scanned": scanned,
        "declared": len(dec),
        "read": len(read_anywhere),
        "declared_but_unread": unread,
        "declared_dynamic": declared_dynamic,
        "unresolved": still_unknown,
        "dynamic_paths_declared": len(dyn),
        "corpus_fields_with_no_consumer": unread_corpus,
        "scripts_scanned": len(script_files),
        "artifact_frontmatter_readers": sorted(readers - RUNNERS),
        "runners_excluded": sorted(RUNNERS),
    }


def main(argv: list[str] | None = None) -> int:
    problems, counts = check_a()
    for c in counts["declared_but_unread"]:
        print(f"NOTE   declared but read by no gate (FR-040 shape — consume or remove): {c}")
    for d in counts["declared_dynamic"]:
        print(f"NOTE   declared-dynamic read: {d}")
    for c in counts["corpus_fields_with_no_consumer"]:
        # FR-040 / spec 058 T020. Not a failure: the field is the workspace's to remove
        # and the kit has no data to consume it with. Reported every run so it cannot
        # become invisible — the state it was in before, at 41/41 artifacts correct and
        # 0/41 read.
        print(f"NOTE   corpus field with no consumer (FR-040 — consume or remove, "
              f"owner-run): {c}")
    for u in counts["unresolved"]:
        print(f"FAIL   unresolved read — no contract declaration and no declared "
              f"dynamic path: {u}", file=sys.stderr)
        problems.append(u)
    for p in problems:
        print(f"FAIL   {p}", file=sys.stderr)
    if problems:
        return 1
    print(f"OK     {counts['read']} field(s) read across {counts['gates_scanned']} gate(s), "
          f"{counts['declared']} declared, {len(counts['declared_dynamic'])} declared-dynamic, "
          f"0 unresolved")
    # The `gates:` population is CHECKED, not assumed: every script that reads artifact
    # frontmatter through the shared parser is in it, or this failed above. Printed so the
    # two exclusions are visible in the log rather than in the source only.
    print(f"       gates: population derived from {counts['scripts_scanned']} script(s) — "
          f"{len(counts['artifact_frontmatter_readers'])} reader(s) "
          f"{counts['artifact_frontmatter_readers']}; excluded as runners: "
          f"{counts['runners_excluded']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
