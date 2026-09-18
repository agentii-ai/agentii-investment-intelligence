#!/usr/bin/env python3
"""audit_named_artifacts.py — spec 046: which named artifacts actually exist?

Spec 046 names ~86 concrete artifacts (scripts, templates, commands, runtime
files). Prose cannot be trusted to say which of them are built: the spec's own
header admits it "reads as false if read as all-implemented", and three of Part I's
six ✅ marks were shown to be wrong (Q113). This script answers the question by
measurement.

Four verdicts, and the distinction between the last two is the point:

  BUILT       the file (or command) resolves
  WIRING-ONLY every part exists EXCEPT the dispatch entry point — the work is a
              table entry, not a build
  MISSING     named, not built, and not rejected anywhere
  ABSENT-OK   named, not built, and *deliberately* rejected by a decision
              (Q4's 派生优于台账 family). Reporting these as gaps would be wrong.

Q105's lesson applies here directly: "not found" and "never asked for" are
different states, and collapsing them is how a mechanism comes to return an empty
success. `ABSENT-OK` is the audit's own VACUOUS marker.

Usage:
    python3 scripts/audit_named_artifacts.py              # report
    python3 scripts/audit_named_artifacts.py --strict     # exit 1 if MISSING
    python3 scripts/audit_named_artifacts.py --counts     # verify the spec's NUMBERS

`--counts` exists because the same defect afflicts quantities. On 2026-09-18 every
one of seven checked numbers in spec 046's plan was wrong (62 skills -> 80; 9
templates -> 13; "14% mode substrate" -> 96%; "53 of 62 skills default-only" -> 0).
A number in prose is a declaration, and declarations drift. Seven of seven is not
a series of typos, it is a missing mechanism — so the numbers are measured here
too, in the same command, rather than in a second script that would drift from it.
"""
from __future__ import annotations

import argparse
import collections
import re
import subprocess
import sys
from pathlib import Path

import yaml

KIT = Path(__file__).resolve().parents[1]
AGENZYM = KIT.parent
SPEC_DIR = AGENZYM / "specs" / "046-agentii-research-orchestration"
WORKSPACES = [Path("/Users/frank/B/agentii-space-tech-SPCX"),
              Path("/Users/frank/B/agentii-physical-ai")]

SCAN_FILES = ["spec.md", "plan.md", "quickstart.md", "data-model.md",
              "live-data-provider.md"]

# Named in the spec, rejected by a decision. Absent on purpose — see Q4.
ABSENT_OK = {
    "registry.json": "Q4 — derived over ledger",
    "artifacts.json": "Q4 — derived over ledger",
    "checkpoint.json": "Q4 — the filesystem is the checkpoint",
    "entity-index.json": "Q4 — derived view, no persisted ledger",
    "staged.json": "Q? — staged order is a proposal, never a runtime store",
}

# Command -> the script that would back it, if one is needed.
COMMAND_BACKING = {
    "converge": "converge.py", "challenge": "challenge.py",
    "implement": "dispatch.py", "status": "thesis_status.py",
    "plan": None, "intake": None, "assume": None,
}
# `agentii.ai` is the product DOMAIN, not a command — the `agentii\.([a-z]+)`
# regex cannot tell a verb from a TLD. Excluded rather than reported.
NOT_A_COMMAND = {"ai"}
# `agentii.md` matches the command regex but is a FILE, not a command. NOTE: this
# entry produced a false negative on 2026-09-18 — it was reported MISSING by the
# resolve-a-name-to-a-file rule, which conflates "no instance in these repos" with
# "nothing built". `agentii.md` has a published contract (contracts/agentii-md-schema.md),
# an FR range (FR-087–FR-095) and 4+ skills that write it; only a RUNTIME INSTANCE is
# absent. That is the Q105 distinction, and the same class as the two false positives
# below. Fixed by reporting the distinction rather than the verdict.
RUNTIME_FILES = {
    "agentii.md": ("has a published contract + FR-087–FR-095 + 4 skills writing it; "
                   "no RUNTIME INSTANCE in either workspace (both have constitution.md, "
                   "which supersedes it per Q140)"),
}


