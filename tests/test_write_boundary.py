"""test_write_boundary.py — T177 (Q124/Q127/Q138/Q142/Q147).

**Asserted by TRACING, not by reading.** A test that greps the four writers for
`write_boundary.write` proves that a string appears in a file; it does not prove
the write goes through the boundary. The distinction matters here more than
usual, because Q147's finding was precisely that a named location had **four
implementations and zero gates** — and a grep-based test would have reported that
as compliant the moment the four call sites were renamed.

So the central test instruments `Path.write_text` itself, runs each writer, and
asserts that **every byte that reached the filesystem came through
`write_boundary`**. A second write path anywhere — including one added later by
someone who did not read this file — fails it.

The rest pin the three gate families: credential blocked, second writer refused,
and the mode-independent gates running in single-skill mode (the mode that
previously had *no* gate at all, since every gate was declared thesis-only).
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import write_boundary  # noqa: E402


# ── the tracing harness ─────────────────────────────────────────────────────

class WriteTracer:
    """Records every `Path.write_text` and which module frames produced it."""

    def __init__(self, monkeypatch):
        self.calls: list[tuple[Path, bool]] = []      # (path, came_through_boundary)
        orig = Path.write_text

        def traced(self_path, *a, **kw):
            via = any("write_boundary" in f.filename
                      for f in traceback.extract_stack())
            self.calls.append((Path(self_path), via))
            return orig(self_path, *a, **kw)

        monkeypatch.setattr(Path, "write_text", traced, raising=True)

    def bypasses(self) -> list[Path]:
        return [p for p, via in self.calls if not via]


# ── T177: one writer, proven by trace ───────────────────────────────────────

def test_every_writer_routes_through_the_boundary(tmp_path, monkeypatch):
    """Run every writer; every filesystem write must come via the boundary.

    The four Q147 measured all had their own private `_atomic_write`, i.e. their own
    gate-free path: `synthesize_report.py`, `reduce_journals.py`, `thesis_status.py`,
    `portfolio_aggregate.py`.

    **This docstring said "all four" and the body ran three — `synthesize_report` was
    never invoked — and `agentii_cmd` was not in the set at all.** That omission is
    where the thesis.md seam lived: `agentii_cmd._write` was a bare `Path.write_text`,
    the one write path to `thesis.md` that the boundary never saw, and the test named
    for exactly this property did not cover it. The tracer now runs `agentii_cmd`
    too, because a tracer that enumerates its own subjects by memory will keep
    missing the one that was added last.
    """
    import agentii_cmd
    import portfolio_aggregate
    import reduce_journals
    import thesis_status

    tracer = WriteTracer(monkeypatch)

    # agentii_cmd: the scaffold path — constitution, L1 files, specify's thesis.md.
    # Without this call the seam was untested: this was the ungated writer.
    ws = tmp_path / "ac-ws"
    agentii_cmd.constitution_scaffold(ws)

    # reduce_journals: journal shards -> thesis.reduce.json (the Q15 machine file)
    shard_dir = tmp_path / "shards"; shard_dir.mkdir()
    (shard_dir / "run1.ndjson").write_text(
        '{"skill_id": "dcf", "ticker": "NVDA", "entity_claims": [], "status": "ok"}\n'
        '{"skill_id": "risk", "ticker": "NVDA", "entity_claims": [], "status": "ok"}\n',
        encoding="utf-8")
    (tmp_path / "theses" / "001-mvp").mkdir(parents=True)
    reduce_journals.reduce(shard_dir, tmp_path / "theses" / "001-mvp" / "thesis.md")

    # thesis_status: workspace -> theses/INDEX.md
    (tmp_path / "theses" / "001-x").mkdir(parents=True)
    thesis_status.main(["--workspace", str(tmp_path)])

    # portfolio_aggregate: workspace -> _portfolio/{portfolio-view,conflicts}.md
    portfolio_aggregate.main(["--workspace", str(tmp_path)])

    assert tracer.calls, "no writes were traced at all — the harness is broken"
    assert not tracer.bypasses(), (
        f"{len(tracer.bypasses())} write(s) bypassed the boundary: "
        f"{[str(p) for p in tracer.bypasses()]}. Every persistent artifact must go "
        f"through write_boundary.write (Q147) — a gate attached to one of N "
        f"writers is worse than no gate, because it reads as enforced.")


def test_boundary_is_the_only_definition_of_the_atomic_write():
    """The four private `_atomic_write` copies must be gone. Checked by parsing
    the module for a definition, and by confirming no writer module defines one —
    a definition is stronger evidence of a second path than a call is.

    Unparseable files are REPORTED, not skipped silently: `scripts/` contains one
    (`port-dimension-prompts.py`, marked RETIRED — 2026-06-13) whose body is not
    valid Python. It is retired so it is not a live write path, but a `.py` that
    a linter cannot read is exactly the kind of file a gate silently steps over —
    so this test says so rather than pretending the directory parsed cleanly."""
    import ast
    offenders, unparseable = [], []
    for f in sorted((ROOT / "scripts").glob("*.py")):
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as e:
            unparseable.append(f"{f.name}:{e.lineno} ({e.msg})")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_atomic_write":
                offenders.append(f.name)
    assert offenders == ["write_boundary.py"], (
        f"`_atomic_write` is defined in {offenders}. It was defined in four "
        f"writers before T172; each definition was a gate-free write path.")
    if unparseable:
        print(f"\n  NOTE — {len(unparseable)} file(s) in scripts/ do not parse as "
              f"Python and were not examined: {unparseable}")


# ── Q124: credentials block, and the block does not touch the disk ──────────

@pytest.mark.parametrize("secret,kind", [
    ("sk-ant-api03-aaaaaaaaaaaaaaaaaaaaaaaaaaaa", "anthropic-key"),
    ("ghp_abcdefghijklmnopqrstuvwxyz0123456789", "github-token"),
    ("AKIAIOSFODNN7EXAMPLE", "aws-access-key"),
    ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "bearer-token"),
    ("FMP_API_KEY=8f14e45fceea167a5a36dedd4bea2543", "assigned-secret"),
    ("-----BEGIN RSA PRIVATE KEY-----", "private-key-block"),
])
def test_credential_shapes_block_the_write(tmp_path, secret, kind):
    target = tmp_path / "session.md"
    target.write_text("prior content\n", encoding="utf-8")
    r = write_boundary.write(target, f"# notes\n{secret}\n",
                            producer="test", writer="test")
    assert r.verdict == "blocked", r.describe()
    assert any(kind in reason for reason in r.reasons), r.reasons
    assert target.read_text(encoding="utf-8") == "prior content\n", (
        "a blocked write must leave the file untouched")


def test_the_block_records_the_producing_command(tmp_path):
    """Q124: the hit must record WHICH command produced the content — that is
    what makes a leak traceable and a rotation targeted instead of blanket."""
    r = write_boundary.write(tmp_path / "x.md", "sk-ant-" + "a" * 30,
                             producer="agentii.synthesize", writer="s")
    assert "agentii.synthesize" in " ".join(r.reasons)


def test_the_reported_excerpt_does_not_reproduce_the_secret(tmp_path):
    """A scanner that echoes the secret reproduces the harm it exists to stop."""
    secret = "sk-ant-api03-ZZZZZZZZZZZZZZZZZZZZZZZZ"
    r = write_boundary.write(tmp_path / "x.md", secret, producer="t", writer="t")
    joined = " ".join(r.reasons)
    assert secret not in joined, "the report echoed the credential"
    assert "***" in joined, "the excerpt should be masked"


def test_documentation_style_key_names_do_not_trip_the_scan(tmp_path):
    """`FMP_API_KEY=` with no value, and prose about keys, are not leaks. A gate
    that fires on the repo's own contracts gets disabled, not fixed."""
    r = write_boundary.write(
        tmp_path / "c.md",
        "Set `FMP_API_KEY` for higher limits.\nexport FINNHUB_API_KEY\n",
        producer="t", writer="t")
    assert r.ok(), r.describe()


