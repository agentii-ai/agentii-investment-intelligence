"""Spec 055 permanent audits (T047): MS-copyright boundary, coverage_gap honesty,
sector scope. These run on every CI — the one-off audits made permanent."""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BIO_PHARM = ROOT / "plugins" / "vertical-plugins" / "bio-pharm" / "skills" / "agentii"

FORBIDDEN_MARKERS = [
    "Morgan Stanley",               # copyright boundary (spec FR-A02, SC-007)
    "A picture is worth a thousand words",  # corpus title — never in skills
    "IQVIA panel data available",   # licensed panels never assumed (FR-B02)
]
EXCLUDED_SECTORS = ["med.healthcare_services", "med.life_sciences_tools"]


def _skill_dirs():
    return sorted(p for p in BIO_PHARM.iterdir() if p.is_dir())


def _frontmatter(skill: Path) -> dict:
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---"), f"{skill.name}: missing frontmatter"
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm) or {}


def test_no_ms_corpus_text_in_bio_pharm_skills():
    """FR-A02 / SC-007: the Morgan Stanley corpora are methodology references
    only — zero corpus text may appear in any skill file."""
    offenders: list[str] = []
    for skill in _skill_dirs():
        for f in skill.rglob("*"):
            if f.suffix not in (".md", ".yaml"):
                continue
            text = f.read_text(encoding="utf-8", errors="replace")
            for marker in FORBIDDEN_MARKERS:
                if marker.lower() in text.lower():
                    offenders.append(f"{f.relative_to(ROOT)}: {marker!r}")
    assert offenders == [], f"copyright boundary violated: {offenders}"


def test_coverage_gap_honesty_in_every_055_skill():
    """SC-005: every skill declares the coverage_gap path — no silent
    substitution when its data surface is absent."""
    for skill in _skill_dirs():
        body = (skill / "SKILL.md").read_text(encoding="utf-8")
        assert "coverage_gap" in body, f"{skill.name}: missing coverage_gap discipline"


def test_sector_scope_excludes_hc_services_and_life_sciences_tools():
    """SC-006: the vertical is medicines_biotech + medical_devices only
    (user scope — healthcare_services / life_sciences_tools excluded)."""
    for skill in _skill_dirs():
        sectors = _frontmatter(skill).get("sectors") or []
        assert sectors, f"{skill.name}: no sectors declared"
        for excluded in EXCLUDED_SECTORS:
            assert excluded not in sectors, f"{skill.name}: {excluded} in sectors"
        for s in sectors:
            assert s in ("med.medicines_biotech", "med.medical_devices"), \
                f"{skill.name}: unexpected sector {s}"
