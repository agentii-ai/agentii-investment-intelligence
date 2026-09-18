"""test_meta_rules.py — spec 046's five meta-rule checks (T143–T146, Checks 38–42).

The spec carries three meta-rules, and all three say one sentence: **a rule must
name the context it assumes.**

    MR-1  axis attribution    — which axis a value belongs to
    MR-2  the location rule   — where a record lives
    MR-3  mode attribution    — which mode a rule governs (+ where it runs)

Q130's own author broke MR-1 five times, and Q142 broke MR-2 in the round that
introduced MR-3. That is the argument for these being **scripts rather than
paragraphs**: the author is not an exception.

Each check reports its own precondition honestly. Check 40 reports `UNTAGGED: N`
until the tagging pass completes; Checks 41 and 42 report `NO INVENTORY` until the
gate inventory carries mode declarations. **An un-run check must say it has not
run** — Q105, applied to the checks themselves.
"""
from __future__ import annotations

import collections
import json
import re
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
    if tagged:
        assert not both_no_host, (
            f"`both` rules with no enforcement point: {both_no_host}. Q142 was the "
            f"worked example: its `both` attribution was correct and had no trigger.")


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
    reports, and gates only once the field declares a `location_base`."""
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

    print(f"\nCheck 42 — `location:` by syntax, {len(items)} items: "
          + ", ".join(f"{k}={v}" for k, v in counts.items())
          + f" (of the no-component ones, {resolved_role} are RESOLVED)")

    if not doc.get("location_base"):
        pytest.skip(
            f"NO CONVENTION — landing-items.yaml declares no `location_base`, so "
            f"`location:` cannot be resolved against a root and Q147 (one component "
            f"vs N) cannot be decided. Syntax counts above are the whole finding. "
            f"Add `location_base:` and a cardinality rule to make this a gate.")


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