def test_already_redacted_content_passes(tmp_path):
    r = write_boundary.write(tmp_path / "r.md",
                             "The key was `sk-ant-***REDACTED***` — rotate it.\n",
                             producer="t", writer="t")
    assert r.ok(), r.describe()


# ── Q127 / Q138: the second writer is REFUSED, not merged ───────────────────

def test_second_writer_is_refused_not_merged(tmp_path):
    """The observed case: two sessions interleaved one plan document until it
    grew 2.2x. Q127 refuses rather than merging, and Q138 puts `writer:` in the
    document so the refusal is decidable by reading that document alone."""
    p = tmp_path / "plan.md"
    first = "---\nwriter: session-a\n---\n\n# plan\n\n- item one\n"
    assert write_boundary.write(p, first, producer="a", writer="session-a").ok()

    r = write_boundary.write(p, "---\nwriter: session-b\n---\n\n# other\n",
                             producer="b", writer="session-b")
    assert r.verdict == "refused", r.describe()
    assert p.read_text(encoding="utf-8") == first, "refused means UNCHANGED"


def test_same_writer_may_rewrite(tmp_path):
    p = tmp_path / "plan.md"
    write_boundary.write(p, "---\nwriter: a\n---\n\none\n", producer="a", writer="a")
    r = write_boundary.write(p, "---\nwriter: a\n---\n\ntwo\n", producer="a", writer="a")
    assert r.ok(), r.describe()


