# thesis.md — the thesis's two files, and who may write each

> **This contract exists because the file it describes had none, and two writers
> disagreed about what it was.** `thesis.md` was scaffolded as markdown by
> `agentii.specify` and written as JSON by `reduce_journals` — through the write
> boundary on one side and around it on the other. The boundary's second-writer
> refusal, built for exactly this, never saw the second write: the scaffold declared
> no `writer:`, so the file read as append-only and the reducer's write was refused as
> `refuse-append-only` — **blocking** — leaving the file at its scaffold. The reducer
> discarded the `Result` and printed `REDUCED N entries → <path>` anyway.
>
> Nothing raised. Measured across the two live workspaces before the fix: **24 of 26
> `thesis.md` were `# H1` + a fenced ```` ```yaml ```` block**, a shape no reader in
> the kit can read, and every reader returned empty for all of them — so `converge`
> reported `{"status": "converged", "findings": 0}` and an empty portfolio was
> indistinguishable from "no positions". Earlier still, before the boundary was wired,
> commit `cdc5ce3` **overwrote** a thesis's prose with a 526-byte empty reduce, which
> was then copied byte-identically into a snapshot.

## The two files

| Path | Format | Writer | Read by |
|---|---|---|---|
| `theses/{nnn}-{slug}/thesis.md` | prose, `---` frontmatter **at byte 0**, `writer:` **required** | `agentii.specify` | humans; `g1_gate.parse_frontmatter`; `thesis_status` |
| `theses/{nnn}-{slug}/thesis.reduce.json` | JSON object, top-level `"writer"` | `reduce_journals` | `dispatch`, `converge`, `portfolio_aggregate`, `thesis_status` |

**Why two files and not one.** `g1_gate.parse_frontmatter` requires the text to begin
with `---` at byte 0; `json.loads` requires it to begin with `{`. No document is both,
and no reader has a fallback — so a single file can satisfy one family of readers or
the other, never both. `thesis_status.scan_workspace` is the proof: it needs
frontmatter for the pins and JSON for `pending_review`, and each shape populated
exactly half its row.

## Rules

| # | Rule | Enforced by |
|:---:|---|---|
| 1 | `thesis.md` **MUST** begin with `---` at byte 0 and declare `writer:` | `write_boundary.second_writer_verdict` |
| 2 | `thesis.md` **MUST NOT** be JSON | `check_thesis_shape` (check.py) |
| 3 | `thesis.reduce.json` **MUST** declare its `writer` as a top-level key | `write_boundary.declared_writer` |
| 4 | A writer **MUST** declare itself in the document it writes | `write_boundary` — absent ⇒ append-only |
| 5 | A pin whose value is not yet known is **ABSENT**, never a placeholder | `g1_gate.check_frontmatter` |
| 6 | Readers **MUST** distinguish "no machine state" from "empty machine state" | `thesis_doc.read_machine` returns `source` |

> **Rule 4 is the one that failed, in both directions.** `writer:` is not decoration:
> the boundary refuses a write to a document declaring a *different* writer, and treats
> an *undeclared* document as append-only. So omitting the field does not mean "anyone
> may write it" — it means "**nobody may rewrite it**", silently. The scaffold omitted
> it, the reducer could not then write, and the failure was reported as success.
>
> Two carriers, one field: markdown declares `writer:` in frontmatter; **JSON cannot
> contain `---` at all**, so it declares the same thing as a top-level `"writer"` key.
> `declared_writer` reads both. Reading only the frontmatter form meant a JSON file
> declared nothing — so a JSON writer's own *second* write was refused as well, and
> splitting into a JSON file would have reproduced the whole defect on a new path.

> **Rule 5 is Q105's vacancy in a pin.** `check_frontmatter` tests `if not fm.get(pin)`,
> so a truthy placeholder **passes** while pinning nothing. `corpus_version: [TBD]` would
> satisfy every check and mean nothing, which is worse than an absent field — the field
> is present, so nobody looks for it again.

## Frontmatter fields

| field | at scaffold | notes |
|---|---|---|
| `writer` | `agentii.specify` | rule 1 |
| `mode` | `thesis` | required by `g1_gate.check_frontmatter` |
| `thesis_id` | `{nnn}-{slug}` | |
| `claim` | `""` | empty until the human states it — **not** `[TBD]`, see rule 5 |
| `pillars` | `[]` | the spec schema wants `minItems: 1`; a fresh scaffold is deliberately schema-incomplete, and pillar population is the G1/promotion moment |
| `known-open` | `[]` | |
| `depends_on` | `[]` | cross-thesis dependency propagation |
| `as_of` | today | set at scaffold — a thesis is as-of the day it was specified |
| `constitution_pin` | from `constitution.md` | set at scaffold; warn if it still ends `-unratified`, because `reduce_journals.check_aggregate` hard-fails artifacts pinned to it |
| `assumption_pin` | from `assumptions.yaml` | set at scaffold |
| `corpus_version` | **absent** | nothing has been retrieved yet |
| `skill_pin` | **absent** | per-skill hashes live in `skill_pins.jsonl`; duplicating them here would create a second source that drifts |

## The reduce document

```json
{
  "writer": "reduce_journals",
  "reduced_at": "<ISO 8601>",
  "mechanical": { "entry_count": 0, "by_skill": {}, "known_open": [],
                  "subscription_freshness": {}, "verdict_rollup": {},
                  "price_freshness": {"fresh": true, "quote_observed_at": null,
                                      "stale_price": false} },
  "judgment": { "conviction": null, "claims": [], "wrong_if": [] }
}
```

Every reader reads `judgment`; **nothing reads `mechanical` or `reduced_at`.** The
module docstring presents `mechanical` as step ① that judgment must rest on, and it is
written to disk and never consumed. That is recorded rather than silently tolerated:
a block that exists for a reader that does not exist yet is a claim, not a feature.

## Relationship to `thesis-frontmatter.schema.json`

`specs/046-agentii-research-orchestration/contracts/thesis-frontmatter.schema.json`
(located **outside this repository**) declares `judgment` — and the five pins — as
properties of `thesis.md`'s frontmatter. **This contract supersedes that placement for
`judgment`**, and the reason is mechanical rather than a preference:

A machine write of `judgment` into `thesis.md` would mean rewriting the whole document
through `yaml.safe_load` → `yaml.dump`, and **a YAML round-trip does not preserve the
real files' inline comments or key order.** The two migrated theses carry both. Placing
machine state in its own file leaves the human's file byte-stable under machine writes,
which is what makes rule 2 checkable at all.

The schema's `claim` and `pillars` requirements **do** apply — to `thesis.md`, as
frontmatter fields. Note that nothing currently reads them; they are read by the
schema only.

## The legacy read path

A `thesis.md` that parses as a JSON object is still read, as `source == "legacy"`, so
workspaces written before the split keep working. **No writer may produce that form** —
it exists to be read and retired, not to be written.

`thesis_doc.read_machine(path) -> (doc, source)` with `source ∈ {reduce, legacy, none}`
is the single reader. Precedence: the reduce file, then a legacy JSON `thesis.md`, then
nothing. It never raises — but it does **not** hide which case occurred, because
`source == "none"` reported as an empty result is exactly the silence that kept this
defect alive for as long as it lived.

## Migration

`scripts/migrate_thesis_reduce.py` classifies each thesis (`reduce` / `legacy-json` /
`fenced-yaml` / `frontmatter`) and converts it, dry-run by default. It is **off the
critical path**: `read_machine` reads the legacy shapes, so an unmigrated workspace
still works. It exists for the frontmatter readers, which cannot see a fenced block.
