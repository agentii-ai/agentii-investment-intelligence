"""L0: the environment contract for the market-data path.

The provider adapter is import-guarded, so a missing or mismatched yfinance does
not raise — it silently removes the only implemented provider and every price
lookup becomes SOURCE_UNAVAILABLE. These tests make that state visible instead.

Pins and installed versions have already diverged: `requirements-tools.txt` pins
yfinance==0.2.65 while this machine's venv carries 1.7.0, a major-version gap.
The adapter's field extraction was written and "verified" against a different
version than the one running (see D2).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "data-tools"))
import market_data  # noqa: E402


def _pinned_version(package: str) -> str | None:
    path = REPO_ROOT / "requirements-tools.txt"
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(rf"^{re.escape(package)}==([\w.]+)", line.strip())
        if match:
            return match.group(1)
    return None


def _installed_version(package: str) -> str | None:
    try:
        module = __import__(package)
    except ImportError:
        return None
    return getattr(module, "__version__", None)


def test_yfinance_is_importable():
    """Without it, `_real_providers()` returns an empty dict and every quote is
    SOURCE_UNAVAILABLE. The failure is silent by design, so assert it loudly here."""
    assert _installed_version("yfinance") is not None, (
        "yfinance is not installed — the only implemented market provider is absent, "
        "so every price lookup degrades to SOURCE_UNAVAILABLE"
    )


def test_real_providers_constructs_both_closures():
    providers = market_data._real_providers()
    assert "yfinance" in providers, "the quote provider must be constructible"
    assert "yfinance_history" in providers, "the history provider must be constructible"


@pytest.mark.xfail(strict=False, reason=(
    "D-drift: requirements-tools.txt pins yfinance==0.2.65 but this environment "
    "runs 1.7.0 — the adapter's FastInfo field names were verified against a "
    "different major version than the one executing. Environmental: XPASS means "
    "the pin and the runtime agree."))
def test_installed_yfinance_matches_the_declared_pin():
    pinned = _pinned_version("yfinance")
    if pinned is None:
        pytest.skip("no yfinance pin declared")
    installed = _installed_version("yfinance")
    if installed is None:
        pytest.skip("yfinance not installed")

    assert installed == pinned, (
        f"requirements-tools.txt pins yfinance=={pinned} but {installed} is "
        f"installed; the T076 field extraction was validated against the pinned "
        f"version's fast_info key set"
    )


@pytest.mark.xfail(strict=False, reason=(
    "D2 (environment form): the camelCase names market_data.py reads via getattr() "
    "do not exist on FastInfo. Version-dependent — a yfinance release that adds "
    "__getattr__ would flip this."))
def test_fast_info_key_contract_holds_for_the_installed_version():
    """Pins the D2 root cause as an executable environment fact: for every field
    market_data.py extracts via getattr(), assert whether that attribute actually
    exists on the installed FastInfo.

    `open` and `market_cap` resolve; the camelCase names do not. If a future
    yfinance adds __getattr__ this test flips and tells us the adapter's getattr
    calls became valid — the signal that D2 can be closed differently."""
    try:
        from yfinance.scrapers.quote import FastInfo
    except ImportError:  # pragma: no cover - guarded by the test above
        pytest.skip("yfinance.scrapers.quote.FastInfo not available")

    extracted_via_getattr = [
        "market_cap", "dayHigh", "dayLow", "open",
        "previousClose", "lastVolume", "fiftyDayAverage",
    ]
    resolving = {n for n in extracted_via_getattr if hasattr(FastInfo, n)}
    non_resolving = set(extracted_via_getattr) - resolving

    # The defect, stated as an assertion about the environment:
    assert not non_resolving, (
        f"market_data.py reads these via getattr(info, name, None), but FastInfo "
        f"has no such attribute, so they are ALWAYS None: {sorted(non_resolving)}. "
        f"Only {sorted(resolving)} resolve. FastInfo exposes snake_case properties "
        f"and accepts camelCase only through __getitem__."
    )