def test_undeclared_writer_is_append_only(tmp_path):
    """Q127's fail-safe, and its most important clause: 'undeclared' must never
    silently mean 'anyone may overwrite'. An append is allowed; a rewrite is not."""
    p = tmp_path / "notes.md"
    base = "no frontmatter here\nline two\n"
    write_boundary.write(p, base, producer="a")
    r = write_boundary.write(p, base + "appended line\n", producer="b")
    assert r.ok(), r.describe()
    r = write_boundary.write(p, "completely different\n", producer="b")
    assert r.verdict == "refused", r.describe()
    assert "APPEND-ONLY" in " ".join(r.reasons)


def test_writer_declaration_is_read_from_the_document_alone(tmp_path):
    """Q138 chose frontmatter over a workspace registry precisely so the verdict
    is decidable at the moment of the second write by reading ONE file."""
    text = "---\nticker: NVDA\nwriter: reduce_journals\nas_of: 2026-09-18\n---\n\nbody\n"
    assert write_boundary.declared_writer(text) == "reduce_journals"
    assert write_boundary.declared_writer("no frontmatter") is None


# ── Q142 / T175: the mode-independent gates run in SINGLE-SKILL mode ────────

def test_citation_density_gate_fires_in_single_skill_mode(tmp_path):
    """The point of Q142: this gate must run where there is no thesis. Before
    T172 there was no execution point at all in single-skill mode."""
    body = "# Report\n\n" + ("analysis of the segment " * 80)   # ~400 words, 0 cites
    r = write_boundary.write(tmp_path / "r.md", body, producer="t", mode="single-skill")
    assert any("citation-density" in reason for reason in r.reasons), r.describe()


def test_evidence_class_gate_says_it_could_not_run_without_the_field(tmp_path):
    """Q146: the determination must be a FIELD. When it is absent the gate reports
    that it could not run, rather than guessing from prose — Q105 applied here."""
    r = write_boundary.write(tmp_path / "r.md", "# Report\n\nsome prose\n", producer="t")
    assert any("NO `support:`" in reason for reason in r.reasons), r.describe()


def test_number_canonical_form_flags_a_percentage_rate(tmp_path):
    body = "growth_rate: 12%\n[[cite]]\n"
    r = write_boundary.write(tmp_path / "r.md", body, producer="t")
    assert any("number-canonical-form" in reason for reason in r.reasons), r.describe()


def test_prose_gates_are_skipped_for_json_and_say_so(tmp_path):
    """Running a citation-density check over thesis.md's JSON would report
    `examined: 0` and pass — a vacuous success. It is skipped, and the skip is
    recorded, which is the difference between those two."""
    r = write_boundary.write(tmp_path / "thesis.md", '{"judgment": {"claims": []}}\n',
                             producer="t", kind="json", writer="reduce_journals")
    assert r.ok(), r.describe()
    assert any("prose gates SKIPPED" in e for e in r.examined), r.examined


def test_the_boundary_reports_what_it_examined(tmp_path):
    """Q105 on the boundary itself: a write that returned success while checking
    nothing would be the same defect this file was built to fix."""
    r = write_boundary.write(tmp_path / "r.md", "# t\n[[c]]\n", producer="t", writer="t")
    assert r.ok()
    assert len(r.examined) >= 4, r.examined
    assert any("credential-shapes" in e for e in r.examined)


