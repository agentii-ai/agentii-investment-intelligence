"""test_artifact_citations.py — FR-041's negative fixtures (spec 058 T021).

Every rule below has a fixture that MUST fail, and the rule's own scoping is tested too:
the same literal template that fails in a citation *position* must PASS when an artifact
is quoting it. That second case is not politeness — measured 2026-09-21, all three
occurrences of the unexpanded template in the real corpus are artifacts quoting the
instruction while reporting that it is unsatisfiable, and `tasks.md` T021 had listed one
of them as a malformed citation. A gate that fires on documentation gets switched off.

The three malformed forms T021 names, and what each actually is in the corpus:
  (a) `/v/SPEC/005/958` — the thesis number in the `citation_id` slot. 2 live instances,
      both inline link destinations in 005's `LUNR/2026-09-20_competitive_methodology.md`.
  (b) `/v/YSS/agentii://source/<uuid>/2` — the platform's internal identifier pasted into
      the public path. 1 live instance, a frontmatter `url:` in 005's YSS artifact.
  (c) `https://agentii.ai/v/{ticker}/{citation_id}/{page}` — **quoted documentation in all
      three places it occurs**, so it is NOT a malformed-citation category. The category
      the task was reaching for — an unexpanded template in a citation POSITION — is real
      and is tested below; the corpus simply does not contain one.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KIT / "scripts"))

import check_artifact_citations as c  # noqa: E402

WORKSPACE = Path("/Users/frank/B/agentii-space-tech-SPCX")


def _art(tmp_path: Path, body: str, frontmatter: str = "ticker: FLY\n") -> Path:
    p = tmp_path / "artifact.md"
    p.write_text(f"---\n{frontmatter}---\n\n{body}")
    return p


def _problems(tmp_path: Path, body: str, frontmatter: str = "ticker: FLY\n") -> list[str]:
    p = _art(tmp_path, body, frontmatter)
    problems, _ = c.check_text(p.read_text(), where=p.name)
    return problems


# ── (a) the thesis number in the citation_id slot ───────────────────────────

def test_thesis_number_in_the_citation_id_slot_fails(tmp_path):
    """The live form verbatim: `[spec.md:958](https://agentii.ai/v/SPEC/005/958)`."""
    problems = _problems(tmp_path, "> P3** ([spec.md:958](https://agentii.ai/v/SPEC/005/958)).\n")
    assert problems, "the live malformed form passed"
    assert "[a-z]+[0-9]+" in " ".join(problems), (
        f"the failure does not name the pattern the id must satisfy:\n{problems}")
    assert "SPEC/005" in " ".join(problems), f"the failure does not quote the url:\n{problems}"


def test_a_wellformed_inline_link_passes(tmp_path):
    """The control. Without this, a gate that failed everything would look identical.

    The fixture carries a `citations` block on purpose: without it the SECOND rule fires
    (prose-cited, nothing recorded) and this test would be measuring the wrong rule — which
    is what its first version did, and the gate was right to fail it.
    """
    fm = ("ticker: FLY\ncitations:\n"
          "  - figure: \"8-K page\"\n"
          "    url: \"https://agentii.ai/v/LUNR/sec525/58\"\n")
    problems = _problems(tmp_path,
                         "See ([📄 LUNR 8-K p.58](https://agentii.ai/v/LUNR/sec525/58)).\n", fm)
    assert problems == [], f"a well-formed citation failed:\n{problems}"


# ── (b) a nested scheme inside the path ─────────────────────────────────────

def test_a_nested_agentii_scheme_in_the_path_fails(tmp_path):
    """The live form: the platform's internal identifier pasted into the public URL."""
    fm = ('citations:\n  - figure: "181 facts"\n'
          '    citation_id: "agentii://source/c1b8bdad-e745-4764-ae16-cd732e37c20d?page=page2"\n'
          '    url: "https://agentii.ai/v/YSS/agentii://source/c1b8bdad-e745-4764-ae16-cd732e37c20d/2"\n')
    problems = _problems(tmp_path, "Body.\n", fm)
    assert problems, "the nested-scheme url passed"
    assert any("nested URL scheme" in p for p in problems), problems


# ── (c) an unexpanded template: position decides ────────────────────────────

def test_a_template_in_a_citation_position_fails(tmp_path):
    """The category is real; it just has no live instance. A link destination that was
    never filled in resolves to nothing."""
    problems = _problems(tmp_path, "See ([📄](https://agentii.ai/v/{ticker}/{citation_id}/{page})).\n")
    assert problems, "an unexpanded template in a link destination passed"
    assert any("unexpanded template" in p for p in problems), problems


