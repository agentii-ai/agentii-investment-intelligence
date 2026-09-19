# agentii.md — [WORKSPACE_NAME]

> **This file is the WORKSPACE'S CONSTITUTION.** It is scaffolded into a workspace
> that has no `constitution.md`, and in that workspace it **is** the governing
> instrument — not a chronicle, not a memory index, not a log.
>
> **Q140's rule, stated where it is needed**: `constitution.md` decides which role
> `agentii.md` plays. Present ⇒ `agentii.md` is a chronicle and Q81's rotation
> applies to it. Absent ⇒ **`agentii.md` IS the constitution**, and **Q81 rules 1
> and 2 do NOT apply** — rotating it would rotate the project's principles away.
> The rationale Q81 gave for rotation ("dropping an old shard loses no truth")
> is exactly the premise that fails here: for a chronicle it is true, and for a
> constitution it is destructive.
>
> **Do not add `constitution.md` to this workspace without reading
> `scripts/reconcile_instruments.py` first.** The migration `agentii.md` →
> `constitution.md` is one-way, and any principle this file carries that the new
> constitution does not absorb is **lost**. Use the reconciler; it reports what
> would be dropped.

**RATIFICATION**: replace every `[BRACKETED]` placeholder below. `agentii.specify`
refuses a workspace whose governing instrument still contains one — the refusal is
structural, not advisory (Q83).

---

## 1. Research Scope

**Workspace**: [WORKSPACE_NAME]
**Scope**: [WHAT THIS WORKSPACE COVERS — the asset class, sector, or question set]
**Out of scope**: [WHAT IT DELIBERATELY DOES NOT COVER]

## 2. Principles

Each principle gets an id, and every id used elsewhere in this workspace must
resolve to one of these. A principle cited but not defined here is
`UNFRAMED_REFERENCE` — the same failure the constitution template's Principle
Register guards against, and it exists here for the same reason: a document that
cites its own principles by number needs the numbers to be a closed set.

| id | principle | what violating it looks like |
|----|-----------|------------------------------|
| P1 | [PRINCIPLE] | [THE OBSERVABLE FAILURE] |
| P2 | [PRINCIPLE] | [THE OBSERVABLE FAILURE] |

## 3. Evidence Discipline

- Every material claim traces to a source, cited inline. A number without a
  source is an error, not an estimate.
- Claims are classified `FACT` / `DEDUCTED` / `VIEW`, as a **field** on each claim
  (`claim_class`), not as prose the reader has to interpret.
- [ANY WORKSPACE-SPECIFIC RULE — a data source you accept or refuse, a definition
  you hold to, a period convention]

## 4. Output Contract

This workspace runs in **single-skill mode**: a skill is invoked directly against
agentii.ai data, with no thesis. The early instrument set therefore applies, and
none of it is replaced by `artifacts/` — that substitution happens **only in
thesis mode**.

| instrument | purpose | path |
|---|---|---|
| raw deliverable | the skill's full per-run output | `{ticker}/YYYY-MM-DD_HHMM_{skill}_{affix}.md` |
| snapshot | point-in-time memory, restored on session start | `snapshots/{ticker}/{YYYY-MM-DD}_{semantic-slug}.md` |
| session | the run transcript, read on demand | `sessions/{YYYY-MM-DD}/{HHMM}_{session_id}.jsonl` |
| session index | the auto-loaded catalog of runs | `sessions/INDEX.md` |
| formatting | currency, percentage and table conventions | `style.md` |

**Snapshot key is `{ticker}`, in this mode and in thesis mode both** (Q144). A
ticker always exists; a thesis id does not. Thesis attribution, where it applies,
lives in the snapshot's **frontmatter**, never in its path.

**Disclaimers.** Any presentation-shaped output this workspace produces
(`thesis-report.html`, `dashboard.html`, `pitch-deck`, `earnings-preview`) carries
the canonical block from
`plugins/vertical-plugins/scenarios/templates/disclaimer.md` — verbatim, from the
source, with its placeholders filled. It is never restated, paraphrased or forked.

## 5. Amendment

Amend by editing this file directly, and record the change in the log below. There
is no `constitution amend` for this instrument: that command amends
`constitution.md`, and running it here would create the second instrument whose
existence changes this file's role (see the warning at the top).

| date | change | why |
|------|--------|-----|
| [YYYY-MM-DD] | [WHAT CHANGED] | [WHAT FORCED IT] |