# ── Q124's false-positive budget, pinned from a real scan ───────────────────

@pytest.mark.parametrize("line", [
    "export AGENTII_API_KEY=sk_live_YOUR_KEY_HERE",
    'status="$(curl -H "x-api-key: sk_live_BAD_KEY_FOR_GATE_TEST" "$BASE/v1/x")"',
    "FMP_API_KEY=REPLACE_ME",
    "FINNHUB_API_KEY=<YOUR_FINNHUB_KEY>",
])
def test_measured_placeholders_do_not_block(tmp_path, line):
    """These four strings are the ACTUAL false positives a scan of this repo
    produced (1,243 text files → 12 hits, 4 of them documentation placeholders,
    0 real leaks). Q124's hit semantics are blocking, so without this a README
    write would be refused — and a gate that fires on its own documentation gets
    disabled rather than fixed."""
    r = write_boundary.write(tmp_path / "doc.md", line + "\n", producer="t", writer="t")
    assert r.ok(), r.describe()


def test_a_real_looking_key_still_blocks(tmp_path):
    """The placeholder exclusion must not become a hole. A 32-hex FMP key with a
    real prefix still blocks."""
    r = write_boundary.write(tmp_path / "x.md",
                             "FMP_API_KEY=8f14e45fceea167a5a36dedd4bea2543\n",
                             producer="t", writer="t")
    assert r.verdict == "blocked", r.describe()


# ── T124: the artifact citation gate (Q102) ────────────────────────────────

_ARTIFACT_BARE = ("# NVDA — recent quarter\n\n"
                  "Revenue per 0001819994-26-000062 p37 was $4.1B.\n")
_ARTIFACT_LINKED = ("# NVDA — recent quarter\n\n"
                    "Revenue was $4.1B [source](https://agentii.ai/v/NVDA/sec8/37).\n")


def test_bare_accession_artifact_is_blocked(tmp_path):
    """Q102's measured case: 44 artifacts, 0 occurrences of `agentii.ai/v/`.
    Honest and UNFOLLOWABLE — a reader cannot open the source, which for
    usability is the same as having none."""
    r = write_boundary.write(tmp_path / "nvda_recent-quarter_default.md",
                             _ARTIFACT_BARE, producer="t", writer="t", citable=True)
    assert r.verdict == "blocked", r.describe()
    assert any("bare accession" in x for x in r.reasons), r.reasons


def test_followable_citation_passes(tmp_path):
    r = write_boundary.write(tmp_path / "a.md", _ARTIFACT_LINKED,
                             producer="t", writer="t", citable=True)
    assert r.ok(), r.describe()


def test_zero_citations_and_unfollowable_stay_distinct(tmp_path):
    """Q100's whole point: a report that cites nothing and a report whose
    citations cannot be opened are DIFFERENT failures with different fixes."""
    r_zero = write_boundary.write(tmp_path / "z.md", "# t\n\nprose only\n",
                                  producer="t", writer="t", citable=True)
    r_bare = write_boundary.write(tmp_path / "b.md", _ARTIFACT_BARE,
                                  producer="t", writer="t", citable=True)
    assert any("0 citations of any form" in x for x in r_zero.reasons)
    assert any("bare accession" in x for x in r_bare.reasons)
    assert r_zero.reasons != r_bare.reasons


def test_non_artifact_reports_that_the_citation_gate_did_not_run(tmp_path):
    """Q105: a clean result on INDEX.md must not be read as a citation verdict."""
    r = write_boundary.write(tmp_path / "INDEX.md", "# theses\n", producer="t", writer="t")
    assert r.ok()
    assert any("citation-form NOT RUN" in e for e in r.examined), r.examined


# ── T126: the evidence-image gate (Q96) ────────────────────────────────────

_IMG = '<img src="data:image/png;base64,AAAA" data-source="sec8-p37">'


def test_image_with_a_source_and_no_licence_registry_says_it_could_not_evaluate(tmp_path):
    """Q96 puts licence POLICY in the vertical; this is the MECHANISM. With no
    registry the gate reports that it could not evaluate rather than guessing."""
    r = write_boundary.write(tmp_path / "r.html", _IMG, producer="t", writer="t")
    assert any("no licence registry supplied" in x for x in r.reasons), r.reasons


