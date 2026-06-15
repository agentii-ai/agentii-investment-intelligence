# Office Tooling (canonical office-output contract)

Canonical approach for generating office files in this package. The agentii MCP
surface does **not** expose abstract `xlsx.build` / `pptx.build` / `pptx.edit` /
`pptx.refresh` tools — those belong to a different plugin. Skills MUST use the
concrete primitives below.

## Excel (`.xlsx`) — via `Bash` + Python `openpyxl`

The agent writes a self-contained Python script (no external deps beyond
`pip install openpyxl`) from the data already retrieved via XBRL tools, executes
it with `Bash`, and verifies the output file exists.

1. Write `_build_{ticker}_{type}.py` using `openpyxl`.
2. Execute: `Bash: python3 _build_{ticker}_{type}.py`.
3. Verify: `Bash: ls -la {ticker}/{YYYY-MM-DD_HHMM}_statement-{type}.xlsx` — confirm
   the file exists and its size > 0.
4. Follow Anthropic FSI `xlsx-author` conventions: **blue font** = hardcoded
   inputs, **black font** = formulas, **green font** = cross-sheet links; named
   ranges for key metrics; a `Checks` tab with TRUE/FALSE validation.

**Degraded fallback (true last resort)**: only if `python3 -c "import openpyxl"`
exits non-zero. Output a `.md` summary with full data tables, annotate
`data_availability: degraded` and `openpyxl_missing: true`, and report the exact
command `pip install openpyxl` to the user. The `.md` is NOT an acceptable
substitute when openpyxl is available.

`Bash` MUST appear in the skill's `allowed_tools` whenever this path is used.

## PowerPoint (`.pptx`) — `.md` slide specifications

This package produces polished `.md` slide-deck specifications as the primary
deliverable. Each `.md` is structured slide-by-slide and can be pasted directly
into Google Slides, Keynote, Deckset, or PowerPoint. Skills MUST state they
output `.md` slide specifications and MUST NOT claim to produce `.pptx` binaries.

Optional binary `.pptx` rendering is available via the companion
`financial-analysis:pptx-author` skill (separate plugin install; requires
`python-pptx`). Do not assume it is present.

## Word (`.docx`)

Not supported in this package.

## Verification Rule

After writing any office file, verify the file exists at the expected path and
report its size. Never report success for a file that was not actually written.
