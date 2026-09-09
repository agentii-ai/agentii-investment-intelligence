#!/usr/bin/env python3
"""alloc_thesis_id.py — {nnn}-{slug} allocation via mkdir-as-CAS (spec 046 Q27).

POSIX mkdir is atomic: the directory creation itself is the lock. EEXIST means
someone else took the number — increment and retry. Never `exist_ok=True`: that
swallows EEXIST and silently degrades the CAS into directory sharing — the most
likely implementation bug of this design (Q27).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ID_RE = re.compile(r"^(\d{3})-")


def scan_highest(theses_dir: Path) -> int:
    highest = 0
    if not theses_dir.is_dir():
        return highest
    for child in theses_dir.iterdir():
        m = _ID_RE.match(child.name)
        if m:
            highest = max(highest, int(m.group(1)))
    return highest


def allocate(theses_dir: Path, slug: str) -> Path:
    """Create theses/{nnn}-{slug}/ atomically. Returns the created path."""
    theses_dir.mkdir(parents=True, exist_ok=True)  # container, not the CAS itself
    while True:
        n = scan_highest(theses_dir) + 1
        target = theses_dir / f"{n:03d}-{slug}"
        try:
            target.mkdir()  # atomic; EEXIST = someone else already took this number
            return target
        except FileExistsError:
            continue  # no sleep, no lock — rescan and retry


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Allocate theses/{nnn}-{slug}/ via mkdir-CAS (Q27)")
    p.add_argument("--theses-dir", required=True)
    p.add_argument("--slug", required=True)
    args = p.parse_args(argv)
    path = allocate(Path(args.theses_dir), args.slug)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