# Vendored trees that must never satisfy a spec-046 name. Without this the audit
# "found" constitution.yaml inside a third-party edgartools checkout — a match
# that is worse than no match, because it reports BUILT for a file spec 046 does
# not own. Same class of error as Q124/Q125's false "Clear" marks.
_VENDOR = ("mcp-repos/", "node_modules/", "vendor/", ".venv/", "site-packages/")


def _tracked(repo: Path, prefix: str = "") -> list[str]:
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files"],
                             capture_output=True, text=True, check=True).stdout
        untracked = subprocess.run(
            ["git", "-C", str(repo), "ls-files", "-o", "--exclude-standard"],
            capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return []
    return [prefix + l for l in (out + untracked).splitlines()
            if l.strip() and not any(v in prefix + l for v in _VENDOR)]


def _index() -> dict[str, list[str]]:
    byname: dict[str, list[str]] = collections.defaultdict(list)
    for repo, prefix in ((KIT, "kit/"), (AGENZYM, "agenzym/")):
        for f in _tracked(repo, prefix):
            byname[Path(f).name].append(f)
    for ws in WORKSPACES:
        if not ws.is_dir():
            continue
        for p in ws.rglob("*"):
            if p.is_file() and "/.git/" not in str(p):
                byname[p.name].append(f"ws:{ws.name}/{p.relative_to(ws)}")
    return byname


def _registered_subcommands() -> set[str]:
    """Literal add_parser names PLUS the DELEGATING table's keys.

    The first version matched only literal `sub.add_parser("x")` calls, so when
    Phase 11 registered four commands via a loop over DELEGATING it would have kept
    reporting all four as WIRING-ONLY. Fourth time this session an instrument was
    the broken thing — and this time the fix to the system invalidated the check,
    which is the more dangerous direction: a green report over a real change."""
    src = (KIT / "scripts" / "agentii_cmd.py")
    if not src.is_file():
        return set()
    text = src.read_text(encoding="utf-8")
    names = set(re.findall(r'add_parser\(\s*"([a-z-]+)"', text))
    m = re.search(r"^DELEGATING\s*=\s*\{(.*?)^\}", text, re.S | re.M)
    if m:
        names |= set(re.findall(r'"([a-z-]+)":\s*\(', m.group(1)))
    return names


def _skill_names() -> set[str]:
    skills = KIT / "plugins" / "vertical-plugins" / "scenarios" / "skills" / "agentii"
    return {d.name for d in skills.iterdir() if (d / "SKILL.md").is_file()} \
        if skills.is_dir() else set()


def _q_numbers() -> tuple[set[int], list[int]]:
    """Distinct Q-numbers in spec 046's spec.md, and any gaps in 1..max."""
    text = (SPEC_DIR / "spec.md").read_text(encoding="utf-8")
    nums = {int(n) for n in re.findall(r"\bQ(\d{1,3})\b", text)}
    gaps = [i for i in range(1, max(nums, default=0) + 1) if i not in nums]
    return nums, gaps


def _counts() -> int:
    """Check the spec's asserted quantities against the system.

    The CLAIMS come from `<spec dir>/quantity-claims.yaml`; this function supplies
    only the MEASUREMENTS. That split is deliberate — see the comment at the
    claims-file lookup below. Return code mirrors --strict: 1 if any claim is stale."""
    reg = KIT / "skill-registry.yaml"
    if not reg.is_file():
        print(f"no skill-registry.yaml in {KIT}", file=sys.stderr)
        return 2
    entries = yaml.safe_load(reg.read_text(encoding="utf-8"))["skills"]
    tot = len(entries)
    tpl_dir = KIT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
    tpl = [p for p in tpl_dir.iterdir() if p.is_file() and "template" in p.name] if tpl_dir.is_dir() else []
    kitskills = KIT / "plugins" / "vertical-plugins" / "scenarios" / "skills" / "agentii"
    kit = [d for d in kitskills.iterdir() if (d / "SKILL.md").is_file()] if kitskills.is_dir() else []
    modefiles = list((KIT / "plugins").glob("vertical-plugins/*/skills/agentii/*/references/modes.md"))
    skildirs = list((KIT / "plugins").glob("vertical-plugins/*/skills/agentii/*/"))
    default_only = sum(1 for e in entries if (e.get("modes") or []) == ["default"])
    total_modes = sum(len(e.get("modes") or []) for e in entries)

    # The claims live in the spec dir, NOT in this script. If they were literals
    # here, correcting the prose would not clear the check — and the check would
    # become a stale declaration of its own, i.e. the failure it exists to catch.
    claims_file = SPEC_DIR / "quantity-claims.yaml"
    if not claims_file.is_file():
        print(f"missing {claims_file} — the asserted numbers have no home to be checked against",
              file=sys.stderr)
        return 2
    doc = yaml.safe_load(claims_file.read_text(encoding="utf-8"))
    measured = {
        "registry_count": tot,
        "template_files": len(tpl),
        "kit_skills_disk": len(kit),
        "kit_skills_registry": sum(1 for e in entries if e.get("role") == "kit"),
        "skills_with_modes_md": len(modefiles),
        "skill_dirs": len(skildirs),
        "total_modes": total_modes,
        "default_only_skills": default_only,
        "requires_count": sum(1 for e in entries if e.get("requires")),
        "essentials_modes_count": sum(1 for e in entries if e.get("essentials_modes")),
        # Distinct Q-numbers in the spec. NOT a count of "- **Q{n}:" lines: that
        # regex missed 21 definitions written in other shapes and reported 126 for
        # a real 147, i.e. the MEASURE was wrong while the CLAIM was right. A count
        # of distinct numbers is format-independent, and the gap check below makes
        # "Q1..QN with no holes" explicit rather than assumed.
        "question_count": len(_q_numbers()[0]),
    }
    print(f"spec 046 quantitative claims — {claims_file.name} vs measured\n")
    bad = checked = 0
    for c in doc["claims"]:
        label, claimed = c["label"], c.get("claimed")
        got = measured.get(c["measure"])
        if got is None:
            print(f"  ??   {label:<46} unknown measure {c['measure']!r}", file=sys.stderr)
            return 2
        share = f"  ({got / max(1, tot):.0%} of {tot})" if c.get("as_share") else ""
        if claimed is None:
            print(f"  --   {label:<46} measured {got}{share}  (no claim to check)")
            continue
        checked += 1
        ok = claimed == got
        bad += 0 if ok else 1
        print(f"  {'ok ' if ok else 'XX '} {label:<46} claimed {claimed:<4} measured {got}{share}"
              + ("" if ok else "   <-- STALE"))
    qs, gaps = _q_numbers()
    # Truncate: a failure message that dumps 851 numbers is a message nobody reads.
    detail = "no gaps" if not gaps else (
        f"GAPS {gaps[:8]}" + (f" … +{len(gaps) - 8} more" if len(gaps) > 8 else ""))
    print(f"\n  Q-numbering: Q1–Q{max(qs, default=0)}, {len(qs)} distinct, {detail}")
    print(f"{checked} claims checked, {bad} stale")
    return 1 if (bad or gaps) else 0
    return 1 if bad else 0


def _plan_graph() -> int:
    """Check the plan's phase graph: DAG, no cycles, and SYMMETRIC edges.

    The prerequisite column is hand-maintained prose and so is the ordering
    diagram beside it. Where one names a blocker and the other does not, the
    plan asserts an order it does not record — the same declaration-vs-artifact
    gap as Checks 41 and 42, applied to the plan itself.

    Measured 2026-09-18: three asymmetric edges, one of them in a sentence this
    plan writes explicitly ("Phase 12 blocks Phase 3, and Phase 3 does not know
    it") and then leaves in the table."""
    text = (SPEC_DIR / "plan.md").read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*\*\*(\d+)(?:\s+amend)?\*\*\s*\|([^|]*)\|[^|]*\|[^|]*\|([^|]*)\|",
        text, re.M)
    prereq: dict[int, str] = {}
    for num, _body, cell in rows:
        # 2..6 are the AMENDED Part I phases and sit in the same table; excluding them
        # made the check report "<no row>" for Phase 3 — a phase whose row exists.
        if 2 <= int(num) <= 20:
            prereq[int(num)] = cell.strip()
    if not prereq:
        print("  no Part II phase rows found — did the table shape change?", file=sys.stderr)
        return 2

    # Edges declared in the prerequisite cell: "must land with Phase N", "blocks Phase N",
    # "Phase N amend", bare "N amend", "6 amend + 7".
    # A prereq cell may only name phases it DEPENDS ON. The first version of this
    # check regexed every "Phase N" and so read "detectors are SEPARATE from Phase
    # 13's" as a dependency on 13 — a false positive of exactly the kind this file
    # has already produced twice (the vendored constitution.yaml, spec 016's
    # registry.json). Negation words now suppress the match.
    NEG = ("separate", "independent", "not ", "none", "does not", "unlike")
    edges: list[tuple[int, int, str]] = []
    for num, cell in sorted(prereq.items()):
        for m in re.finditer(r"Phase\s+(\d+)", cell):
            before = cell[max(0, m.start() - 32):m.start()].lower()
            if any(w in before for w in NEG):
                continue
            edges.append((num, int(m.group(1)), cell))
        for m in re.finditer(r"\b(\d+)\s+amend\b", cell):
            edges.append((num, int(m.group(1)), cell))

    print("Part II phase graph — edges declared in the prerequisite column\n")
    problems: list[str] = []
    named: dict[int, set[int]] = {}
    for src, dst, cell in edges:
        if dst not in prereq and dst not in range(0, 7):
            problems.append(f"Phase {src} names Phase {dst}, which has no Part II row")
        named.setdefault(src, set()).add(dst)
        print(f"  {src:>2} <- {dst:<2}  ({cell[:52]})")

    # Symmetry: if A names B as a prerequisite, B must name A as a blocker, or the
    # blocker must be stated somewhere in B's row (§15.3 style prose counts).
    # ONLY edges that a phase's own text states explicitly. An earlier version
    # invented {13: {7, 8}} from "invalidates part of Q81/Q83's acceptance
    # criteria" — a guess about which phases own those Part I decisions, not a
    # measurement. Unverified mappings do not belong in a checker.
    blockers = {
        15: {14},      # §15.3: Phase 14's verification cannot be satisfied before 15
        12: {3},       # Phase 12: "must land with Phase 3, not after"
    }
    declared = {src: sorted(dst) for src, dst in named.items()}
    for blocker, blocked in sorted(blockers.items()):
        for b in sorted(blocked):
            back = f"Phase {blocker}" in prereq.get(b, "") or f"{blocker} amend" in prereq.get(b, "")
            if not back:
                problems.append(
                    f"Phase {blocker} blocks Phase {b}, but Phase {b}'s prerequisite cell "
                    f"does not say so: {prereq.get(b, '<no row>')[:60]!r}")

    # Mutual pairs are CO-REQUIREMENTS ("must land with"), not orderings — they must be
    # separated out before the DAG claim can be true. An earlier version said "DAG, no
    # cycles" in its docstring while only checking symmetry, so the claim was unearned.
    pairs = {(a, b) for a, ds in declared.items() for b in ds if a in declared.get(b, [])}
    mutual = {tuple(sorted(p_)) for p_ in pairs}
    dag = {a: [b for b in ds if tuple(sorted((a, b))) not in mutual]
           for a, ds in declared.items()}

    def _cycles(g: dict[int, list[int]]) -> list[list[int]]:
        seen: list[list[int]] = []
        def walk(n: int, path: list[int]) -> None:
            for nxt in g.get(n, []):
                if nxt in path:
                    seen.append(path[path.index(nxt):] + [nxt])
                elif len(path) < 12:
                    walk(nxt, path + [nxt])
        for start in g:
            walk(start, [start])
        return seen

    cycles = _cycles(dag)
    print("\n  co-requirements (must land together, not ordered):",
          sorted(mutual) or "none")
    print("  ordering DAG:", {k: v for k, v in sorted(dag.items()) if v} or "none")
    if cycles:
        for c in cycles:
            problems.append("cycle in the ordering graph: " + " -> ".join(map(str, c)))

    print("\n  declared prerequisites:", {k: v for k, v in sorted(declared.items())})
    print("  blockers asserted in prose but not in the table:",
          {k: v for k, v in blockers.items()})
    if problems:
        print("\nASYMMETRIC / DANGLING EDGES:", file=sys.stderr)
        for p_ in problems:
            print(f"  - {p_}", file=sys.stderr)
        return 1
    print("\nOK — the phase graph is a DAG with symmetric edges.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(prog="audit_named_artifacts.py")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if any named artifact is MISSING (not merely absent-ok)")
    ap.add_argument("--counts", action="store_true",
                    help="check the spec's numeric claims instead of its named artifacts")
    ap.add_argument("--graph", action="store_true",
                    help="check the plan's phase graph for dangling and asymmetric edges")
    a = ap.parse_args()
    if a.counts:
        return _counts()
    if a.graph:
        return _plan_graph()

    text = "".join((SPEC_DIR / f).read_text(encoding="utf-8")
                   for f in SCAN_FILES if (SPEC_DIR / f).is_file())
    if not text:
        print(f"no spec files found under {SPEC_DIR}", file=sys.stderr)
        return 2

    byname = _index()
    registered = _registered_subcommands()
    skills = _skill_names()
    cmd_src = (KIT / "scripts" / "agentii_cmd.py")
    registered = registered if cmd_src.is_file() else set()

    cands: collections.Counter[str] = collections.Counter()
    for m in re.finditer(r"`([A-Za-z0-9_./-]+\.(?:py|sh|json|yaml|yml|html))`", text):
        cands[m.group(1)] += 1
    for m in re.finditer(r"`agentii\.([a-z]+)`", text):
        cands[f"agentii.{m.group(1)}"] += 1

    buckets: dict[str, list[tuple[int, str, str]]] = {
        "BUILT": [], "WIRING-ONLY": [], "MISSING": [], "ABSENT-OK": []}
    for name in sorted(cands):
        n = cands[name]
        if name in RUNTIME_FILES:
            buckets["MISSING"].append((n, name, RUNTIME_FILES[name]))
        elif name.startswith("agentii."):
            cmd = name.split(".", 1)[1]
            if cmd in NOT_A_COMMAND:
                continue
            backing = COMMAND_BACKING.get(cmd)
            has_script = bool(backing) and (KIT / "scripts" / backing).is_file()
            if cmd in registered:
                buckets["BUILT"].append((n, name, "registered in agentii_cmd.py"))
            elif cmd in skills:
                why = f"skill exists; {backing} exists" if has_script \
                    else "skill exists; no backing script needed"
                buckets["WIRING-ONLY"].append((n, name, why))
            elif has_script:
                buckets["WIRING-ONLY"].append(
                    (n, name, f"{backing} exists; no skill; dispatch entry missing"))
            else:
                buckets["MISSING"].append(
                    (n, name, f"no skill, no {backing or 'script'}"))
        else:
            bare = name.split("/")[-1]
            # ABSENT-OK takes precedence over the file lookup: a name the spec
            # REJECTED stays rejected even when a same-named file exists elsewhere
            # for an unrelated purpose (registry.json exists as spec 016's skill
            # registry — that must not make Q4's rejected registry.json "BUILT").
            if bare in ABSENT_OK:
                buckets["ABSENT-OK"].append((n, name, ABSENT_OK[bare]))
            elif bare in byname:
                buckets["BUILT"].append((n, name, byname[bare][0]))
            else:
                buckets["MISSING"].append((n, name, "not found in kit, agenzym or either workspace"))

    total = sum(len(v) for v in buckets.values())
    print(f"spec 046 named artifacts: {total} distinct\n")
    for label, note in (("BUILT", ""), ("WIRING-ONLY", " <- every part built but the entry point"),
                        ("MISSING", ""), ("ABSENT-OK", " <- absent by decision, NOT a gap")):
        rows = buckets[label]
        print(f"{label}  ({len(rows)}){note}")
        for n, name, why in sorted(rows, key=lambda x: (-x[0], x[1])):
            print(f"  {n:>2}x  {name:<34} {why}")
        print()
    print("counts: " + " · ".join(f"{k} {len(v)}" for k, v in buckets.items()))
    return 1 if (a.strict and buckets["MISSING"]) else 0


if __name__ == "__main__":
    sys.exit(main())
