"""Spec 039 pytest configuration and shared fixtures.

- Adds `--run-live` opt-in flag; `live`-marked tests are skipped unless it is passed.
- Provides fixture-loading helpers for the key-free, deterministic data-tools suite.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run @pytest.mark.live tests against real external endpoints (needs API-key secrets).",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        return
    skip_live = pytest.mark.skip(reason="live test: pass --run-live (and set API-key secrets) to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def load_fixture():
    """Return a loader for recorded JSON fixtures under tests/fixtures/.

    Usage: `data = load_fixture("tools/fred_gdp.json")`.
    """

    def _load(rel_path: str):
        path = FIXTURES_DIR / rel_path
        return json.loads(path.read_text(encoding="utf-8"))

    return _load
