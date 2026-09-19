"""test_meta_rules.py — spec 046's meta-rule and gate-integrity checks (Checks 38–49).

The spec carries FOUR meta-rules, and all four say one sentence: **a rule must
name the context it assumes.**

    MR-1  axis attribution    — which axis a value belongs to          (Check 38)
    MR-2  the location rule   — where a record lives                   (Check 39)
    MR-3  mode attribution    — which mode a rule governs, + where it runs
                                                                       (Checks 40–42)
    MR-4  evidence attribution — where the observation behind a decision lives
                                                                       (Check 44)

Q130's own author broke MR-1 five times, Q142 broke MR-2 in the round that
introduced MR-3, and MR-3's own author broke it again in the next round. That is
the argument for these being **scripts rather than paragraphs**: the author is not
an exception.

**The checks that are not meta-rules**, added 2026-09-19 and all the same shape —
*the declaration and the implementation have drifted, and no reader can see it*:

    Check 41  a gate's declared mode must be satisfiable by its inputs
    Check 45  derived counts must actually recompute from the claim list
    Check 46  no reference label may have been emptied (22 were)
    Check 47  the landing index must not silently overwrite its own keys
    Check 48  no `check_*.py` may be reachable from nowhere
    Check 49  the disclaimer's single source must still hold

Each check reports its own precondition honestly. Check 40 reports `UNTAGGED: N`
until the tagging pass completes. **An un-run check must say it has not run** —
Q105, applied to the checks themselves — and where a check can gate, it gates
rather than reporting: Checks 42 and 44 both began as reports and became gates
when the convention they needed was finally declared.

**This docstring said "five meta-rule checks … Checks 38–42" while the file held
eleven.** Left as a note rather than silently corrected: the header of the file
that checks hand-maintained counts is exactly where a hand-maintained count of its
own went stale, which is the whole subject.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

import pytest
import yaml

KIT = Path(__file__).resolve().parents[1]
SPEC = KIT.parent / "specs" / "046-agentii-research-orchestration"
SPEC_MD = SPEC / "spec.md"

SPEC_TEXTS = [SPEC / f for f in
              ("spec.md", "plan.md", "quickstart.md", "data-model.md")]


def _spec_text() -> str:
    return "".join(p.read_text(encoding="utf-8") for p in SPEC_TEXTS if p.is_file())


def _q_blocks() -> list[tuple[int, str]]:
    text = SPEC_MD.read_text(encoding="utf-8")
    out = []
    for b in re.split(r"(?=^- \*\*Q\d+:)", text, flags=re.M):
        m = re.match(r"^- \*\*Q(\d+):", b)
        if m:
            out.append((int(m.group(1)), b))
    return out


# ── Check 38 — MR-1 axis attribution ────────────────────────────────────────

_AXIS_ROW = re.compile(r"^\s*\|\s*\*\*`(\w+)`\*\*\s*\|\s*\*\*(.+?)\*\*", re.M)


def _spec_axis_table() -> dict[str, str]:
    """The spec's own axis table (Q76): axis name → the 语义 it states.

    Scoped to Q76's block. The shape `| **`x`** | **y** |` recurs throughout the
    spec (parameter tables, capability tables), so an unscoped scan picks up
    `converge`, `max_tasks_per_day` and eight other non-axes — which is how the
    first version of this function reported a disagreement that was its own."""
    block = next((b for n, b in _q_blocks() if n == 76), "")
    return {m.group(1): m.group(2) for m in _AXIS_ROW.finditer(block)}


def test_check_38_every_axis_states_the_question_it_answers():
    """A new enum value must name its axis AND the question that axis answers.

    Q76 framed axes as *classifications*; a classification with no stated question
    is a bucket. Measured 2026-09-18: the five axes that PREDATE the rule carried no
    description, while the three added after it all did — which is the rule working
    on new input and never being applied to old.

    The expected wording is READ FROM the spec's Q76 table, not restated here: a
    hand-copied second list would be one more thing to drift."""
    schema = json.loads(
        (SPEC / "contracts" / "taxonomy.schema.json").read_text(encoding="utf-8"))
    axes = schema["properties"]["axes"]["properties"]
    undocumented = [k for k, v in axes.items() if not (v.get("description") or "").strip()]
    assert not undocumented, (
        f"axes with no stated question: {undocumented}. MR-1 requires every axis to "
        f"name what it answers — see the schema's `description` per axis.")

    table = _spec_axis_table()
    assert set(table) == set(axes), (
        f"the spec's Q76 table and the schema disagree on which axes exist: "
        f"table-only={set(table) - set(axes)}, schema-only={set(axes) - set(table)}. "
        f"An axis added in one place and not the other is MR-1's exact failure.")
    for name, stated in table.items():
        assert stated in axes[name]["description"], (
            f"axis `{name}`: the Q76 table says it answers 「{stated}」 but the schema's "
            f"description does not repeat that wording — the two have drifted.")



def test_check_38_no_value_on_two_axes_or_none():
    """Q76's placement rule, across both taxonomy files."""
    for f in (KIT / "contracts" / "taxonomy.yaml",
              KIT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
              / "taxonomy-workspace-template.yaml"):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        seen: dict[str, list[str]] = {}
        for axis, vals in d["axes"].items():
            for v in vals:
                seen.setdefault(v, []).append(axis)
        dup = {v: a for v, a in seen.items() if len(a) > 1}
        assert not dup, f"{f.name}: value(s) on two axes: {dup}"


