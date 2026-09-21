"""test_skill_propagation.py — the source of truth and its derivative, held true.

spec 058 T037 and T129. Two state assertions over the real tree, both of which were false
at some point on 2026-09-21 and neither of which had a control:

  1. **No shipped file carries the retired port sentinel.** The seven machine-ported
     equity-research-core skills carried `<!-- BEGIN port-dimension-prompts methodology +
     modes -->` in `SKILL.md` and the END twin in `references/modes.md` — 28 marker
     instances across two trees — plus 84 literal `dim` tokens. Their producer,
     `scripts/port-dimension-prompts.py`, is RETIRED (2026-06-13, FR-014c) and its body is
     not valid Python, so nothing consumes them again. `T034` removed them from the
     vertical tree and `T037` propagated.

  2. **The bundle equals its source.** `plugins/agent-plugins/agentii-equity-agent/skills/
     agentii/` is a vendored copy of nine `equity-research-core` skills, and
     `scripts/sync-agent-skills.py`'s own docstring says the vertical copy is the source of
     truth and that generator is how a change travels. Measured 2026-09-21: the trees were
     byte-identical before the repair and diverge the moment one is edited without a
     re-sync — which is exactly what T037 exists to close, and what this test keeps closed.

The third assertion is the one that makes the other two trustworthy: the sentinel's
producer must still be RETIRED. If someone un-retires it, the sentinels become meaningful
again and the rule that forbids them has to be revisited — so the test says so rather than
letting a future reader re-derive it.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
VERTICAL = KIT / "plugins" / "vertical-plugins" / "equity-research-core" / "skills" / "agentii"
BUNDLE = KIT / "plugins" / "agent-plugins" / "agentii-equity-agent" / "skills" / "agentii"
PORT_SCRIPT = KIT / "scripts" / "port-dimension-prompts.py"
NINE = ["business-model", "competitive", "earnings-sentiment", "growth-strategy",
        "recent-quarter", "risk", "secular-trends", "turnaround", "valuation-methods"]


def _digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_no_shipped_file_carries_the_retired_port_sentinel():
    """T129 — the state, over the whole plugin tree, not only the nine.

    Scans both halves of the pair: the BEGIN in `SKILL.md` and the END that travelled into
    `references/modes.md`. A check that scanned only `SKILL.md` would pass a skill whose
    references still carried half of a dead sentinel."""
    offenders = []
    for f in sorted((KIT / "plugins").rglob("*.md")):
        if f.is_symlink():
            continue                       # the meta-plugin's 80 symlinks point at these
        if "port-dimension-prompts" in f.read_text(encoding="utf-8", errors="ignore"):
            offenders.append(str(f.relative_to(KIT)))
    assert not offenders, (
        "shipped file(s) carry the retired port sentinel. Its producer is retired "
        "(FR-014c) and cannot run, so nothing consumes it — a shipped skill must not "
        f"carry it, and re-porting would reintroduce it:\n  " + "\n  ".join(offenders))


def test_the_bundle_is_byte_identical_to_its_source():
    """T037 — `sync-agent-skills.py`'s contract, asserted rather than assumed.

    The generator iterates the directories that are ALREADY bundled and re-copies each from
    its vertical source, so it can refresh a bundle but never grow one. That is why
    "re-running it is safe and will not change the bundle's membership" (T037's note) — and
    why a divergence here means someone edited one side by hand."""
    assert BUNDLE.is_dir(), "the agent-plugin bundle is missing"
    packaged = sorted(d.name for d in BUNDLE.iterdir() if d.is_dir())
    assert packaged == sorted(NINE), (
        f"the bundle's membership changed: {packaged}. It holds the nine "
        f"equity-research-core skills; the manifest's claim of 24 across 4 verticals is "
        f"T037's separate finding and is not asserted here")

    drift = []
    for name in NINE:
        for rel in ("SKILL.md", "references/modes.md", "references/output-structure.md"):
            a, b = VERTICAL / name / rel, BUNDLE / name / rel
            if not (a.is_file() and b.is_file()):
                continue
            if _digest(a) != _digest(b):
                drift.append(f"{name}/{rel}")
    assert not drift, (
        "the bundle differs from the vertical source it is generated from — run "
        f"`python3 scripts/sync-agent-skills.py` (FR-051's rule, one directory over):\n  "
        + "\n  ".join(drift))


def test_the_sentinel_producer_is_still_retired():
    """The premise of both rules above.

    If `port-dimension-prompts.py` were un-retired, its sentinels would mean something
    again, `references/modes.md` would be a port target, and the assertions here would be
    forbidding a live mechanism rather than clearing a dead one. This test is how a future
    reader finds that out without re-deriving the whole chain — the same discipline as
    `test_artifact_contract.py`'s fixture-drift guard."""
    head = PORT_SCRIPT.read_text(encoding="utf-8", errors="ignore")[:400]
    assert "RETIRED" in head, (
        "the port script no longer declares itself retired — the sentinel rules in this "
        "file and Check 53 were written for a retired producer; revisit both")
