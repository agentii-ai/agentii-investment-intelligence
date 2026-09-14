#!/usr/bin/env python3
"""g1_gate.py — deterministic artifact gate (spec 046 Q1/Q8).

S1-minimal rule set: the five pins present (assumption/corpus/as_of/constitution/skill)
+ `mode` + `data_class`. Millisecond-scale, zero LLM — it runs at every dispatch.
The full rule set (value plausibility, corpus framing, anti-anchoring, lookahead,
constitution postconditions, sector-native coverage, data-quality blocking) lands
with S3 (tasks T037/T038).

Exit codes: 0 = pass, 1 = fail, 2 = usage error.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml", file=sys.stderr)
    sys.exit(2)

FIVE_PINS = ("assumption_pin", "corpus_version", "as_of",
             "constitution_pin", "skill_pin")


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    try:
        _, fm, _ = text.split("---", 2)
        return yaml.safe_load(fm) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def check_frontmatter(fm: dict) -> list[str]:
    """Deterministic checks. Returns a list of problems (empty = pass)."""
    problems: list[str] = []
    for pin in FIVE_PINS:
        if not fm.get(pin):
            problems.append(f"missing pin: {pin}")
    if not fm.get("mode"):
        problems.append("missing field: mode")
    if not fm.get("data_class"):
        problems.append("missing field: data_class")
    return problems


def check_artifact(path: Path) -> list[str]:
    return check_frontmatter(parse_frontmatter(path.read_text(encoding="utf-8")))


# =============================================================================
# Full rule set (S3, Q1/Q7/Q16/Q17/Q19/Q21/Q45/Q52/Q73/Q78/Q83)
# =============================================================================

import datetime as _dt  # noqa: E402
import re as _re  # noqa: E402

_REF_OPEN = _re.compile(r"<ref:([a-z_]+)(?:\s[^>]*)?>")
_REF_CLOSE = _re.compile(r"</ref:([a-z_]+)>")
_CITATION_RE = _re.compile(r"/v/[A-Z0-9]+/[A-Za-z0-9_-]+/(?:page\d+)?")
_PERIOD_RE = _re.compile(r"^(\d{4})Q([1-4])$")
_NATIVE_MED = {"fda-catalyst-analysis", "pipeline-analysis", "trial-readout-analysis"}
_STRONG_MED = {"med.medicines_biotech", "med.medical_devices"}


def _quarter_end(period: str) -> _dt.date | None:
    m = _PERIOD_RE.match(period or "")
    if not m:
        return None
    year, q = int(m.group(1)), int(m.group(2))
    last_month = q * 3
    last_day = {3: 31, 6: 30, 9: 30, 12: 31}[last_month]
    return _dt.date(year, last_month, last_day)


def _check_corpus_framing(text: str, fm: dict) -> list[str]:
    problems: list[str] = []
    opens = [(m.group(1), m.start(), m.end()) for m in _REF_OPEN.finditer(text)]
    closes = [(m.group(1), m.start()) for m in _REF_CLOSE.finditer(text)]
    # Q19 rule 1: closed tags must match opens (truncated generation is detectable)
    stack: list[tuple[str, int]] = []
    events = sorted([(pos, "open", name, None) for name, pos, _ in opens] +
                    [(pos, "close", name, None) for name, pos in closes])
    for pos, kind, name, _ in events:
        if kind == "open":
            stack.append((name, pos))
        else:
            if not stack:
                problems.append("UNFRAMED_REFERENCE: closing </ref:%s> without opening" % name)
            elif stack[-1][0] != name:
                problems.append(f"UNFRAMED_REFERENCE: </ref:{name}> does not close "
                                f"<ref:{stack[-1][0]}> (Q19 same-name rule)")
                stack.pop()
            else:
                stack.pop()
    for name, _pos in stack:
        problems.append(f"UNFRAMED_REFERENCE: unclosed <ref:{name}> block (Q19 rule 1)")
    # Q7: every <ref:strategy> must have a method_selection verdict entry.
    strategy_ids = [m.group(1) for m in
                    _re.finditer(r'<ref:strategy[^>]*\bid="([^"]+)"', text)]
    selections = [s.get("ref") for s in (fm.get("method_selection") or [])
                  if isinstance(s, dict)]
    for sid in strategy_ids:
        if sid not in selections:
            problems.append(f"UNFRAMED_REFERENCE: <ref:strategy id={sid}> has no "
                            f"method_selection verdict (Q7)")
    # Q7/Q19: technical_setup block text must not appear in citation lines.
    for m in _re.finditer(r"<ref:technical_setup[^>]*>(.*?)</ref:technical_setup>",
                          text, flags=_re.DOTALL):
        block_tokens = {w.lower() for w in _re.findall(r"[a-z]{5,}", m.group(1))}
        for line in text.splitlines():
            if _CITATION_RE.search(line):
                line_tokens = {w.lower() for w in _re.findall(r"[a-z]{5,}", line)}
                shared = block_tokens & line_tokens
                if shared:
                    problems.append("UNFRAMED_REFERENCE: technical_setup content appears "
                                    f"in a citation line ({sorted(shared)[:3]}) — setups "
                                    f"never enter citation slots (Q7/Q19)")
                    break
    return problems


def _check_lookahead(fm: dict) -> list[str]:
    problems: list[str] = []
    as_of = str(fm.get("as_of") or "")
    try:
        as_of_date = _dt.date.fromisoformat(as_of)
    except ValueError:
        return problems  # as_of unparseable → pins check already flags it
    for claim in fm.get("entity_claims") or []:
        if not isinstance(claim, dict):
            continue
        q_end = _quarter_end(str(claim.get("period") or ""))
        if q_end and q_end > as_of_date:
            problems.append(f"LOOKAHEAD_VIOLATION: claim {claim.get('entity')}."
                            f"{claim.get('metric')} period {claim.get('period')} ends after "
                            f"as_of {as_of} (Q17)")
    return problems


def _check_scalar_postcondition(fm: dict, constitution: dict,
                                notices: list[str]) -> list[str]:
    problems: list[str] = []
    pin = str(fm.get("constitution_pin") or "")
    if pin == "unratified":
        notices.append("constitution scalar postcondition skipped — "
                       "constitution_pin: unratified (Q83 graceful skip)")
        return problems
    for c in constitution.get("constraints") or []:
        if c.get("arity") != "scalar":
            continue
        field, max_val = c.get("field"), c.get("max")
        value = fm.get(field)
        if value is None or not isinstance(max_val, (int, float)):
            continue
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                continue
        if value > max_val:
            problems.append(f"CONSTITUTION_BREACH: {field}={value} exceeds "
                            f"{c.get('id')} max {max_val} (Q16 scalar postcondition)")
    return problems


def _check_value_plausibility(fm: dict, rules: list[dict],
                              notices: list[str]) -> list[str]:
    problems: list[str] = []
    claims: dict[str, list[float]] = {}
    for c in fm.get("entity_claims") or []:
        if isinstance(c, dict) and isinstance(c.get("value"), (int, float)):
            claims.setdefault(str(c.get("metric")), []).append(float(c["value"]))
    for rule in rules or []:
        op = rule.get("op")
        if op in ("between", "lt", "gt"):
            # Rule semantics: the op states the violation condition directly.
            args = rule.get("args") or []
            metrics = rule.get("metric")
            metrics = metrics if isinstance(metrics, list) else [metrics]
            for metric in metrics:
                for value in claims.get(str(metric), []):
                    bad = {"between": not (args[0] <= value <= args[1]),
                           "lt": value < args[0],
                           "gt": value > args[0],
                           }[op]
                    if bad:
                        _emit_plausibility(rule, metric, value, problems, notices)
        elif op in ("lt_ref", "gt_ref", "ratio_gt"):
            ref = str(rule.get("ref_metric") or "")
            if ref not in claims:
                continue  # cannot evaluate without the reference claim
            for value in claims.get(str(rule.get("metric")), []):
                ref_val = claims[ref][0]
                bad = {"lt_ref": value >= ref_val,
                       "gt_ref": value <= ref_val,
                       "ratio_gt": abs(value / ref_val if ref_val else 0) <= rule.get("args", [0])[0],
                       }[op]
                if bad:
                    _emit_plausibility(rule, rule.get("metric"), value, problems, notices)
        elif op == "sum_equals":
            prefix, total = str(rule.get("sum_metric_prefix")), str(rule.get("total_metric"))
            parts = [v for k, vs in claims.items() if k.startswith(prefix) for v in vs]
            totals = claims.get(total, [])
            if parts and totals and abs(sum(parts) - totals[0]) > 1e-6:
                _emit_plausibility(rule, f"{prefix}→{total}",
                                   abs(sum(parts) - totals[0]), problems, notices)
    return problems


def _emit_plausibility(rule: dict, metric, value, problems: list[str], notices: list[str]) -> None:
    msg = (f"VALUE_IMPLAUSIBLE: {rule.get('id')} — {metric}={value} violates "
           f"op {rule.get('op')} (Q21)")
    if rule.get("level") == "warn":
        notices.append("warn: " + msg)
    else:
        problems.append(msg)


def _check_blind_estimate(fm: dict) -> list[str]:
    problems: list[str] = []
    blind = fm.get("blind_estimate")
    if not isinstance(blind, dict) or not blind.get("written_at"):
        return problems
    retrieved = [str(c.get("retrieved_at")) for c in (fm.get("entity_claims") or [])
                 if isinstance(c, dict) and c.get("retrieved_at")]
    if not retrieved:
        return problems
    try:
        written = _dt.datetime.fromisoformat(str(blind["written_at"]))
    except ValueError:
        return problems
    for r in retrieved:
        try:
            fetched = _dt.datetime.fromisoformat(r)
        except ValueError:
            continue
        if written > fetched:
            problems.append("ANTI_ANCHORING_VIOLATION: blind_estimate.written_at "
                            f"({blind['written_at']}) is after quote retrieved_at ({r}) "
                            f"— the estimate was anchored (Q73)")
            break
    return problems


def check_market_data_allowlist(stage: str, allowed_tools: list[str]) -> list[str]:
    """Q45 override-consistency check: `early` MUST include get_price_history;
    `late` MUST include get_realtime_quote and NOT get_price_history. An `early`
    skill whose allowlist lacks history (or a `late` skill carrying it) is an
    illegal state — deterministic, never left to the agent."""
    tools = set(allowed_tools or [])
    if stage == "early" and "get_price_history" not in tools:
        return ["MARKET_DATA_ALLOWLIST: early-stage skill must include "
                "get_price_history in allowed_tools (Q45)"]
    if stage == "late":
        problems = []
        if "get_realtime_quote" not in tools:
            problems.append("MARKET_DATA_ALLOWLIST: late-stage skill must include "
                            "get_realtime_quote in allowed_tools (Q45)")
        if "get_price_history" in tools:
            problems.append("MARKET_DATA_ALLOWLIST: late-stage skill must NOT include "
                            "get_price_history (Q42 — early-only tool)")
        return problems
    return []


def check_sector_native(sector_path: str, matrix_skills: list[str]) -> list[str]:
    """Q52: med strong-authorization industries MUST include ≥1 bio-pharm native
    skill in the deployment matrix. Weak industries have no requirement."""
    if sector_path not in _STRONG_MED:
        return []
    if not (set(matrix_skills) & _NATIVE_MED):
        return [f"SECTOR_NATIVE_MISSING: thesis sector {sector_path} MUST include "
                f"≥1 of {sorted(_NATIVE_MED)} in the deployment matrix (Q52)"]
    return []


def check_artifact_full(path: Path, *, constitution_path: Path | None = None,
                        value_checks_path: Path | None = None,
                        with_notices: bool = False):
    """The complete G1 rule set. Returns (problems, notices) when with_notices,
    else the problems list (S1 callers' shape preserved)."""
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    notices: list[str] = []
    problems = check_frontmatter(fm)
    problems += _check_corpus_framing(text, fm)
    problems += _check_lookahead(fm)
    problems += _check_blind_estimate(fm)
    for flag in fm.get("data_quality_flags") or []:
        if isinstance(flag, dict) and flag.get("severity") == "blocking":
            problems.append(f"DATA_QUALITY_BLOCKING: {flag.get('source')}.{flag.get('metric')} "
                            f"carries a blocking flag (Q78) — artifact must not deliver")
    # D75 #6 (T-001 first-run feedback): entity_claims must be STRUCTURED — prose
    # strings defeat the entity index, the contradiction detector and the
    # value-plausibility gate (the Q20 field is the whole control plane's input).
    claims = fm.get("entity_claims")
    if claims is not None:
        if not isinstance(claims, list):
            problems.append("SCHEMA_MISMATCH: entity_claims must be a list (Q20)")
        else:
            for i, c in enumerate(claims):
                if not isinstance(c, dict):
                    problems.append(f"SCHEMA_MISMATCH: entity_claims[{i}] is prose, "
                                    f"not the structured {{entity, metric, value, unit, "
                                    f"period, source, retrieved_at}} form (Q20)")
                elif not (c.get("entity") and c.get("metric")
                          and isinstance(c.get("value"), (int, float))):
                    problems.append(f"SCHEMA_MISMATCH: entity_claims[{i}] missing "
                                    f"entity/metric/value (Q20)")
    if constitution_path and constitution_path.is_file():
        try:
            constitution = yaml.safe_load(constitution_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            constitution = {}
        problems += _check_scalar_postcondition(fm, constitution, notices)
    if value_checks_path and value_checks_path.is_file():
        try:
            vc = yaml.safe_load(value_checks_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            vc = {}
        problems += _check_value_plausibility(fm, vc.get("rules") or [], notices)
    return (problems, notices) if with_notices else problems


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="G1 deterministic gate (S1-minimal)")
    p.add_argument("--artifact", required=True, help="artifact .md file to check")
    args = p.parse_args(argv)

    path = Path(args.artifact)
    if not path.is_file():
        print(f"G1 FAIL — artifact not found: {path}", file=sys.stderr)
        return 1
    problems = check_artifact(path)
    if problems:
        print(f"G1 FAIL — {path}:", file=sys.stderr)
        for pr in problems:
            print(f"  ✗ {pr}", file=sys.stderr)
        return 1
    print(f"G1 PASS — {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