# ── Check 39 — MR-2 the location rule ───────────────────────────────────────

_RECORD_RULE = re.compile(
    r"(在\s*`?[A-Za-z_./-]+`?\s*(被)?记录处|由\s*`?[A-Za-z_./-]+`?\s*计算"
    r"|checks? where .{0,40} is recorded|computed from `[^`]+`)", re.I)

# A rule's own statement necessarily quotes the phrasing it forbids. Every one of
# the five initial "offenders" was a self-match: spec.md:33 is MR-2's enforcement
# row, 4109/4116/4138 and plan.md:1234 are the rule's text. Same shape as the Q34
# rule-3 false positive that flagged 307 citation URLs — a pattern that matches
# its own definition is not a finding.
_RULE_SELF_STATEMENT = re.compile(r"必须(同时)?点名|必须被附上|must name X's location", re.I)


def test_check_39_record_dependent_rules_name_a_location():
    """MR-2: a rule that depends on a record must name the record's location.

    Unnamed ⇒ incomplete, *because in practice it is a gate that never fires*.
    This scans for the phrasing shape; it cannot judge semantics, so what it can
    honestly assert is that no rule uses the shape without naming a file. The
    rule's own statements are excluded — otherwise the check fails on the text
    that defines it."""
    offenders = []
    for path in SPEC_TEXTS:
        if not path.is_file():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _RULE_SELF_STATEMENT.search(line):
                continue
            if _RECORD_RULE.search(line) and not re.search(
                    r"`[^`]*\.(md|yaml|json|py|ndjson)`", line):
                offenders.append(f"{path.name}:{i}: {line.strip()[:90]}")
    assert not offenders, (
        f"{len(offenders)} rule(s) use MR-2's phrasing without naming a location: "
        f"\n  " + "\n  ".join(offenders[:5]))


# ── Check 40 — MR-3 mode attribution (T144) ─────────────────────────────────

_MODE_TAG = re.compile(r"\*\*适用范围\*\*\s*[:：]?\s*(thesis|single-skill|both)")


def test_check_40_mode_attribution_reports_untagged():
    """MR-3: every normative rule names the mode it governs; `both` also names
    where it runs. Ships reporting UNTAGGED while the tagging pass (T170) is
    outstanding — Q105's discipline applied to this rule's own gate."""
    blocks = _q_blocks()
    tagged = [(n, b) for n, b in blocks if _MODE_TAG.search(b)]
    untagged = [n for n, b in blocks if not _MODE_TAG.search(b)]
    # `both` without an enforcement point is the Q142 defect, caught in the round
    # that introduced MR-3.
    both_no_host = [n for n, b in tagged
                    if re.search(r"\*\*适用范围\*\*[:：]?\s*both", b)
                    and not re.search(r"落点|enforcement point|执行点", b)]
    print(f"\nCheck 40 — mode attribution: {len(tagged)} tagged, "
          f"{len(untagged)} UNTAGGED of {len(blocks)}; "
          f"{len(both_no_host)} `both` without an enforcement point")
    assert isinstance(untagged, list)          # reports; does not fail while untagged
    # `both` without an enforcement point: REPORTED, with each offender named, for
    # the same reason Check 44 reports `UNCITED: N`. These five are not a tagging
    # gap — the other 24 `both` rules were each given a `**执行点**` naming a
    # VERIFIED symbol. These five have no mechanism to name, which is the finding:
    #
    #   Q63  taxonomy placement is a platform-file decision with no gate
    #   Q100 the pack's viewer-link coverage gate was never built
    #   Q106 G1 independence from its own store is a design constraint, unmechanised
    #   Q121 the multi-signal coverage determination has no implementation
    #   Q136 the derivation record's location is MR-4's `evidence:` field, pending
    #
    # A red suite over a known-open item trains people to ignore the suite; the
    # count is the forcing function instead. It becomes an assertion when these
    # five acquire enforcement points.
    if both_no_host:
        print(f"    {len(both_no_host)} `both` rule(s) with NO enforcement point to "
              f"name — the mechanism does not exist yet: {both_no_host}")


