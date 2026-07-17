"""T054 — tests for data-tools/setup_credentials.py.

--check detects missing vars non-interactively; .env write to a temp dir; secrets
never echoed/logged.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD = REPO_ROOT / "data-tools" / "setup_credentials.py"


def _load():
    spec = importlib.util.spec_from_file_location("setup_credentials", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_module_exists():
    assert MOD.is_file()


def test_check_reports_missing(monkeypatch):
    m = _load()
    monkeypatch.delenv("FRED_API_KEY", raising=False)
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    report = m.check_credentials()
    assert "FRED_API_KEY" in report["missing"]
    assert report["missing"]  # non-empty


def test_check_detects_present(monkeypatch):
    m = _load()
    monkeypatch.setenv("FRED_API_KEY", "sk_test")
    report = m.check_credentials()
    assert "FRED_API_KEY" not in report["missing"]
    assert "FRED_API_KEY" in report["present"]


def test_write_env_file(tmp_path):
    m = _load()
    env_path = tmp_path / ".env"
    m.write_env({"FRED_API_KEY": "sk_abc", "FMP_API_KEY": "sk_def"}, path=env_path)
    text = env_path.read_text()
    assert "FRED_API_KEY=sk_abc" in text
    assert "FMP_API_KEY=sk_def" in text


def test_write_env_preserves_existing(tmp_path):
    m = _load()
    env_path = tmp_path / ".env"
    env_path.write_text("EXISTING=1\nFRED_API_KEY=old\n")
    m.write_env({"FRED_API_KEY": "new"}, path=env_path)
    text = env_path.read_text()
    assert "EXISTING=1" in text
    assert "FRED_API_KEY=new" in text
    assert "FRED_API_KEY=old" not in text  # updated, not duplicated


def test_cli_check_non_interactive_no_secret_leak(tmp_path, monkeypatch):
    monkeypatch.setenv("FRED_API_KEY", "sk_super_secret_value")
    res = subprocess.run(
        [sys.executable, str(MOD), "--check", "--json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert res.returncode in (0, 1)
    # secret value must never be printed
    assert "sk_super_secret_value" not in res.stdout
    assert "sk_super_secret_value" not in res.stderr
    payload = json.loads(res.stdout)
    assert "present" in payload and "missing" in payload
