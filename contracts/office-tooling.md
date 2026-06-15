# Office Tooling (canonical code-mode office-output contract)

The agentii MCP surface does **not** expose abstract `xlsx.build` / `pptx.build` /
`pptx.edit` / `pptx.refresh` tools — those belong to a different plugin. Office
files are produced in **code-mode**: the agent writes a self-contained Python
script and runs it via `Bash`, using `openpyxl` (Excel), `python-pptx`
(PowerPoint), and `python-docx` (Word), with **LibreOffice headless** for formula
recalculation and PDF conversion. This mirrors Anthropic's official
`financial-services` office architecture.

When running inside a live Office session (Cowork, `mcp__office__*` tools
present), skills MAY drive the live document instead. The canonical preflight
layered probe is defined in FR-043.

## Excel (`.xlsx`) — `Bash` + Python `openpyxl` + LibreOffice recalc

The agent writes a self-contained Python script from already-retrieved XBRL data,
executes it with `Bash`, recalculates formulas via LibreOffice headless, and
audits the result.

1. Write `_build_{ticker}_{type}.py` using `openpyxl`.
2. Execute: `Bash: python3 _build_{ticker}_{type}.py`.
3. Recalculate: invoke `soffice --headless --norestore --calc --infilter="Calc Office Open XML" --outdir={dir} {path}`. If the package's `scripts/recalc.py` is reachable, use `Bash: python3 scripts/recalc.py {path}` (a convenience wrapper around the soffice call that also runs the hardcoded-count audit).
4. Verify: `Bash: ls -la {ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx` — confirm
   file exists and size > 0.
5. Audit: confirm `hardcoded_count == 0` for cells tagged `projection | margin |
   discount_factor | pv | sensitivity`.

**Conventions** (mirroring Anthropic `xlsx-author`):
- **Blue font** = hardcoded input assumptions
- **Black font** = live formulas
- **Green font** = cross-sheet links
- Named ranges for key metrics
- A `Checks` tab with TRUE/FALSE validation ties (BS balances, CF ties to cash)

**Formulas-over-hardcodes invariant (FR-020)**: every projection / margin /
discount-factor / PV / sensitivity cell MUST be a live formula, never a
Python-computed hardcoded value.

**LibreOffice recalc (`recalc.py`)**: resolves all formulas after build.
`soffice --headless --convert-to pdf` is available for distribution-ready exports.
LibreOffice rendering may differ from Microsoft Office — warn users to review in
the native app.

**Degraded fallback (FR-044)**: only when `python3 -c "import openpyxl"` exits
non-zero. Output a `.md` summary with full data tables, annotate
`data_availability: degraded` and `openpyxl_missing: true`, and report the exact
command `pip install openpyxl` to the user. The `.md` is NOT an acceptable
substitute when openpyxl IS available.

`Bash` MUST appear in the skill's `allowed_tools` whenever this path is used.

## PowerPoint (`.pptx`) — `Bash` + Python `python-pptx` + LibreOffice validation

Primary deliverable is a **real `.pptx` binary** via `Bash` + `python-pptx`:
one idea per slide; every figure footnoted to its source model cell or `/v/`
citation; firm template honored when mounted at `./templates/`; charts embedded
as model-rendered PNGs when fidelity matters.

1. Write `_build_{ticker}_pitch.py` using `python-pptx`.
2. Execute: `Bash: python3 _build_{ticker}_pitch.py`.
3. Verify: `Bash: ls -la {ticker}/{YYYY-MM-DD_HHMM}_pitch-deck_{affix}.pptx` —
   confirm file exists and size > 0.
4. Validate structural integrity (slide count, source footers per skill's
   `## Validation Gates`).

**Degraded fallback (FR-044)**: when `python3 -c "import pptx"` exits non-zero,
produce a polished `.md` slide specification (one slide per section, structured
for pasting into Google Slides / Keynote / Deckset / PowerPoint). Annotate
`data_availability: degraded` and `python_pptx_missing: true`, and report the
exact command `pip install python-pptx` to the user.

LibreOffice provides structural validation and PDF export. Warn that LibreOffice
rendering may differ from Microsoft Office — recommend final review in the
native app.

`Bash` MUST appear in the skill's `allowed_tools` whenever this path is used.

## Word (`.docx`) — `Bash` + Python `python-docx` (available-but-optional at v2.3.1)

`.docx` support is documented as available-but-optional. All skills default to
`.md` at v2.3.1. `.docx` consumption is deferred until a dedicated memo/IC-note
skill ships in the `models-and-pitches` vertical. The contract path is:

1. Write `_build_{ticker}_memo.py` using `python-docx`.
2. Execute: `Bash: python3 _build_{ticker}_memo.py`.
3. Verify: `Bash: ls -la {ticker}/{YYYY-MM-DD_HHMM}_memo_{affix}.docx`.

**Degraded fallback**: when `python3 -c "import docx"` exits non-zero, produce
`.md` with `data_availability: degraded` + `python_docx_missing: true`.

## Shared Verification Rule

After writing any office file, verify the file exists at the expected path and
report its size. **Never report success for a file that was not actually written.**

## Layered Preflight Probe (FR-043)

Office-producing skills run a layered dependency probe before build:

1. **Detect live Office session**: if `mcp__office__*` tools are present (Cowork),
   drive the live workbook/deck.
2. **Probe Python library**: `python3 -c "import openpyxl"` (Excel) /
   `python3 -c "import pptx"` (PowerPoint) / `python3 -c "import docx"` (Word).
3. **Probe LibreOffice**: `which soffice` for recalc / convert.

If a backend is missing, halt-or-degrade per FR-044 with the exact remediation
command (`pip install openpyxl python-pptx python-docx`, install LibreOffice).

## `xlsx-financials` Shared Core

`xlsx-financials` is the shared formatted-statement skill that all tabular model
outputs route through. It pairs XBRL data with the `openpyxl` path to produce
formatted `.xlsx` (number formats, frozen headers, hierarchical indentation,
formula traces from `gold.xbrl_calculations`). `dcf`, `comps`, `3-statement`,
`recent-quarter`, and `earnings-preview` route tabular financial output through
it for consistent formatting and centralized formula auditing per FR-088.