# ── Check 41 / 42 — need the gate inventory (T165) ──────────────────────────

def _gate_inventory() -> dict | None:
    f = KIT / "plugins" / "vertical-plugins" / "scenarios" / "templates" / "workflow.yml"
    if not f.is_file():
        return None
    return yaml.safe_load(f.read_text(encoding="utf-8"))


# Where each declared field actually EXISTS, per mode. Q145's finding was that
# the citation gate declared `both` while its input (`claim_class`) lived in one
# mode's schema — a rule that can declare a mode and still have no data there.
# T169 moves `claim_class` into the public core; until it lands, this table says
# the truth and Check 41 reports the citation gate as UNSATISFIABLE in
# single-skill mode. That is the correct answer, not a broken check.
def _declared_fields() -> set[str]:
    """The fields single-skill mode's frontmatter actually declares.

    DERIVED from contracts/output-frontmatter-schema.md's Fields table, not
    hand-listed — a second copy of a field list is one more thing to drift, and
    this check's whole subject is declaration-versus-reality.

    The first version of this was a literal `set()`, which made EVERY `both`
    gate unsatisfiable by construction. That read like Q145's finding but was an
    artifact of the empty input: `body` and `citations` obviously exist in a
    single-skill report. Same defect as the checks this sits beside."""
    f = KIT / "contracts" / "output-frontmatter-schema.md"
    if not f.is_file():
        return set()
    out = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*`([a-z_]+)`\s*\|", line)
        if m:
            out.add(m.group(1))
    # Not frontmatter columns, but the artifact itself always has these.
    return out | {"body", "citations", "word_count", "support"}


_MODE_FIELDS = {
    # Thesis mode's schema is contracts/artifact-frontmatter.schema.json (FR-090
    # pins) plus everything the output schema declares — thesis artifacts are a
    # superset by Q145's design.
    "thesis": {"FIVE_PINS", "claim_class", "key_metrics", "requires",
               "assumptions", "tasks_md", "claims", "thesis_files",
               "mechanism_outcome", "citations", "body", "word_count",
               "support", "citation_count", "ticker", "tickers", "skill", "affix"},
}


def test_check_41_declared_mode_is_satisfiable():
    """A gate's declared mode must be a SUBSET of the modes where its inputs exist.

    Q145: the citation gate was declared mode-independent while its input
    (`claim_class`) existed in only one mode's schema. A self-contradictory rule
    cannot be found by reading — only by comparing declaration to implementation,
    which is what this does."""
    inv = _gate_inventory()
    if inv is None:
        pytest.skip("NO INVENTORY — workflow.yml absent")
    gates = inv.get("machine_gates") or []
    if not gates:
        pytest.skip("NO INVENTORY — workflow.yml declares no `machine_gates`. "
                    "Check 41 cannot run until T165 splits the inventory.")

    unsatisfiable = []
    single = _declared_fields()
    fields = {**_MODE_FIELDS, "single-skill": single}
    for g in gates:
        modes = ["thesis", "single-skill"] if g.get("mode") == "both" else [g.get("mode")]
        reads = set(g.get("reads") or [])
        if not reads:
            unsatisfiable.append((g.get("id"), "declares no `reads:` — presence is not content"))
            continue
        for m in modes:
            missing = reads - fields.get(m, set())
            if missing:
                unsatisfiable.append(
                    (g.get("id"), f"declared `{g.get('mode')}` but reads {sorted(missing)}, "
                                  f"which do not exist in {m} mode"))

    print(f"\nCheck 41 — {len(gates)} machine gates "
          f"[single-skill declares {len(single)} fields], "
          f"({sum(1 for g in gates if g.get('mode') == 'both')} `both`); "
          f"unsatisfiable: {len(unsatisfiable)}")
    for gid, why in unsatisfiable:
        print(f"    {gid}: {why}")

    # NOW A GATE (2026-09-18, after T167–T169). It reported while the fix was
    # open; it asserts now that it is closed, and the transition is the point.
    # History: it first found 2 unsatisfiable `both` gates — `citation-integrity`
    # (needs `claim_class`) and `vacuous-reporting` (needs `mechanism_outcome`) —
    # which is Q145's and Q146's finding, detected mechanically rather than
    # argued. Adding both to the public core took it to 0.
    assert unsatisfiable == [], (
        f"{len(unsatisfiable)} `both` gate(s) declare a mode their inputs do not "
        f"exist in — Q145's defect: a rule can declare `both` and still have no "
        f"data to read. " + "; ".join(f"{g}: {w}" for g, w in unsatisfiable))


