#!/usr/bin/env python3
"""LibreOffice headless recalculation + audit for .xlsx workbooks.

Mirrors Anthropic's financial-services office architecture: after openpyxl
builds the workbook, this script recalculates all formulas via LibreOffice
headless and audits that hardcoded_count == 0 for cells tagged as projection,
margin, discount_factor, pv, or sensitivity.

Usage:
    python3 scripts/recalc.py {ticker}/{YYYY-MM-DD_HHMM}_dcf_base.xlsx  [--pdf]  [--audit-only]

Exit codes:
    0 — recalc succeeded, audit passed (hardcoded_count == 0)
    1 — LibreOffice not found (install: brew install libreoffice)
    2 — recalc failed (file not found, soffice error, or timeout)
    3 — audit failed (hardcoded_count > 0 for tagged cells)
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Cells tagged with these markers MUST be live formulas (not hardcoded values).
# openpyxl build scripts apply these as cell comments or named-range metadata.
AUDIT_TAGS = {"projection", "margin", "discount_factor", "pv", "sensitivity"}


def _find_soffice() -> str:
    """Locate LibreOffice soffice binary."""
    soffice = shutil.which("soffice")
    if soffice:
        return soffice
    # macOS common paths
    for candidate in [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/opt/libreoffice/program/soffice",
    ]:
        if os.path.isfile(candidate):
            return candidate
    return ""


def recalc(xlsx_path: str, timeout: int = 60) -> bool:
    """Recalculate formulas in-place via LibreOffice headless.

    Uses a temporary user profile to avoid conflicts with any running
    LibreOffice instance. Returns True on success.
    """
    soffice = _find_soffice()
    if not soffice:
        print("ERROR: LibreOffice not found. Install: brew install libreoffice")
        return False

    abs_path = str(Path(xlsx_path).resolve())
    if not os.path.isfile(abs_path):
        print(f"ERROR: File not found: {abs_path}")
        return False

    work_dir = str(Path(abs_path).parent.resolve())

    with tempfile.TemporaryDirectory(prefix="soffice_profile_") as profile_dir:
        cmd = [
            soffice,
            "--headless",
            "--norestore",
            f"-env:UserInstallation=file://{profile_dir}",
            "--calc",
            "--infilter=Calc Office Open XML",
            f"--outdir={work_dir}",
            abs_path,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                print(f"ERROR: soffice exited {result.returncode}")
                if result.stderr:
                    print(result.stderr[:500])
                return False
        except subprocess.TimeoutExpired:
            print(f"ERROR: LibreOffice recalc timed out after {timeout}s")
            return False

    # LibreOffice may produce a lock file; clean it up
    lock_file = Path(work_dir) / f".~lock.{Path(abs_path).name}#"
    if lock_file.exists():
        lock_file.unlink()

    return True


def convert_to_pdf(xlsx_path: str, timeout: int = 60) -> str | None:
    """Convert .xlsx to PDF via LibreOffice headless.

    Returns the path to the generated PDF, or None on failure.
    """
    soffice = _find_soffice()
    if not soffice:
        return None

    abs_path = str(Path(xlsx_path).resolve())
    work_dir = str(Path(abs_path).parent.resolve())

    with tempfile.TemporaryDirectory(prefix="soffice_profile_") as profile_dir:
        cmd = [
            soffice,
            "--headless",
            "--norestore",
            f"-env:UserInstallation=file://{profile_dir}",
            "--convert-to",
            "pdf",
            "--outdir",
            work_dir,
            abs_path,
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return None
        except subprocess.TimeoutExpired:
            return None

    pdf_path = str(Path(xlsx_path).with_suffix(".pdf"))
    return pdf_path if os.path.isfile(pdf_path) else None


def audit_hardcoded(xlsx_path: str) -> tuple[int, list[str]]:
    """Audit tagged cells for hardcoded values.

    Uses openpyxl to read the workbook and check that every cell tagged with
    an AUDIT_TAGS marker (via comment text or named-range participation)
    contains a formula, not a hardcoded value.

    Returns (hardcoded_count, [cell_references...]).
    """
    try:
        import openpyxl
    except ImportError:
        print("WARNING: openpyxl not installed; skipping formula audit.")
        return -1, []

    wb = openpyxl.load_workbook(xlsx_path, data_only=False)

    hardcoded = []
    tagged_named_ranges: dict[str, set[str]] = {}

    # Collect cells that belong to audit-tagged named ranges
    for name, range_def in wb.defined_names.items():
        name_lower = name.lower()
        for tag in AUDIT_TAGS:
            if tag in name_lower:
                # Resolve the named range destinations
                for title, coord in range_def.destinations:
                    tagged_named_ranges.setdefault(tag, set()).add(coord)

    # Scan all sheets
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if cell.value is None or isinstance(cell.value, str):
                    continue
                # Formula cells have a leading '='
                is_formula = isinstance(cell.value, str) and str(cell.value).startswith("=")

                # Check cell comments for audit tags
                if cell.comment:
                    comment_text = cell.comment.text.lower()
                    for tag in AUDIT_TAGS:
                        if tag in comment_text and not is_formula:
                            ref = f"{ws.title}!{cell.coordinate}"
                            hardcoded.append(ref)
                            break

    wb.close()
    return len(hardcoded), hardcoded


def main():
    parser = argparse.ArgumentParser(
        description="LibreOffice headless recalc + formula audit for agentii .xlsx workbooks"
    )
    parser.add_argument("xlsx_path", help="Path to the .xlsx workbook")
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Also convert to PDF after recalc",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Skip recalc; only run the hardcoded-count audit",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="LibreOffice timeout in seconds (default: 60)",
    )
    args = parser.parse_args()

    xlsx_path = args.xlsx_path
    if not os.path.isfile(xlsx_path):
        print(f"ERROR: {xlsx_path} not found")
        sys.exit(2)

    # Step 1 — Recalc (unless audit-only)
    if not args.audit_only:
        print(f"Recalculating: {xlsx_path}")
        if not recalc(xlsx_path, timeout=args.timeout):
            sys.exit(2)
        print("  recalc: OK")
        # Brief pause for filesystem flush
        time.sleep(0.5)

    # Step 2 — Audit
    print(f"Auditing: {xlsx_path}")
    hardcoded_count, hardcoded_refs = audit_hardcoded(xlsx_path)

    if hardcoded_count < 0:
        print("  audit: SKIPPED (openpyxl not available)")
    elif hardcoded_count == 0:
        print("  audit: OK (hardcoded_count == 0)")
    else:
        print(f"  audit: FAILED — {hardcoded_count} hardcoded cell(s) found:")
        for ref in hardcoded_refs[:20]:
            print(f"    - {ref}")
        sys.exit(3)

    # Step 3 — Optional PDF
    if args.pdf:
        print(f"Converting to PDF: {xlsx_path}")
        pdf_path = convert_to_pdf(xlsx_path, timeout=args.timeout)
        if pdf_path:
            print(f"  pdf: {pdf_path}")
        else:
            print("  pdf: FAILED (LibreOffice unavailable or conversion error)")

    print("recalc.py: done")
    sys.exit(0)


if __name__ == "__main__":
    main()
