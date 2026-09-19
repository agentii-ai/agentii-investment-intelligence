"""T025/T026 — the walking skeleton must walk: one gated artifact, end to end.

Chain (plan S1): ratify minimal L1 → mkdir-CAS thesis → one task → dispatch with
explicit thesis_dir → data-layer refusal demonstrated (DATA_STALE) → artifact with
5 pins + observed_at → G1 passes → journal shard → reduction → atomic thesis.reduce.json.

Plus the concurrency negative test: 8 parallel subagents' journal appends must not
corrupt (Q4 item 3 — the reason shards exist).
"""
from __future__ import annotations

import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "data-tools"))

import alloc_thesis_id  # noqa: E402
import g1_gate  # noqa: E402
import journal  # noqa: E402
import market_data  # noqa: E402
import reduce_journals  # noqa: E402

FAKE_OK = {"fake": lambda t: {
    "symbol": t, "price": 230.0, "market_cap": 5562502934738,
    "observed_at": "2026-09-08T16:00:00-04:00", "price_basis": "close",
    "data_class": "fast"}}
FAKE_NO_OBSERVED_AT = {"fake": lambda t: {"symbol": t, "price": 230.0}}


def test_walking_skeleton_end_to_end(tmp_path):
    # 1. L1 scaffold (templates exist) — ratify minimally with real values.
    templates = ROOT / "plugins" / "vertical-plugins" / "scenarios" / "templates"
    assert (templates / "constitution-template.md").is_file()
    assert (templates / "constitution-template.yaml").is_file()

    # 2. mkdir-CAS thesis allocation.
    thesis = alloc_thesis_id.allocate(tmp_path / "workspace" / "theses", "mvp")
    assert thesis.name == "001-mvp"

    # 3. One task: NVDA × recent-quarter × default.
    task_line = "- [ ] T001 [S1] NVDA × recent-quarter × default (src: Q30/Q79)"
    (thesis / "tasks.md").write_text(f"# tasks\n{task_line}\n")
    assert "NVDA × recent-quarter × default" in (thesis / "tasks.md").read_text()

    # 4. Dispatch with explicit thesis_dir (refusal without it is T026's test).
    import dispatch
    import subprocess
    import sys as _sys
    env_ok = subprocess.run(
        [_sys.executable, str(ROOT / "scripts" / "dispatch.py"),
         "--thesis-dir", str(thesis), "--task", "NVDA recent-quarter default",
         "--journal", str(thesis / "shards" / "run1.ndjson")],
        capture_output=True, text=True)
    assert env_ok.returncode == 0, env_ok.stderr
    assert "thesis_dir=" in env_ok.stdout

    # 5. Data-layer refusal demonstrated: the un-pinnable quote is refused.
    refused = market_data.get_quote("NVDA", providers=FAKE_NO_OBSERVED_AT,
                                    cache_root=tmp_path / "cache")
    assert refused["status"] == "error"
    assert refused["error"].startswith("DATA_STALE")
    # ... and the pinnable quote flows.
    good = market_data.get_quote("NVDA", providers=FAKE_OK, cache_root=tmp_path / "cache")
    assert good["data"]["observed_at"].startswith("2026-09-08")

    # 6. Artifact with 5 pins + observed_at → G1 passes.
    artifact = thesis / "artifacts" / "NVDA" / "2026-09-08_recent-quarter_default.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(f"""---
assumption_pin: 1
corpus_version: "2026-08"
as_of: 2026-09-08
constitution_pin: 0.1.0
skill_pin: "recent-quarter:abc123"
mode: default
data_class: slow
entity_claims:
  - entity: NVDA
    metric: gross_margin
    value: 73.0
    unit: pct
    period: 2026Q2
    source: "xbrl:us-gaap:GrossProfit/Revenues"
    retrieved_at: 2026-09-08T09:12:00-04:00
    observed_at: 2026-09-08T16:00:00-04:00
---

# NVDA recent-quarter analysis
""")
    assert g1_gate.check_artifact(artifact) == []
    # ... and a pin-dropped artifact fails.
    bad = artifact.with_name("bad.md")
    bad.write_text(artifact.read_text().replace("skill_pin:", "removed:"))
    assert g1_gate.check_artifact(bad)

    # 7. Journal shard → reduction → atomic thesis.reduce.json.
    journal.append_entry(thesis / "shards" / "run1.ndjson",
                         journal.make_entry("recent-quarter", "NVDA", "default",
                                            "001-mvp", ["get_realtime_quote"],
                                            observed_at="2026-09-08T16:00:00-04:00"))
    doc = reduce_journals.reduce(thesis / "shards", thesis / "thesis.md")
    # D75 #5: dispatch journals EVERY dispatch (explicit path included) — the
    # reducer therefore sees the dispatch record + the skill entry.
    assert doc["mechanical"]["entry_count"] == 2
    # The reduce lands in thesis.reduce.json — thesis.md is the human's prose file.
    reduce_file = thesis / "thesis.reduce.json"
    assert reduce_file.is_file()
    assert reduce_file.read_text(encoding="utf-8").startswith("{")
    assert not (thesis / "thesis.reduce.json.tmp").exists()

    # The slice's demonstrable result: one gated artifact under refusal-enforced
    # correctness, reduced into an atomically written thesis.reduce.json.
    assert artifact.is_file()
    assert reduce_file.read_text(encoding="utf-8").startswith("{")


def test_8_parallel_journal_appends_do_not_corrupt(tmp_path):
    shard_dir = tmp_path / "shards"
    shard_dir.mkdir()
    shards = [shard_dir / f"agent{i}.ndjson" for i in range(8)]

    def write_many(i: int):
        for n in range(25):
            journal.append_entry(shards[i],
                                 journal.make_entry("recent-quarter", "NVDA",
                                                    "default", "001-mvp", []))

    threads = [threading.Thread(target=write_many, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = sum(len(journal.read_shard(s)) for s in shards)
    assert total == 200, "interleaved appends lost or corrupted entries"