def _loc_components(loc: str) -> list[str]:
    """Split a location into the components it names, BY SYNTAX ONLY.

    Splits only on the compound separators the data actually uses (` + `, ` / `,
    `, `, `; `). Splitting on a bare `/` cuts `scripts/g1_gate.py` in two — the
    first version did that and reported 178 of 178 open items unresolvable.

    No existence check, deliberately. Five iterations of this function each
    moved the headline count, because whether a value "resolves" depends on a
    root convention **the file does not declare** — values are written relative
    to four different roots and some are elided (`specs/046-.../spec.md`). A
    stable statement about syntax is worth more than an unstable one about
    existence: the counts below cannot be wrong, and resolution is deferred to
    the convention this check says is missing."""
    loc = re.sub(r"\.\.\.", "", loc)
    return [c.strip() for c in re.split(r"\s\+\s|\s/\s|,\s|;\s", loc) if c.strip()]


def _names_a_path(comp: str) -> bool:
    """Does this component try to name a file? Extension or separator."""
    return bool(re.search(r"\.(py|md|ya?ml|json|jsonl|html|txt|ndjson)$", comp)) or "/" in comp


def test_check_42_a_named_location_is_one_component():
    """Q147 — the rule is right and NOT ENFORCEABLE against this field. Reports it.

    Q147 found three rule families naming "the write boundary": a location with
    four implementations and none of the three gates, so each rule was enforced
    1/N times. The rule it produced — a location named by N rules must be one
    component — presupposes that `location:` denotes a component.

    Measured 2026-09-18 over the 230 landing items, it often does not:

        names one path-shaped component      see printed counts
        names N>1 path-shaped components     ← not a defect, see below
        names no component (a role)          ("artifact boundary gate")

    The N>1 case must not be "fixed": `contracts/taxonomy.yaml +
    taxonomy-workspace-template.yaml` names two files because the change really
    did need both. Naming only one WOULD be Q147's defect — the documentation
    naming one place while reality has two. So the rule cannot be applied
    mechanically in either direction, and this check does not pretend to: it
    reports, and gates only once the field declares a `location_base`.

    ── T199, 2026-09-19: IT NOW GATES. ────────────────────────────────────────

    `location_base:` is declared, and the field was normalised: 43 components
    that were written against an undeclared root (`templates/…`, `synthesize
    SKILL.md`, a bare `dispatch.py`) or elided (`specs/046-.../`) are now real
    paths. The gate it enables is the one MR-2 was always about:

        a `location:` that does not resolve is a DEFECT when the item is marked
        `resolved: true` — and only then.

    The `resolved:`-aware half is not a softening; it is what makes the rule
    correct. Q24 is the case that proves it: the item names
    `status/SKILL.md` and says in its own text "the skill body does not". An
    unresolvable location on an OPEN item is the item telling the truth about
    work not yet done — demanding resolvability there would force a lie or a
    deletion. And a location on a RESOLVED item that resolves to nothing is
    exactly MR-2's failure ("unnamed ⇒ incomplete, **because in practice it is
    a gate that never fires**") in its completed form: a reader follows the
    path and finds nothing, while the index says the work is done.

    It found Q24 on its first run — the item was marked resolved on 2026-09-18
    by a decision that no skill body was needed, while its `location:` still
    named the file that decision said would not exist. A note recorded the
    decision; the field a reader follows did not."""
    idx = SPEC / "landing-items.yaml"
    if not idx.is_file():
        pytest.skip("no landing-items.yaml")
    doc = yaml.safe_load(idx.read_text(encoding="utf-8"))
    items = doc["items"]

    counts = {"one": 0, "many": 0, "no-component": 0}
    resolved_role = 0
    for i in items:
        comps = _loc_components(i.get("location") or "")
        paths = [c for c in comps if _names_a_path(c)]
        if len(paths) == 1:
            counts["one"] += 1
        elif len(paths) > 1:
            counts["many"] += 1
        else:
            counts["no-component"] += 1
            resolved_role += bool(i.get("resolved"))

    # ── the gate ────────────────────────────────────────────────────────────
    base = doc.get("location_base")
    if not base:
        print(f"\nCheck 42 — `location:` by syntax, {len(items)} items: "
              + ", ".join(f"{k}={v}" for k, v in counts.items())
              + f" (of the no-component ones, {resolved_role} are RESOLVED)")
        pytest.skip(
            "NO CONVENTION — landing-items.yaml declares no `location_base`, so "
            "`location:` cannot be resolved against a root and Q147 (one component "
            "vs N) cannot be decided. Add `location_base:` and a cardinality rule "
            "to make this a gate.")

    roots = [(KIT / b).resolve() for b in base]
    unresolved_resolved: list[str] = []   # defects
    unresolved_open: list[str] = []       # legitimate: the file is to be written
    for i in items:
        for c in _loc_components(i.get("location") or ""):
            c = re.split(r"\s+(?:header|\(|schema|this index)", c)[0].strip("`'\"")
            if c.startswith("runtime-workspace/"):
                continue        # a file in whichever workspace runs — not a repo path
            if not re.search(r"\.(py|md|ya?ml|json|jsonl|html|txt|ndjson)$", c):
                continue        # a role, not a file ("artifact boundary gate")
            if any((r / c).exists() for r in roots):
                continue
            (unresolved_resolved if i.get("resolved") else unresolved_open).append(
                f"{i.get('question')}: {c}")
            break               # one representative per item keeps the count legible

    print(f"\nCheck 42 — `location:` {len(items)} items: "
          + ", ".join(f"{k}={v}" for k, v in counts.items())
          + f" | unresolvable: {len(unresolved_resolved)} on RESOLVED items, "
          f"{len(unresolved_open)} on open items (legitimate)")

    assert not unresolved_resolved, (
        f"{len(unresolved_resolved)} landing item(s) are marked `resolved: true` "
        f"while their `location:` resolves to nothing. A reader follows the path and "
        f"finds nothing, while the index says the work is done — MR-2's 'a gate that "
        f"never fires', in its completed form:\n  "
        + "\n  ".join(unresolved_resolved))


