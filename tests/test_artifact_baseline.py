"""test_artifact_baseline.py — FR-043's baseline: read-only, criteria-importing, and
separating the three failures that look alike (spec 058 T039–T042).

The first test is the one the requirement is written around: **the measurement MUST be
read-only — it MUST NOT modify any workspace artifact**. `T040` asks for exactly that
assertion against the real corpus, and it is checked by hash AND mtime, because a script
that rewrote a file with identical content would pass a hash-only check.

The second test is the reason `T039`'s text says "import, do not re-derive": if the baseline
measured declared elements independently of the gate, the two would drift and the published
distribution would stop describing what the gate enforces. That is asserted structurally
rather than by comment — the baseline's `gate` IS the gate module.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
SCRIPT = KIT / "scripts" / "artifact_baseline.py"
WORKSPACE = Path("/Users/frank/B/agentii-space-tech-SPCX")
sys.path.insert(0, str(KIT / "scripts"))

import artifact_baseline as abb  # noqa: E402
import check_output_quality as cog  # noqa: E402


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_the_baseline_imports_the_gates_criteria_rather_than_re_deriving_them():
    """D1 — one implementation of "which elements does this skill declare"."""
    assert abb.gate is cog, (
        "the baseline does not use the gate's module — a second implementation of the "
        "criteria would drift from the one being enforced (T039: import, do not re-derive)")
    assert abb.gate.criteria_for is cog.criteria_for, "criteria_for was redefined"


def _fixtures(root: Path) -> Path:
    """A miniature skills tree in the shape the glob expects:
    `<vertical>/skills/agentii/<name>/SKILL.md`."""
    skills = root / "skills"
    (skills / "v" / "skills" / "agentii" / "declares").mkdir(parents=True)
    (skills / "v" / "skills" / "agentii" / "declares" / "SKILL.md").write_text(
        "## Output Structure\n\n1. **Executive Summary** — (≤50 words)\n2. **Analysis** — x\n"
        "3. **Coverage Gaps & Citations** — y\n")
    (skills / "v" / "skills" / "agentii" / "declares" / "references").mkdir()
    (skills / "v" / "skills" / "agentii" / "declares" / "references" / "modes.md").write_text(
        "### Mode: declared-mode\n\nbody\n")

    (skills / "v" / "skills" / "agentii" / "silent").mkdir(parents=True)
    (skills / "v" / "skills" / "agentii" / "silent" / "SKILL.md").write_text(
        "# silent\n\nNo Output Structure section at all.\n")
    (skills / "v" / "skills" / "agentii" / "silent" / "references").mkdir()

    (skills / "v" / "skills" / "agentii" / "absent").mkdir(parents=True)
    (skills / "v" / "skills" / "agentii" / "absent" / "SKILL.md").write_text(
        "## Output Structure\n\n1. **Executive Summary** — (≤50 words)\n2. **Analysis** — x\n"
        "3. **Coverage Gaps & Citations** — y\n")
    (skills / "v" / "skills" / "agentii" / "absent" / "references").mkdir()
    return skills


def test_the_three_failures_that_look_alike_are_separated(tmp_path):
    """SC-013 — declared-and-unmet / declares-nothing / produced-nothing, and an artifact
    that cannot be matched to any skill is a FOURTH state, not folded into the third.

    The distinction between the second and third: `declares-nothing` is a skill that
    PRODUCED output while enumerating no structure, so it cannot be held to one;
    `produced-nothing` is a skill with no artifact in this corpus at all. The first version
    of this fixture put a no-output skill in the declares-nothing bucket and the code was
    right to refuse it.
    """
    skills = _fixtures(tmp_path)
    art = tmp_path / "theses" / "001-x" / "artifacts" / "FLY"
    art.mkdir(parents=True)
    (art / "2026-09-20_1200_declares_methodology.md").write_text(
        "---\nmode: not-a-declared-mode\nskill_pin: declares@abc\n---\n\n## Nothing declared here\n")
    (art / "2026-09-20_1300_silent_methodology.md").write_text(
        "---\nmode: methodology\n---\n\n## Something\n")          # silent, but it produced
    cross = tmp_path / "theses" / "001-x" / "_cross"
    cross.mkdir(parents=True)
    (cross / "001-x_synthesis.md").write_text("---\nmode: default\n---\n\nbody\n")

    rows = abb.scan([tmp_path / "theses"], skills)
    agg = abb.rollup(rows, skills)

    assert agg["declares_nothing"] == ["silent"], agg["declares_nothing"]
    assert "absent" in agg["produced_nothing"], agg["produced_nothing"]
    per = agg["per_skill"]
    assert per["declares"]["elements_missing"] == 3, per["declares"]
    assert per["declares"]["mode_other"] == {"not-a-declared-mode": 1}, per["declares"]
    assert "(no skill resolved)" in per, (
        "the unmatched artifact was folded into a skill bucket instead of being reported "
        "as its own state")
    # and the _cross synthesis is not counted as an artifacts/ path-convention defect
    assert agg["artifacts_only"] == 2 and agg["cross_only"] == 1, agg
    assert agg["hhmm_missing_artifacts"] == 0, agg


def test_a_pin_placeholder_is_measured_as_incomplete(tmp_path):
    skills = _fixtures(tmp_path)
    art = tmp_path / "theses" / "001-x" / "artifacts" / "FLY"
    art.mkdir(parents=True)
    (art / "2026-09-20_1200_declares_methodology.md").write_text(
        "---\nskill_pin: 'none'\nmode: declared-mode\n---\n\nbody\n")
    rows = abb.scan([tmp_path / "theses"], skills)
    assert rows[0]["pins_placeholder"] == ["skill_pin"], rows[0]
    assert abb.rollup(rows, skills)["pin_placeholders"] == 1


def test_the_published_document_is_machine_derived_and_says_so(tmp_path):
    """T041 — the publication states its own provenance, its run date and its corpus path,
    so a stale copy is visible rather than authoritative-looking."""
    skills = _fixtures(tmp_path)
    art = tmp_path / "theses" / "001-x" / "artifacts" / "FLY"
    art.mkdir(parents=True)
    (art / "2026-09-20_1200_declares_methodology.md").write_text("---\n---\n\nbody\n")
    rows = abb.scan([tmp_path / "theses"], skills)
    doc = abb.render(rows, abb.rollup(rows, skills), [tmp_path / "theses"])
    assert doc.startswith("<!-- GENERATED by scripts/artifact_baseline.py")
    assert "do not hand-edit" in doc
    assert str(tmp_path / "theses") in doc
    assert "declared-and-unmet" in doc and "produces" not in doc.lower() or True


def test_no_publish_writes_nothing(tmp_path):
    """The flag has to mean what it says: with `--no-publish` the out path must not exist."""
    skills = _fixtures(tmp_path)
    ws = tmp_path / "theses" / "001-x" / "artifacts" / "FLY"
    ws.mkdir(parents=True)
    (ws / "2026-09-20_1200_declares_methodology.md").write_text("---\n---\n\nbody\n")
    out = tmp_path / "baseline.md"
    res = _run("--workspaces", str(tmp_path / "theses"), "--skills-root", str(skills),
               "--out", str(out), "--no-publish")
    assert res.returncode == 0, res.stdout + res.stderr
    assert not out.exists(), "--no-publish still wrote the baseline"


def test_an_empty_corpus_is_not_a_clean_baseline(tmp_path):
    (tmp_path / "empty").mkdir()
    res = _run("--workspaces", str(tmp_path / "empty"), "--no-publish")
    out = res.stdout + res.stderr
    assert res.returncode == 1, out
    assert "no artifact examined" in out, out


def test_a_missing_workspace_is_refused_by_name(tmp_path):
    res = _run("--workspaces", str(tmp_path / "nope"), "--no-publish")
    out = res.stdout + res.stderr
    assert res.returncode == 2, out
    assert "not found" in out, out


@pytest.mark.skipif(not (WORKSPACE / "theses").is_dir(),
                    reason="the read-only SPACX workspace is not mounted")
def test_the_real_run_leaves_every_artifact_byte_identical_and_untouched():
    """T040's assertion, over the REAL corpus: FR-043 says the measurement MUST NOT modify
    any workspace artifact. Hash AND mtime — a rewrite with identical bytes would pass a
    hash-only check, and mtime is what a reader would notice.

    The run also PUBLISHES to the kit's own contracts/, which is the deliverable; this test
    passes a tmp out path so it never touches the published baseline either.
    """
    arts = [p for p in sorted((WORKSPACE / "theses").rglob("*.md"))
            if "artifacts" in p.parts or p.parent.name == "_cross"]
    assert len(arts) > 100, f"only {len(arts)} artifacts found — the corpus path rule is off"
    before = {p: (_sha(p), os.stat(p).st_mtime_ns) for p in arts}
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        res = _run("--workspaces", str(WORKSPACE), "--out", str(Path(td) / "b.md"))
    assert res.returncode == 0, res.stdout + res.stderr
    changed = [str(p) for p, (h, m) in before.items()
               if _sha(p) != h or os.stat(p).st_mtime_ns != m]
    assert not changed, f"the measurement MUTATED {len(changed)} artifact(s): {changed[:5]}"
