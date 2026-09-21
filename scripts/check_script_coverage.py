#!/usr/bin/env python3
"""check_script_coverage.py — FR-003: every script CI runs must be exercised by a test.

T043. The rule is narrow, and the narrowness is the finding: **a script that CI runs and no
test covers can break the pipeline while every local check stays green.** Measured
2026-09-21: six such scripts exist (the `validate-*.py` family), and **two of them are
failing right now** — 34 violations between them — which nobody sees because `check.py`,
the gate everyone runs, does not invoke them. That is this specification's defect class in
its purest form: a rule with an enforcement point that never fires.

THE POPULATION RULE, stated because the first version of T043 got it wrong. "CI runs it"
means: invoked by a step in `.github/workflows/*.yml`, **or** reached from `check.py` (by
import or by `spec_from_file_location`). It does NOT mean "no test names it" — that is a
name-grep over the whole `scripts/` directory, and it produced 19 where 12 of them are
scripts CI never runs at all. Building the gate to those 19 would have opened with twelve
non-defects; the honest number is 6, and it changes as scripts are covered.

"Covered" means a test REACHES the script, by one of two routes, and the second is why the
rule is not a name-grep:
  * a **reference** — the script's name appears as a real string constant in a test module
    (paths are built as `KIT / "scripts" / "x.py"`, so the joined literal never appears);
    docstrings are excluded, because `validate-citations.py`'s only "reference" was a
    sentence in prose;
  * a **reach** — the script is imported by a script a test runs. `sync_registry.py` is
    exercised by every suite run via `check.py`, so reporting it uncovered was a false
    positive of exactly the kind T043's text warns about.

The limit is stated rather than implied: this gate proves a script is exercised, NOT that
its behaviour is asserted. The per-script tests are what make the coverage real, and three
of them currently carry `xfail(strict=True)` — because running these scripts is how the kit
found out its CI is red (34 violations in `validate-multi-ticker-syntax.py`, 1 in
`validate-prose-safety.py`) while its local gate stayed green.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
TESTS = ROOT / "tests"

# A workflow step that runs a script: `run: python3 scripts/<name>.py` (optionally `bash`,
# optionally with `|| ...`); also `bash scripts/<name>.sh`.
_WORKFLOW_INVOKE = re.compile(r"\b(?:python3?|bash|sh)\s+(scripts/[A-Za-z0-9_.\-]+\.(?:py|sh))")
# check.py reaching a script: `import <mod>` or `spec_from_file_location("<x>", ...)`.
_CHECK_IMPORT = re.compile(r"^\s*import\s+([a-z_][a-z0-9_]*)", re.M)


def ci_run(root: Path = ROOT) -> dict[str, str]:
    """script filename -> why it is considered CI-run. Reported, not just counted.

    `root` is a parameter rather than a module global so a test can point it at a fixture:
    the first version read the globals, and the test that patched them crashed on a missing
    `scripts/check.py` — a shape the REAL tree never has, but a fixture does.
    """
    out: dict[str, str] = {}
    wf_dir = root / ".github" / "workflows"
    for wf in sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml")):
        for m in _WORKFLOW_INVOKE.finditer(wf.read_text(encoding="utf-8")):
            out.setdefault(Path(m.group(1)).name, f"{wf.name} invokes it")
    check = root / "scripts" / "check.py"
    if not check.is_file():
        return out
    text = check.read_text(encoding="utf-8")
    names = {p.stem: p.name for p in sorted((root / "scripts").glob("*.py"))}
    for mod in set(_CHECK_IMPORT.findall(text)):
        if f"{mod}.py" in names.values():
            out.setdefault(f"{mod}.py", f"check.py imports {mod}")
    # `spec_from_file_location("x", ROOT / "scripts" / "<y>.py")` — the other reach path
    for m in re.finditer(r'spec_from_file_location\([^,]+,\s*[^)]*?/([A-Za-z0-9_.\-]+\.py)', text):
        out.setdefault(m.group(1), "check.py loads it by path")
    return out


def _code_strings(path: Path) -> list[str]:
    """Every string literal in a test module that is NOT a docstring.

    The three versions this function replaced, and why each was wrong, are the point:
      1. `stem in text` — a docstring mentioning `validate-citations.py` counted as
         coverage, the name-grep weakness one layer down (measured: that script's only
         "reference" was a sentence in prose);
      2. `"scripts/<name>" in text` — too strict: these tests build paths as
         `KIT / "scripts" / "x.py"`, so the joined literal never appears and EVERY script
         read as uncovered;
      3. scanning lines for the name plus a `scripts` token — a multi-line docstring's inner
         lines are not quote-prefixed, so prose could still slip through.
    Reading the AST sees only real string constants in code, which is what a reference is.
    """
    import ast
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            d = ast.get_docstring(node, clean=False)
            if d is not None:
                docstrings.add(d)
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and n.value not in docstrings]


def referenced_in_tests(script_name: str, tests_dir: Path) -> bool:
    """Does a test REFERENCE this script (a path or an import), rather than mention it?"""
    stem = Path(script_name).stem
    import_form = re.compile(rf"^\s*(?:from|import)\s+{re.escape(stem)}\b", re.M)
    for t in tests_dir.rglob("*.py"):
        if any(script_name in s for s in _code_strings(t)):
            return True
        if import_form.search(t.read_text(encoding="utf-8", errors="ignore")):
            return True
    return False


def imported_by(script_name: str, root: Path = ROOT) -> set[str]:
    """The module names this script imports from its own directory."""
    p = root / "scripts" / script_name
    if p.suffix != ".py" or not p.is_file():
        return set()
    return set(_CHECK_IMPORT.findall(p.read_text(encoding="utf-8", errors="ignore")))


def covered_names(ci: dict[str, str], root: Path = ROOT) -> tuple[set[str], dict[str, str]]:
    """Which CI-run scripts actually EXECUTE under the suite, and why.

    NAMED-OR-REACHED, and the second half is not a convenience: `sync_registry.py` is
    imported by `check.py`, and `tests/test_check_extensions.py` runs `check.py` in a
    sandbox — so `sync_registry.build_entries()` executes every suite run. A gate whose rule
    was "a test must name it" reported that as uncovered, which is a false positive of
    exactly the kind T043's own text warns about. Coverage propagates along the import
    edge; a fixpoint is enough because the graph is tiny.
    """
    covered: set[str] = set()
    why: dict[str, str] = {}
    # module name -> script filename. The first version compared a MODULE (`sync_registry`)
    # against FILENAMES (`sync_registry.py`) and so never matched, reporting a script as
    # uncovered while `tests/test_check_extensions.py` exercised it on every run.
    by_module = {Path(n).stem: n for n in ci}
    for n in ci:
        if referenced_in_tests(n, root / "tests"):
            covered.add(n)
            why[n] = "a test references it"
    # Forward, not backward: for each script a test RUNS, everything IT imports also
    # executes under the suite. The first version asked the reverse question — "does this
    # uncovered script import something covered?" — which is the dependency direction and
    # covered nothing.
    changed = True
    while changed:
        changed = False
        for runner in sorted(covered):
            for mod in imported_by(runner, root):
                dep = by_module.get(mod)
                if dep and dep not in covered:
                    covered.add(dep)
                    why[dep] = f"imported by {runner}, which a test runs"
                    changed = True
    return covered, why


def check(root: Path = ROOT) -> tuple[list[str], dict]:
    ci = ci_run(root)
    covered, why = covered_names(ci, root)
    uncovered = {n: r for n, r in sorted(ci.items()) if n not in covered}
    problems = [
        f"{n}: CI runs it ({r}) and no test reaches it — it can break the pipeline while "
        f"every local check stays green (FR-003)"
        for n, r in uncovered.items()
    ]
    return problems, {
        "ci_run": sorted(ci),
        "ci_run_reasons": ci,
        "covered": sorted(covered),
        "covered_reasons": why,
        "uncovered": sorted(uncovered),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_script_coverage.py",
        description="FR-003 — name any script CI runs that no test covers.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    problems, counts = check()
    if a.json:
        print(json.dumps({"problems": problems, **counts}, indent=2))
    for p in problems:
        print(f"FAIL   {p}", file=sys.stderr)

    if not counts["ci_run"]:
        # The population itself must not be able to collapse to nothing: a workflow that
        # stopped invoking scripts would make this gate green and meaningless.
        print("FAIL   no CI-run script was found at all — the workflow/import scan is "
              "broken, which is not the same as everything being covered", file=sys.stderr)
        return 1
    if problems:
        if not a.json:
            print(f"FAIL — {len(problems)} of {len(counts['ci_run'])} CI-run script(s) are "
                  f"uncovered by any test", file=sys.stderr)
        return 1
    print(f"OK — {len(counts['ci_run'])} CI-run script(s), all referenced by a test "
          f"({', '.join(counts['ci_run'])})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