# ── Check 44 — MR-4 evidence attribution (T186/T188/T189) ───────────────────

def test_check_44_decisions_name_where_the_observation_lives():
    """MR-4: a decision resting on an observation must name where it lives.

    MR-4 is MR-2's twin, not a restatement. MR-2 governs RECORDS — a rule
    depending on a record must say where the record lives. MR-4 governs
    OBSERVATIONS — a decision resting on an observation must say where it lives.
    A spec can pass MR-1/2/3 on every line and still be unreviewable, because no
    line says how anyone came to believe it.

    Ships reporting `UNCITED: N` until T187 cites the six session histories —
    Q105's discipline applied to this rule's own gate. Three states, matching
    T157's treatment of `requires:`: a citation passes; the literal `inferred`
    is a DECISION (this rests on reasoning, not observation) and passes; an
    ABSENT `evidence:` is "not yet attributed" and is what UNCITED counts."""
    idx = SPEC / "landing-items.yaml"
    if not idx.is_file():
        pytest.skip("no landing-items.yaml")
    doc = yaml.safe_load(idx.read_text(encoding="utf-8"))
    items = doc["items"]

    cited, inferred, absent = [], [], []
    for i in items:
        ev = i.get("evidence")
        if ev is None:
            absent.append(i)
        elif str(ev).strip().lower() == "inferred":
            inferred.append(i)
        else:
            cited.append(i)

    print(f"\nCheck 44 — evidence attribution over {len(items)} landing items: "
          f"cited={len(cited)}, `inferred`={len(inferred)}, UNCITED={len(absent)}")
    by_q = collections.Counter(i.get("question") for i in absent)
    top = ", ".join(f"{q}×{c}" for q, c in by_q.most_common(6))
    print(f"    UNCITED by question (top): {top}")

    assert isinstance(absent, list)      # reports; does not fail while T187 is open
    # The one thing that IS checkable today: a citation must not be empty or
    # self-referential. `evidence: TBD` / `evidence: see spec` are the shapes
    # that make the field present while leaving the decision unattributed —
    # exactly the "presence is not content" failure T157 found in `requires:`.
    vacuous = [i["item"][:60] for i in cited
               if len(str(i["evidence"]).strip()) < 12
               or re.search(r"\b(TBD|TODO|see above|同上|见上文)\b", str(i["evidence"]), re.I)]
    assert not vacuous, (
        f"{len(vacuous)} `evidence:` value(s) are present but attribute nothing: "
        f"{vacuous[:3]}. A placeholder satisfies the schema and not the rule — the "
        f"same defect as an auto-generated `requires: []`.")


def test_check_44_mr4_is_registered_like_its_three_siblings():
    """MR-4 must be registered in the same place as MR-1/2/3, with an
    enforcement point — MR-4's own subject is decisions that name no source, and
    an unregistered meta-rule is one."""
    doc = yaml.safe_load((SPEC / "landing-items.yaml").read_text(encoding="utf-8"))
    rules = {m["id"]: m for m in (doc.get("meta_rules") or [])}
    assert set(rules) >= {"MR-1", "MR-2", "MR-3", "MR-4"}, (
        f"meta-rules registered: {sorted(rules)} — MR-4 is missing")
    for mid, m in rules.items():
        assert m.get("enforcement"), (
            f"{mid} declares no enforcement point. MR-2's own rule: a rule that "
            f"names no place to run is a gate that never fires.")


