# Slug Rules for `## Mode: <slug>` headings (v1.0 frozen)

Deterministic slugification algorithm used by `scripts/port-dimension-prompts.py` to convert source sub-prompt YAML filenames (or `name:` fields) into mode slugs. Per **** + Round 4 Q12.

## Algorithm

For each sub-prompt YAML at `references/prompts/<dim>/<filename>.yaml`:

1. **If YAML declares a `name:` field at top-level OR under `metadata.description`**, use that as the semantic name; otherwise compute from filename.
2. **From filename (fallback path)**:
 - Strip `.yaml` extension.
 - Strip `_optimized` suffix if present (the optimized version supersedes the bare version per FR-106).
 - Strip leading `<dim>_` prefix (e.g., `1_1` → `1`, `2_1_3` → `1_3`).
3. **Normalize** the chosen string:
 - Lowercase all ASCII letters.
 - Replace any run of `[^a-z0-9]+` with a single `-`.
 - Strip leading and trailing `-`.
4. **Prepend dimension prefix** (optional, for human readability): the slug body is enough; the parent `## Mode:` heading provides dimension context.
5. **Reserved keyword check**: if the resulting slug equals `all`, FAIL with `AGENTII_PORT_RESERVED_SLUG` (the `--mode=all` keyword cannot collide with a real mode slug).

## Examples

| Source path | YAML `name:` field | Computed slug |
|---|---|---|
| `references/prompts/1/1_1.yaml` | `Business Model & Offerings Analysis` | `business-model-and-offerings-analysis` |
| `references/prompts/2/2_1_1.yaml` | (no name field) | `1-1` (from `2_1_1` → strip `2_` → `1_1` → `1-1`) |
| `references/prompts/4/4_1_optimized.yaml` | (under `metadata.description`) | `technology-trend-exposure-evaluation` |
| `references/prompts/4/4_2_3_optimized.yaml` | `name: Capital Allocation Analysis` | `capital-allocation-analysis` |
| `references/prompts/7/7_3_1.yaml` | (no name) | `3-1` |
| `references/prompts/8/8_1_1.yaml` | (no name) | `1-1` |

## Conflict resolution

If two YAMLs in the same dim resolve to the same slug after the algorithm:

- **Same-dim collision** → FAIL with `AGENTII_PORT_SLUG_COLLISION` and emit the conflicting pair. The analyst MUST disambiguate by adding distinct `name:` fields.
- **Cross-dim collision** → ALLOWED. Mode slugs are addressed within their parent dimension's command namespace (`/agentii:dim-2 NVDA --mode=peer-overview` vs `/agentii:dim-3 NVDA --mode=peer-overview` may coexist).

## `_optimized` precedence rule

When `<filename>.yaml` AND `<filename>_optimized.yaml` both exist (dim-4 has only `_optimized`; other dims may grow this pattern over time):

- The `_optimized` version is emitted; the bare version is dropped.
- A marker file `.optimized-superseded.yaml` MUST exist in the dim dir listing the superseded bare filenames; otherwise the port script FAILS with `AGENTII_PORT_AMBIGUOUS_VERSION`.

## Validation

`scripts/validate-mode-syntax.py`  re-runs this algorithm against every SKILL.md and verifies the emitted `## Mode:` headings match. Drift between this contract and the port script's behavior raises `AGENTII_PORT_SLUG_DRIFT` in CI.

## Reserved slugs (v1.0)

| Slug | Reason |
|---|---|
| `all` | `--mode=all` keyword  — runs every mode of the dimension |
| `essentials` | implicit default when no `--mode=` flag is provided; resolves to skill's `essentials_modes` list |

A real mode whose name slugifies to either reserved keyword MUST be renamed by the analyst before the port runs.
