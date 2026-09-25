"""test_check_citation_resolution.py — the offline half of the live citation check (062 `T083`).

THE NETWORK HALF CANNOT BE TESTED HERE, and saying so is the point: `check_citation_resolution.py`
verifies against `api.agentii.ai`, so a test of it needs the service and a credential. What CAN be
tested is the half where a bug would be silent — **which citations get counted and how they group**.

That half is where the first version of the script was wrong, in a way no live run would have
revealed: it reported `citations: 497 of 987` for a corpus holding **6,530** citations, because it was
counting distinct `(document, page)` PAIRS and calling them citations. The live verdict was right and
the label was wrong, which is the worst combination — a correct number wearing a name that means
something else gets quoted.

**BOTH LINK FORMS ARE COUNTED.** The corpus writes `/{N}` 2,244 times and `/page{N}` 948 times, and the
`LINK_RX` regression that missed the second form once moved a headline figure by 7×. This file pins the
grouping over both.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_citation_resolution as res  # noqa: E402

FM = "---\nas_of: 2026-09-01\n---\n"


def _artifact(tmp_path, name: str, body: str) -> str:
    p = tmp_path / name
    p.write_text(FM + body, encoding="utf-8")
    return str(p)


def test_citations_group_by_document_and_deduplicate_pages(tmp_path):
    """Six citations of one document are ONE document with THREE distinct page references.

    That distinction is the whole reason the check is affordable: 6,530 citations in the two corpora
    are 133 documents and 987 page references, so the cache turns 6,530 requests into 133.
    """
    a = _artifact(tmp_path, "a.md",
                  "Revenue $1B https://agentii.ai/v/AMZN/sec131/23 and $2B https://agentii.ai/v/AMZN/sec131/23.\n"
                  "Capex $3B https://agentii.ai/v/AMZN/sec131/page24 and $4B https://agentii.ai/v/AMZN/sec131/25.\n"
                  "Again https://agentii.ai/v/AMZN/sec131/25 and https://agentii.ai/v/AMZN/sec131/23.\n")
    got = res.citations_in([a])
    assert got == {("AMZN", "sec131"): {"23", "24", "25"}}, got


def test_both_link_forms_land_in_the_same_group(tmp_path):
    """`/{N}` and `/page{N}` are the same citation written two ways, and the corpus uses both."""
    a = _artifact(tmp_path, "a.md",
                  "A https://agentii.ai/v/ISRG/sec166/77 and B https://agentii.ai/v/ISRG/sec166/page77.\n")
    got = res.citations_in([a])
    assert got == {("ISRG", "sec166"): {"77"}}, got


def test_the_frontmatter_machine_list_is_not_counted(tmp_path):
    """The pins block's own `citations:` list is not a citation in the prose — and an artifact whose
    ONLY citations are there is the red case the density rule exists for."""
    p = tmp_path / "a.md"
    # The list goes INSIDE the frontmatter block — the first version of this fixture put it after the
    # closing `---`, which made it body text, so the URL was (correctly) counted and the test failed
    # against working code. The fixture was the defect.
    p.write_text("---\nas_of: 2026-09-01\n"
                 'citations:\n  - {url: "https://agentii.ai/v/AMZN/sec131/23"}\n---\n\n'
                 "No inline citations in this body at all.\n", encoding="utf-8")
    assert res.citations_in([str(p)]) == {}, "the frontmatter list must not count as a citation"