# ── Check 45 — derived counts must actually be derivable (T196, Q146) ───────

def _recount(claims: list[dict]) -> dict[str, int]:
    """The derivation the contract promises, written once so it is inspectable.

    Deliberately a plain loop over a list — no prose, no regex, no model. That is
    the whole point of Q146: a G1 gate counts claims by reading FIELDS. The moment
    this needs to understand a sentence, the gate has stopped being deterministic.
    """
    out = {"facts_count": 0, "deducted_count": 0, "views_count": 0}
    key = {"FACT": "facts_count", "DEDUCTED": "deducted_count", "VIEW": "views_count"}
    for c in claims:
        out[key[c["claim_class"]]] += 1
    return out


def test_check_45_the_claim_class_is_per_claim_not_per_file():
    """The incoherence T169 shipped, asserted against the schema so it cannot return.

    T169 put `claim_class` on the ARTIFACT — one element of {FACT,DEDUCTED,VIEW} per
    file. Q146 requires the counts to be DERIVED from the classes, and three counts
    are not derivable from one value: a file reading `claim_class: FACT` can only
    yield `facts_count: 1, deducted_count: 0, views_count: 0`, whatever it actually
    contains. The field satisfied the schema and enforced nothing — this spec's own
    defect, committed in the change written to fix it.

    So the assertion is structural: the class is a property of a CLAIM, and no
    file-level scalar by that name exists to be mistaken for the source of truth.
    """
    schema = json.loads((SPEC / "contracts" / "artifact-frontmatter.schema.json")
                        .read_text(encoding="utf-8"))

    for label, props in (("top level", schema["properties"]),
                         ("$defs.publicCore", schema["$defs"]["publicCore"]["properties"])):
        assert "claim_class" not in props, (
            f"{label} still carries a scalar `claim_class`. One value cannot derive "
            f"three counts — the class belongs to each claim.")
        assert "claims" in props, f"{label} has no `claims` list for the class to live on"
        assert "claim_class" in props["claims"]["items"]["required"], (
            f"{label}.claims items must REQUIRE claim_class, or the list is unclassed "
            f"and the counts are underivable again")

    # The thesis layer's numeric subset carries the class too (Q146).
    ec = schema["properties"]["entity_claims"]["items"]
    assert "claim_class" in ec["required"], (
        "entity_claims is the NUMERIC SUBSET of the claims; its entries need a class "
        "for the same reason the general list does")


def test_check_45_counts_recompute_from_the_claims_list():
    """A file whose counts do not match its claims is the defect, and it is decidable.

    Two halves. The first shows the derivation is a real function over a real list
    (so the contract's promise is executable at all). The second is the half that
    matters: a hand-maintained count that disagrees is DETECTED. Without it,
    'derived' is a word in a description — and this spec's record is that a
    declaration of derivation is exactly what stops being true silently.
    """
    claims = [{"claim_class": "FACT"}, {"claim_class": "FACT"},
              {"claim_class": "DEDUCTED"}, {"claim_class": "VIEW"},
              {"claim_class": "VIEW"}, {"claim_class": "VIEW"}]
    assert _recount(claims) == {"facts_count": 2, "deducted_count": 1, "views_count": 3}

    # The failure the check exists for: a plausible hand-written header.
    declared = {"facts_count": 3, "deducted_count": 1, "views_count": 3}
    derived = _recount(claims)
    mismatch = {k: (declared[k], derived[k]) for k in derived if declared[k] != derived[k]}
    assert mismatch == {"facts_count": (3, 2)}, mismatch

    # An unclassed claim is not a claim — it is a claim the gate cannot see.
    with pytest.raises(KeyError):
        _recount([{"claim_class": "FACT"}, {}])


# ── Check 46 — no document may carry a label that resolved to nothing (T197) ─

def _shipped_docs() -> list[Path]:
    """Docs a reader or an agent is expected to follow, excluding history."""
    out: list[Path] = []
    for root in (KIT / "contracts", KIT / "docs", KIT / "plugins",
                 KIT / "managed-agent-cookbooks"):
        if root.is_dir():
            out += [p for p in root.rglob("*.md") if p.is_file()]
    out += [p for p in (KIT / "README.md", KIT / "QUICKSTART.md",
                        KIT / "CHANGELOG.md", KIT / "SKILL.md") if p.is_file()]
    return out


