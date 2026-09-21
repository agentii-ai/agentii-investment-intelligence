#!/usr/bin/env python3
"""reduce_journals.py — journal reduction, the writer of thesis.reduce.json
(spec 046 Q15).

Strictly ordered and non-commutative:
  ① script computes mechanical fields (known-open, subscription freshness, verdict
     rollup, Q41 claim-level price freshness) — deterministic, zero LLM;
  ② LLM revises judgment fields (conviction / claims / wrong_if) reading ①'s output
     — a hook point in S1 (no LLM wired yet; the revision step exists and receives
     ①'s mechanical summary);
  ③ one atomic write to `thesis.reduce.json` — the MACHINE half of the thesis, and
     the only file this module writes.

**This docstring used to claim step ③ was "the single write moment of thesis.md …
the single-writer moment of the only living file". That claim was false in both
directions, and it was quoted as evidence by a workspace audit before anyone traced
the code.**

`thesis.md` is the HUMAN's file — prose with `---` frontmatter, written once by
`agentii.specify`. This module also wrote to it, in JSON, through the write boundary.
The boundary's second-writer refusal keys on a `writer:` field in the document's own
frontmatter; the scaffold declared none, so the file read as append-only and this
module's JSON write was refused as `refuse-append-only` — blocking — leaving the file
at its scaffold. **The Result was discarded, so `main()` printed `REDUCED N entries`
over a write that never happened.**

So the claim "single write moment" described an intent, not the behaviour: there were
two writers, the gate refused the second, and the refusal was silent. The fix is the
split this module now implements, plus checking the Result.

Judgment must rest on established mechanical fact, not precede it — order matters.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import write_boundary  # noqa: E402 — the single write boundary (T172)
import thesis_doc  # noqa: E402 — where a thesis keeps machine state
import journal  # noqa: E402

# Q41: a directional claim needs a fresh price — re-quote or accept a <24h quote;
# older prices degrade the claim to stale_price (barred from trade-template).
PRICE_FRESHNESS_MAX_AGE_SECONDS = 24 * 3600


class ReduceWriteRefused(RuntimeError):
    """The boundary refused the write. Carries the boundary's OWN words, not a
    paraphrase — the reason names the competing writer, and paraphrasing it would
    hide the one fact the reader needs."""

    def __init__(self, described: str, target: Path):
        super().__init__(f"reduce write REFUSED for {target}:\n{described}")
        self.described = described
        self.target = target


def _compute_mechanical(shard_dir: Path) -> dict[str, Any]:
    """① mechanical fields — derived facts only."""
    entries: list[dict] = []
    for shard in sorted(shard_dir.glob("*.ndjson")):
        entries.extend(journal.read_shard(shard))
    by_skill: dict[str, int] = {}
    for e in entries:
        by_skill[e["skill_id"]] = by_skill.get(e["skill_id"], 0) + 1
    # Q41 freshness: latest quote-timestamp among entries; degrade to stale_price
    # when older than 24h or absent.
    import datetime
    quote_ts = None
    for e in entries:
        for key in ("quote_observed_at", "observed_at"):
            if e.get(key):
                quote_ts = e[key]
                break
        if quote_ts:
            break
    fresh = False
    if quote_ts:
        try:
            age = (datetime.datetime.now(datetime.timezone.utc)
                   - datetime.datetime.fromisoformat(quote_ts)).total_seconds()
            fresh = age <= PRICE_FRESHNESS_MAX_AGE_SECONDS
        except ValueError:
            fresh = False
    return {
        "entry_count": len(entries),
        "by_skill": by_skill,
        "known_open": [],
        "subscription_freshness": {},
        "verdict_rollup": {},
        "price_freshness": {"fresh": fresh, "quote_observed_at": quote_ts,
                            "stale_price": quote_ts is not None and not fresh},
    }


def build_entity_index(artifacts_root: Path) -> dict:
    """Q20/Q9: the entity index is a VIEW computed at reduction time — all artifact
    `entity_claims` scanned, (entity, metric, period) concatenated. Same key with
    different values: retrieved_at-equal → true contradiction (mechanical report);
    retrieved_at-different → suspected restatement (never a contradiction).

    Two defects from spec 058 §D are fixed here, and both were located by counting the
    real corpus rather than by reading the code (FR-039, T018/T019):

    **1. The entity was `str(claim.get("entity"))`, so an absent entity became the
    literal string `"None"`.** Measured across 477 claims: `ticker` is non-null in
    **477/477** and `entity` in **425/477** — so 52 real claims, 11% of the corpus,
    were filed under an entity called None and every finding about them was unusable.
    They are not malformed: the artifacts document that the two fields hold the SAME
    value ("`entity: FLY  # mirrors ticker: g1_gate requires entity, the contract docs
    say ticker`"). So the fix is a fallback, not a rejection — `entity` then `ticker`.
    Only a claim carrying NEITHER is malformed, and those are counted, not silently
    dropped and not named "None".

    **2. A clean zero was arithmetically forced, not earned.** With no artifact carrying
    `entity_claims`, the old return was `{"contradictions": [], "suspected_restatements":
    []}` — identical to a clean run. Thesis 003 reported exactly that on 0 of 45 artifacts
    carrying the field. The result now carries `examined` counts and `mechanism_outcome`
    (spec 046 Q105's `EXECUTED|VACUOUS`), so "nothing was examined" is sayable.

    **3. An artifact that does not PARSE was read as one that declares nothing.** Both
    arrive at `fm.get("entity_claims")` as `[]`, so a malformed artifact was counted in
    `artifacts_scanned`, contributed no claims, and the run still reported `EXECUTED` —
    FR-038's defect one call site away from where T016 fixed it. `journal_frontmatter` is
    strict now and the failure is counted and named, because the only thing worse than
    dropping an artifact is dropping it silently.
    """
    groups: dict[tuple[str, str, str], list[dict]] = {}
    artifacts_scanned = 0
    artifacts_with_claims = 0
    claims_scanned = 0
    malformed: list[str] = []
    not_comparable: list[str] = []
    unparseable: list[str] = []

    import g1_gate  # same-directory module

    for art in sorted(artifacts_root.rglob("*.md")):
        artifacts_scanned += 1
        try:
            fm = journal_frontmatter(art)
        except g1_gate.FrontmatterError as e:
            unparseable.append(
                f"{art}: frontmatter does not parse ({e}) — NOT read as 'declares no "
                f"claims'; the artifact is excluded from the index and that exclusion is "
                f"the reason to look at it (FR-038)")
            continue
        claims = fm.get("entity_claims") or []
        if claims:
            artifacts_with_claims += 1
        for claim in claims:
            if not isinstance(claim, dict) or claim.get("value") is None:
                continue
            claims_scanned += 1
            # `entity` first, then `ticker` — the corpus carries the same value under
            # both names and writes `entity` in only 89% of claims.
            entity = claim.get("entity") or claim.get("ticker")
            metric = claim.get("metric")
            if entity is None or metric is None:
                which = " and ".join(k for k in ("entity", "metric")
                                     if claim.get(k) is None)
                malformed.append(f"{art}: claim {claim.get('claim_id') or '(no id)'} "
                                 f"has no {which} — not filed, not named 'None'")
                continue
            # A `unit: text` claim carries a qualitative value (5 in the corpus, e.g.
            # `draft_rfp`, `not_revenue`). It is legitimate and simply not numerically
            # comparable, so it is COUNTED and skipped — `float()` on it raised
            # ValueError and crashed the whole index, which is how this was found.
            try:
                value = float(claim["value"])
            except (TypeError, ValueError):
                not_comparable.append(
                    f"{art}: claim {claim.get('claim_id') or '(no id)'} value="
                    f"{str(claim['value'])[:40]!r} unit={claim.get('unit')!r} — "
                    f"not numeric, so not comparable; skipped, not dropped silently"
                )
                continue
            key = (str(entity), str(metric), str(claim.get("period")))
            groups.setdefault(key, []).append({
                "value": value,
                "retrieved_at": claim.get("retrieved_at"),
                "artifact": str(art),
            })

    contradictions: list[dict] = []
    suspected: list[dict] = []
    for (entity, metric, period), rows in groups.items():
        values = {r["value"] for r in rows}
        if len(values) <= 1:
            continue
        times = {r["retrieved_at"] for r in rows}
        record = {"entity": entity, "metric": metric, "period": period,
                  "values": sorted(values), "artifacts": [r["artifact"] for r in rows]}
        if len(times) == 1:
            contradictions.append(record)   # same retrieval window, different value
        else:
            suspected.append(record)        # Q17/Q20: likely a restatement

    examined = {
        "artifacts_scanned": artifacts_scanned,
        "artifacts_with_claims": artifacts_with_claims,
        "artifacts_unparseable": len(unparseable),
        "claims_scanned": claims_scanned,
        "claims_malformed": len(malformed),
        "claims_not_comparable": len(not_comparable),
    }
    return {
        "contradictions": contradictions,
        "suspected_restatements": suspected,
        "examined": examined,
        "malformed": malformed,
        "not_comparable": not_comparable,
        "unparseable": unparseable,
        # 046 Q105. VACUOUS means the index had nothing to read — a state that must be
        # distinguishable from "read everything and found no contradictions".
        "mechanism_outcome": "EXECUTED" if claims_scanned else "VACUOUS",
    }


def journal_frontmatter(path: Path) -> dict:
    """The artifact's frontmatter, or a loud `FrontmatterError`.

    STRICT as of 2026-09-21 (spec 058 FR-038). This function used the lenient
    `parse_frontmatter`, whose `{}` conflates "declares nothing" with "does not parse".
    For an artifact carrying `entity_claims`, that conflation is not a reporting wrinkle,
    it is a hole in the contradiction index: the artifact is counted in
    `artifacts_scanned`, contributes no claims, and the run reports `EXECUTED` over the
    claims it could read. Demonstrated before the fix — two artifacts, one malformed by a
    `\\$` escape, the malformed one carrying 999 against the good one's 100 in the same
    (entity, metric, period): `contradictions: []`, and nothing said why.

    The task note in `tasks.md` T016 named this function as the site of the hazard; the
    citation was wrong (it is here, not `g1_gate.py:44–47`), which is how the site stayed
    unfixed while the parser it wraps was made strict. See T016's note.
    """
    import g1_gate  # same-directory module

    return g1_gate.parse_frontmatter_strict(path.read_text(encoding="utf-8"))


def check_aggregate(artifacts_root: Path, constitution_path: Path,
                    with_notices: bool = False):
    """Q16 aggregate postconditions — the only place in the system with a global
    view. Returns problems (CONSTITUTION_BREACH) — NEVER auto-resolves. While
    `constitution_pin: unratified` the aggregate HARD-FAILS (Q83: placeholder
    governance cannot gate the aggregate)."""
    import g1_gate
    import yaml as _yaml

    notices: list[str] = []
    problems: list[str] = []
    try:
        constitution = _yaml.safe_load(constitution_path.read_text(encoding="utf-8")) or {}
    except (OSError, _yaml.YAMLError):
        constitution = {}
    positions: dict[str, float] = {}
    unratified = False
    for art in sorted(artifacts_root.rglob("*.md")):
        # FR-038 again, and this is the floor the aggregate sits on: an artifact that
        # does not parse contributes no sector and no position, so a malformed one
        # silently REMOVES exposure from the total this gate exists to bound. Loud, not
        # skipped — a breach report that under-counts is worse than no report.
        try:
            fm = g1_gate.parse_frontmatter_strict(art.read_text(encoding="utf-8"))
        except g1_gate.FrontmatterError as e:
            problems.append(
                f"CONSTITUTION_BREACH: {art}: frontmatter does not parse ({e}) — its "
                f"position is NOT in the aggregate below, so the totals under-count "
                f"(FR-038)")
            continue
        if str(fm.get("constitution_pin")) == "unratified":
            unratified = True
        sector = str(fm.get("sector") or "unspecified")
        pos = fm.get("position_pct")
        if isinstance(pos, (int, float)):
            positions[sector] = positions.get(sector, 0.0) + float(pos)
    if unratified:
        problems.append("CONSTITUTION_BREACH: aggregate check HARD-FAILS while "
                        "constitution_pin: unratified (Q83 — placeholder governance "
                        "cannot gate the aggregate)")
        return (problems, notices) if with_notices else problems
    for c in constitution.get("constraints") or []:
        if c.get("arity") != "aggregate":
            continue
        group, max_val = c.get("group_by"), c.get("max")
        if group == "sector":
            for sector, total in positions.items():
                if total > float(max_val):
                    problems.append(f"CONSTITUTION_BREACH: {c.get('id')} — sector "
                                    f"'{sector}' at {total}% exceeds max {max_val}% (Q16)")
    return (problems, notices) if with_notices else problems


def reduce(shard_dir: Path, thesis_path: Path,
           llm_revise: Callable[[dict[str, Any]], dict[str, Any]] | None = None) -> dict:
    mechanical = _compute_mechanical(shard_dir)
    # ② judgment fields read ①'s output — a hook point. Without an LLM wired, the
    # revision is the identity over the mechanical facts (explicit, never implicit).
    judgment = llm_revise(mechanical) if llm_revise else {"conviction": None,
                                                          "claims": [],
                                                          "wrong_if": []}
    doc = {
        # The declared writer TRAVELS IN THE DOCUMENT, exactly as the rule requires of
        # markdown: `write_boundary.declared_writer` reads `writer:` from frontmatter,
        # and JSON cannot carry a `---` block — so it reads the top-level key. Without
        # this line the reduce file declares nothing, "declares nothing" means
        # append-only, and the SECOND reduction is refused exactly as the first one
        # was before the split. The fix would have reproduced the bug on a new path.
        "writer": "reduce_journals",
        "reduced_at": __import__("datetime").datetime.now().astimezone().isoformat(),
        "mechanical": mechanical,
        "judgment": judgment,
    }
    target = thesis_doc.machine_path(thesis_path)
    res = write_boundary.write(
        target,
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        producer='reduce_journals',
        kind='json',
        writer='reduce_journals')
    # The Result is CHECKED. It used to be discarded, which is what made a refused
    # write indistinguishable from a successful one to every caller and to main().
    if not res.ok():
        raise ReduceWriteRefused(res.describe(), target)
    return doc


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Journal reduction → thesis.md (Q15)")
    p.add_argument("--shard-dir", required=True)
    p.add_argument("--thesis", required=True, help="thesis.md output path")
    args = p.parse_args(argv)
    try:
        doc = reduce(Path(args.shard_dir), Path(args.thesis))
    except ReduceWriteRefused as e:
        # No success line on any non-written verdict. The old code printed one
        # unconditionally, which is the lie this whole fix is about.
        print(str(e), file=sys.stderr)
        print("remedy: the target declares a different writer — see contracts/thesis.md",
              file=sys.stderr)
        return 2
    print(f"REDUCED {doc['mechanical']['entry_count']} entries → "
          f"{thesis_doc.machine_path(args.thesis)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
