# Office Backends — Excel, PowerPoint & Word Generation (v2.3.1)

v2.3.1 uses **code-mode** office output — the agent writes self-contained Python
scripts, executes them via `Bash`, and validates the results. No office MCP
server. No API calls for file generation. Everything happens on your machine.

The canonical contract is [`contracts/office-tooling.md`](../../contracts/office-tooling.md).
This doc covers installation only.

---

## Two Bindings, One Contract

Office-producing skills probe backends in order:

1. **Live Office JS** — if `mcp__office__excel_*` / `mcp__office__powerpoint_*` tools
   are present (Claude Cowork), the agent drives the live workbook or deck directly.
2. **Headless Python** — the default. The agent writes a `.py` script using
   `openpyxl` (Excel) or `python-pptx` (PowerPoint), executes it via `Bash`,
   recalculates formulas through LibreOffice, and audits the result.

If neither backend is available, the skill degrades gracefully to a `.md`
deliverable with `data_availability: degraded` and the exact `pip install`
command to fix it. Never a silent failure.

---

## Python + LibreOffice (Default Code-Mode Backend)

### macOS

```bash
# Python libraries
pip install openpyxl python-pptx

# LibreOffice (includes headless calc + impress)
brew install --cask libreoffice

# Verify
python3 -c "import openpyxl; import pptx; print('OK')"
which soffice
```

### Linux (Debian/Ubuntu)

```bash
pip install openpyxl python-pptx
sudo apt install libreoffice-calc libreoffice-impress
python3 -c "import openpyxl; import pptx; print('OK')"
```

### Windows

```powershell
pip install openpyxl python-pptx
# LibreOffice: download from https://www.libreoffice.org/download/
python -c "import openpyxl; import pptx; print('OK')"
```

### Word (Optional, Deferred)

Word `.docx` support via `python-docx` is documented in the office contract as
available-but-optional. All skills default to `.md` at v2.3.1. `.docx`
consumption is deferred until a dedicated memo/IC-note skill ships.

```bash
pip install python-docx   # Optional — not required for any current skill
```

---

## How the Agent Produces Office Files

The agent never calls a remote service for file generation. Instead:

1. **Write** — agent authors a self-contained `_build_{ticker}_{type}.py` script using
   data already retrieved via XBRL tools
2. **Execute** — `Bash: python3 _build_{ticker}_{type}.py`
3. **Verify** — `Bash: ls -la {output_path}` — confirm file exists and size > 0
4. **Recalculate** (Excel only) — `soffice --headless` resolves all formulas; the
   package ships `scripts/recalc.py` as a convenience wrapper that also audits
   `hardcoded_count == 0` for projection/margin/discount cells
5. **Audit** — every tagged cell must be a live formula, never a hardcoded value

### Excel Conventions

- **Blue font** = hardcoded input assumptions
- **Black font** = live formulas
- **Green font** = cross-sheet links
- Named ranges for key metrics
- A `Checks` tab with TRUE/FALSE validation ties (balance sheet balances, cash
  flow ties to cash)

### PowerPoint Conventions

- One idea per slide; every figure footnoted to its source model cell or `/v/`
  citation
- Firm-branded templates honored when mounted at `./templates/`
- Charts embedded as model-rendered PNGs when fidelity matters

---

## Quick Smoke Test

```bash
# Verify Python stack
python3 -c "
import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws['A1'] = 'Hello from agentii'
wb.save('/tmp/agentii-test.xlsx')
print('openpyxl: OK')
"

# Verify LibreOffice
soffice --headless --version

# Verify recalc.py
python3 scripts/recalc.py --audit-only /tmp/agentii-test.xlsx
```

---

## Degraded Fallback Behavior

When a Python library is missing, skills never fail silently:

```
# Example: openpyxl not installed
data_availability: degraded
openpyxl_missing: true
# Remediation: pip install openpyxl
```

The `.md` fallback contains every data table. You're never blocked — just
missing the formatted workbook until you install the library.

---

## Minimum Versions

| Component | Minimum | Notes |
|-----------|---------|-------|
| Python | 3.10+ | Required for openpyxl / python-pptx |
| openpyxl | 3.1+ | Excel workbook creation |
| python-pptx | 0.6.21+ | PowerPoint deck creation |
| python-docx | 0.8.11+ | Word document creation (optional, deferred) |
| LibreOffice | 7.4+ | Formula recalculation + PDF export |

---

## Cross-Platform Notes

- **LibreOffice rendering may differ from Microsoft Office** — skills warn users
  to review the final file in the native app
- **CI golden fixtures** test structural correctness (sheet count, named range
  presence, formula-cell count) — not pixel-perfect rendering
- **Live Office JS** (Cowork) produces native Microsoft Office rendering when
  available; headless Python is the portable fallback