def test_check_46_no_document_carries_an_emptied_reference_label():
    """MEASURED 2026-09-19: 22 cross-reference labels across 7 shipped documents
    had been reduced to `****` by a lossy transform that ate `FR-\\d+` and
    `spec \\d+`.

    The damage is the exact shape this spec keeps finding, one level down from the
    rules it was checking: **the reference survived, its target did not.** Each line
    still read as a well-formed bullet with a description after the colon — so a
    reader skimming the Cross-Reference block saw a list of five references and had
    no signal that all five pointed at nothing. The descriptions were intact and the
    identifiers were gone, which is worse than a broken link: a broken link fails
    loudly, and an empty label reads as content.

    Recovered from git history and restored (T197): the pre-corruption form is in
    the commits that predate it. This check exists so the next lossy pass is caught
    by CI rather than by someone noticing a stray `****`.
    """
    offenders: list[str] = []
    # An emptied label: four or more asterisks standing where a reference belongs.
    # Only a BARE `****` is the defect. A backticked one is someone QUOTING the
    # defect, which is what a correction note and a CHANGELOG entry must be able to
    # do — Check 39 names this class ("a pattern that matches its own definition is
    # not a finding") and this check hit it the first time the CHANGELOG described
    # its own repair. A real emptied label is never inside backticks: it is
    # `- ****: <description>`, generated by a lossy transform, not written by hand.
    bare = re.compile(r"(?<!`)\*\*\*\*(?!`)")
    for p in _shipped_docs():
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if bare.search(line):
                offenders.append(f"{p.relative_to(KIT)}:{n}: {line.strip()[:80]}")

    assert not offenders, (
        "a reference label was emptied — the bullet still reads as a reference and "
        "points at nothing. Recover the target from git history:\n  "
        + "\n  ".join(offenders))


# ── Check 47 — the index is not silently overwriting itself (T198) ───────────

class _NoDuplicateKeys(yaml.SafeLoader):
    """A YAML loader that FAILS on a duplicate mapping key.

    `yaml.safe_load` accepts duplicates and keeps the last — so a file can carry the
    same key three times and parse perfectly. That is the whole reason this check
    exists and has to be a loader rather than a grep: the defect is invisible to both
    the parser and the reader.
    """


def _reject_duplicate_keys(loader, node, deep=False):
    seen = []
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise ValueError(
                f"duplicate key {key!r} at line {key_node.start_mark.line + 1}")
        seen.append(key)
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_NoDuplicateKeys.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _reject_duplicate_keys)


def test_check_47_the_landing_index_has_no_duplicate_keys():
    """MEASURED 2026-09-19: the Q84 entry carried its `evidence:` key FOUR times,
    with an identical value.

    `landing-items.yaml` was reconstructed from a session transcript after a
    `git checkout` destroyed the working copy (the incident is recorded in the file
    itself), and the replay emitted the same block repeatedly. Because YAML keeps the
    last duplicate, **the file parsed cleanly and every count computed from it was
    correct** — so nothing in the existing toolchain could have noticed. Had the four
    copies differed, three would have been discarded without a word, and the surviving
    one would have been whichever the replayer happened to emit last.

    This is MR-4's subject in its purest form: the index is the spec's evidence
    ledger, and a ledger that silently drops entries is worse than one that is short,
    because only the short one is visibly short.
    """
    import io

    path = SPEC / "landing-items.yaml"
    if not path.is_file():
        pytest.skip("no landing-items.yaml")
    try:
        yaml.load(path.read_text(encoding="utf-8"), Loader=_NoDuplicateKeys)
    except ValueError as e:
        pytest.fail(
            f"landing-items.yaml carries a duplicate key — YAML last-wins, so the "
            f"earlier value was discarded silently: {e}")

    # And the declared total must equal what is actually there. The same
    # reconstruction left `totals.items: 217` above 218 real entries.
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    actual = len(doc["items"])
    declared = doc["totals"]["items"]
    assert declared == actual, (
        f"totals.items says {declared}, the file holds {actual}. A count maintained "
        f"by hand beside the thing it counts is what Q134 exists to eliminate. "
        f"(The file's own INCIDENT note makes it a FLOOR while 13 items are still "
        f"missing — a floor is stated as `>N`, not as an exact number that is wrong.)")


# ── Check 48 — no gate script may be an orphan (T200) ───────────────────────