def test_unknown_licence_counts_as_restricted(tmp_path):
    r = write_boundary.write(tmp_path / "r.html", _IMG, producer="t", writer="t",
                             licences={})
    assert r.verdict == "blocked", r.describe()
    assert any("UNKNOWN" in x for x in r.reasons)


def test_restricted_licence_is_refused_and_permissive_passes(tmp_path):
    r = write_boundary.write(tmp_path / "r.html", _IMG, producer="t", writer="t",
                             licences={"sec8-p37": "all-rights-reserved"})
    assert r.verdict == "blocked", r.describe()
    r = write_boundary.write(tmp_path / "ok.html", _IMG, producer="t", writer="t",
                             licences={"sec8-p37": "public-domain"})
    assert r.ok(), r.describe()


def test_external_image_is_refused_even_with_a_permissive_licence(tmp_path):
    """Q46's offline-printable requirement is independent of licence: an external
    `<img src>` is an external dependency whatever its terms."""
    r = write_boundary.write(tmp_path / "r.html",
                             '<img src="https://example.com/a.png" data-source="s">',
                             producer="t", writer="t", licences={"s": "cc0"})
    assert r.verdict == "blocked", r.describe()
    assert any("not a base64 data URI" in x for x in r.reasons)


def test_untraced_raster_image_is_REPORTED_not_refused(tmp_path):
    """Q96 step 4 says "no citation ⇒ refuse", but that governs the RETRIEVAL
    pipeline. At the boundary, refusing an untraced figure blocks every report
    over a hand-drawn chart without adding the provenance — so it is reported.

    The over-blocking version of this gate was caught by
    tests/test_s7_verification.py::test_chart_token_rendered, which renders a
    real report."""
    r = write_boundary.write(tmp_path / "r.html",
                             '<img src="data:image/png;base64,AAAA">',
                             producer="t", writer="t", licences={})
    assert r.verdict == "written", r.describe()
    assert any("data-source" in x for x in r.reasons), r.reasons


def test_generated_svg_chart_is_not_judged_by_the_licence_gate(tmp_path):
    """Q48's charts are inline base64 SVG generated from `data-chart` tokens —
    there is no source document to license, and Q96 is about RETRIEVED evidence
    images. Judging these blocked every report."""
    r = write_boundary.write(tmp_path / "r.html",
                             '<img src="data:image/svg+xml;base64,AAAA">',
                             producer="t", writer="t")
    assert r.ok(), r.describe()
    assert not any("image-licence" in x for x in r.reasons), r.reasons


# ── T127: symbol existence (Q96's cousin — the silent substitution) ────────

def test_nonexistent_symbol_refuses_and_names_near_misses():
    """The measured case: `search_xbrl_facts(ticker=ALNT)` returned **ALNY
    (Alnylam)**, a different company. The session that hit it wrote the
    consequence as *"confident, fully-cited, wrong data"*. Absence is
    recoverable; substitution is not, because nothing downstream can tell."""
    import sys as _s
    _s.path.insert(0, str(ROOT / "data-tools"))
    import _envelope as env

    known = ["NVDA", "AAPL", "ALNY", "GOOG", "MSFT"]
    r = env.symbol_refusal("ALNT", known, source="search_xbrl_facts")
    assert r is not None and r["status"] == "error"
    assert "ALNY" in r["error"], "the near miss must be named"
    assert r["source"] == "search_xbrl_facts"
    env.validate(r)                       # it is a valid envelope


def test_known_symbol_returns_no_refusal():
    import sys as _s
    _s.path.insert(0, str(ROOT / "data-tools"))
    import _envelope as env

    known = ["NVDA", "AAPL"]
    assert env.symbol_refusal("NVDA", known) is None
    # case / separator differences are the SAME symbol, not a near miss
    assert env.symbol_refusal("nvda", known) is None


def test_unknown_symbol_without_a_near_miss_says_so():
    import sys as _s
    _s.path.insert(0, str(ROOT / "data-tools"))
    import _envelope as env

    r = env.symbol_refusal("ZZZZ", ["NVDA", "AAPL"])
    assert r["status"] == "error"
    assert "No near miss" in r["error"]