def test_a_quoted_template_is_documentation_not_a_defect(tmp_path):
    """THE FALSE-POSITIVE GUARD, and the reason the corpus matters.

    This is 002's NVDA artifact verbatim (2026-09-18_1500_secular-trends_methodology.md:398-404):
    an artifact quoting the contract's own form while reporting that the contract cannot
    admit the source class it names. All three corpus occurrences of the literal template
    are this shape. Flagging them would fail the artifacts doing the right thing.
    """
    body = (
        "> ⚠️ **A contract gap this artifact is the first to hit.** PIL-2's falsifier names\n"
        "> `source=peer_reviewed_literature_or_flown_hardware_disclosure`, but\n"
        "> `contracts/artifact-frontmatter.yaml` admits citation URLs only in the form\n"
        "> `https://agentii.ai/v/{ticker}/{citation_id}/{page}` (`citation_url_wellformed`,\n"
        "> level `fail`; `located_via` has no external enum).\n"
    )
    problems = _problems(tmp_path, body)
    assert problems == [], (
        "a quotation of the form was reported as a malformed citation — the gate cannot "
        f"tell documentation from a defect, which is how a gate gets switched off:\n{problems}")


# ── the contract's own stated failure: the ticker-less short form ───────────

def test_the_tickerless_short_form_fails(tmp_path):
    """`citation_url_wellformed` says this form does not resolve and why: the portal route
    redirects to `api.agentii.ai/v1/view_document/{ticker}/{citation_id}` and cannot join
    without a ticker."""
    problems = _problems(tmp_path, "See ([📄 LUNR 8-K](https://agentii.ai/v/sec525/58)).\n")
    assert problems, "the ticker-less short form passed"
    assert any("ticker-less short form" in p for p in problems), problems
    assert any("view_document" in p for p in problems), (
        f"the failure does not say WHY it cannot resolve:\n{problems}")


def test_citations_in_prose_without_a_recorded_block_fail(tmp_path):
    """FR-041's other half: prose links that nothing can join on later. 7 artifacts are in
    this state today."""
    problems = _problems(tmp_path, "Per ([📄 LUNR 8-K p.58](https://agentii.ai/v/LUNR/sec525/58)).\n")
    assert any("no non-empty `citations` block" in p for p in problems), problems


def test_an_artifact_with_a_citations_block_and_links_passes(tmp_path):
    """The control for the rule above — the block is the thing that makes links
    addressable, so its presence must satisfy the rule."""
    fm = ("ticker: FLY\ncitations:\n"
          "  - figure: \"revenue\"\n"
          "    url: \"https://agentii.ai/v/LUNR/sec525/58\"\n")
    problems = _problems(tmp_path,
                         "Per ([📄 LUNR 8-K p.58](https://agentii.ai/v/LUNR/sec525/58)).\n", fm)
    assert problems == [], problems


# ── the surface, and the "examined nothing" state ───────────────────────────

def test_a_directory_with_no_artifacts_is_reported_not_passed(tmp_path):
    """A zero surface must not read as clean (FR-006, one layer up)."""
    empty = tmp_path / "empty"
    empty.mkdir()
    res = subprocess.run(
        [sys.executable, str(KIT / "scripts" / "check_artifact_citations.py"), str(empty)],
        capture_output=True, text=True)
    out = res.stdout + res.stderr
    assert res.returncode != 0, f"an empty tree passed:\n{out}"
    assert "no artifact examined" in out, out


def test_the_clean_surface_is_reported_with_its_counts(tmp_path):
    """`OK` must carry the counts, so a run over one file cannot read like a run over the
    corpus — the same lesson as the gate's own surface table (T126)."""
    p = _art(tmp_path, "See ([📄 LUNR 8-K p.58](https://agentii.ai/v/LUNR/sec525/58)).\n",
             "ticker: FLY\ncitations:\n  - url: \"https://agentii.ai/v/LUNR/sec525/58\"\n")
    res = subprocess.run(
        [sys.executable, str(KIT / "scripts" / "check_artifact_citations.py"), str(p)],
        capture_output=True, text=True)
    out = res.stdout + res.stderr
    assert res.returncode == 0, out
    assert "1 artifact(s)" in out and "inline link(s)" in out, out


# ── against the real corpus, when it is present ─────────────────────────────

@pytest.mark.skipif(not (WORKSPACE / "theses").is_dir(),
                    reason="the read-only SPACX workspace is not mounted")
def test_it_finds_the_live_instances_the_audit_measured():
    """The whole point of a gate is that it fires on the real thing. Read-only: it reads
    two directories and writes nothing. Skips where the workspace is absent, so the suite
    does not depend on another repository's presence."""
    root = WORKSPACE / "theses" / "005-launch-spacecraft-services" / "artifacts"
    problems, examined = c.check_artifacts(root)
    joined = "\n".join(problems)
    assert examined["artifacts"] > 0, "no artifacts examined — the fixture path is wrong"
    assert "/v/SPEC/005/958" in joined, (
        f"the live form (a) was not detected:\n{joined[:2000]}")
    assert "/v/SPEC/005/435" in joined, joined[:2000]
    assert "agentii://source/" in joined, (
        f"the live form (b) was not detected:\n{joined[:2000]}")