def test_check_48_every_check_script_is_actually_invoked():
    """`check_disclaimer.py` was correct, was named as Q139's enforcement point,
    and was invoked by nothing.

    It appeared in no test module and in no step of `.github/workflows/ci.yml`.
    The spec's header calls this "a declared mechanism that silently returns empty
    success" and counts fourteen instances; this was one **inside the gate
    machinery itself**, which is where it does the most damage — a reader who
    greps for `check_disclaimer`, finds a correct implementation, and concludes the
    disclaimer is enforced.

    So the assertion is not "check_disclaimer runs" — that would fix one instance
    and leave the class. It is: **every `scripts/check_*.py` is reached — by CI, by
    a test, or by another shipped script importing it.** A new orphan fails here on
    the commit that adds it.

    **The first version of this check had a false positive, and the false positive
    is the useful part of the record.** It searched CI and `tests/` only, and
    reported `check_page_overflow.py` and `check_no_baked_harness_strings.py` as
    orphans. Both are in active use — `synthesize_report.py:42` imports the first
    and `check.py:1126` imports the second — because a gate is often a *module*
    that a producer calls inline rather than a script CI shells out to. A check
    written from one example of the defect would have "fixed" two working gates.
    So the search covers imports from every shipped script, not just the two places
    the original defect happened to be visible.
    """
    import ast

    scripts = sorted((KIT / "scripts").glob("check_*.py"))
    assert scripts, "no check_*.py scripts found — the glob is wrong, not the repo"

    # A `run:` step's command, not the whole YAML — a step's `name:` and its
    # comments are prose, and prose that mentions a gate does not run it.
    ci = (KIT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    ci_runs = "\n".join(re.findall(r"^\s*run:\s*(.+)$", ci, re.M))

    def _code(p: Path) -> str:
        """The CALLS a Python file makes — comments and docstrings removed.

        The first version searched raw text and passed for the wrong reason: this
        very docstring names `check_disclaimer.py`, so a mere MENTION satisfied a
        check about INVOCATION. A gate named in a comment is exactly the failure
        mode being hunted, so the search had to stop counting prose.
        """
        try:
            src = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return ""
        if p.suffix == ".sh":
            return "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return src
        out = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                out += [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                out.append(node.module or "")
            elif isinstance(node, ast.Call):
                # subprocess.run([sys.executable, "scripts/check_x.py"]) and friends
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                        out.append(sub.value)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                out.append(node.name)
        return "\n".join(out)

    callers: list[Path] = []
    for d in ("tests", "scripts", "data-tools"):
        callers += sorted((KIT / d).rglob("*.py"))
        callers += sorted((KIT / d).rglob("*.sh"))

    # TWO spellings, because the two invocation forms differ: CI shells out to
    # `check_x.py`, while Python imports `check_x`. Searching only the filename
    # reported `check_no_baked_harness_strings` and `check_page_overflow` as
    # orphans — both are imported by scripts that CI does run. The suffix is the
    # difference between a real finding and two false ones.
    orphans = []
    for s in scripts:
        stem, name = s.stem, s.name
        if name in ci_runs:
            continue
        if any(stem in _code(p) for p in callers if p.resolve() != s.resolve()):
            continue
        orphans.append(name)

    assert not orphans, (
        f"{len(orphans)} gate script(s) are reached by nothing — not CI, not a test, "
        f"not another script. They run nowhere and their findings are never seen. A "
        f"gate that does not run is not a weaker gate — it is an absent one that "
        f"reads as present:\n  " + "\n  ".join(orphans))


# ── Check 49 — the disclaimer's single source holds (T202, Q139) ─────────────

def test_check_49_the_disclaimer_gate_runs_and_passes():
    """`scripts/check_disclaimer.py` asserted here as well as in CI.

    Two reasons, and the second is the one that matters. First, CI can be skipped,
    run on a fork, or fail to install its dependencies — a test runs wherever the
    suite runs. Second, this file is where the OTHER checks live, and a gate that
    exists in the repository but not in the suite is how `check_disclaimer` came to
    be invoked by nothing for as long as it was.

    It asserts the exit code rather than re-implementing the comparison: the script
    already compares the dashboard's footer to the source, inner-to-inner, and
    clause-set aware. A second implementation would be one more thing to drift —
    Check 48's own lesson, applied.
    """
    import subprocess
    script = KIT / "scripts" / "check_disclaimer.py"
    assert script.is_file(), "the disclaimer gate is missing"
    res = subprocess.run([sys.executable, str(script)],
                         capture_output=True, text=True, cwd=str(KIT))
    assert res.returncode == 0, (
        f"check_disclaimer.py exited {res.returncode}.\n"
        f"stdout:\n{res.stdout}\nstderr:\n{res.stderr}")
    # And it must still be REPORTING coverage, not passing by finding nothing.
    assert "placement-table coverage" in res.stdout, res.stdout
    assert "thesis-report.html" in res.stdout
