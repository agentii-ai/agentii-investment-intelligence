# Office Backends — Excel & PowerPoint Generation

The `models-and-pitches` skills support 3 office backends, probed in order at Preflight time. If ANY backend is available, skills proceed. If ALL are unavailable, skills halt with `AGENTII_OFFICE_UNREACHABLE`.

## Tier 1: agentii-office MCP (Recommended)

Server-side LibreOffice with guaranteed formula fidelity. Requires `AGENTII_API_KEY`.

```bash
# No installation needed — skills probe automatically:
curl -s -o /dev/null -w "%{http_code}" --max-time 2 https://mcp.agentii.ai/office/mcp/health
```

**Pros**: Zero local deps, guaranteed LibreOffice version, presigned R2 URLs, R2 artifact storage.
**Cons**: Requires agentii.ai account with office quota; internet required.

## Tier 2: Python + LibreOffice (Local)

Open-source stack using `openpyxl`, `python-pptx`, and LibreOffice headless.

### macOS

```bash
# Python deps
pip install openpyxl python-pptx

# LibreOffice (includes headless calc)
brew install --cask libreoffice

# Verify
python3 -c "import openpyxl; import pptx; print('OK')"
libreoffice --headless --version
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
# Verify:
python -c "import openpyxl; import pptx; print('OK')"
```

**Pros**: Fully offline, mature ecosystem, CI-validatable deterministic output.
**Cons**: ~500 MB LibreOffice install; version skew possible across users.

## Tier 3: OfficeCLI (Single Binary)

Zero-dependency single binary with embedded .NET runtime. Apache 2.0 license.

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
officecli --version
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
officecli --version
```

**Pros**: ~50 MB, zero deps, no Python, no LibreOffice, 150+ Excel functions, built-in MCP server, template merging.
**Cons**: Newer project (2026), smaller community than LibreOffice.

## Quick-Start Smoke Test

Verify your chosen backend works before invoking skills:

```bash
# Python backend
python3 -c "
import openpyxl
wb = openpyxl.Workbook
ws = wb.active
ws['A1'] = 'Hello from agentii'
wb.save('/tmp/agentii-test.xlsx')
print('Python backend: OK')
"

# OfficeCLI backend
officecli xlsx new /tmp/agentii-test.xlsx && echo "OfficeCLI backend: OK"
```

## Cross-Backend Determinism

The same `xlsx_spec` or `pptx_spec` produces **byte-identical output** across backends. This is CI-enforced: golden fixtures are rendered under both Python+LibreOffice and OfficeCLI, and SHA256 checksums are compared. Any backend-specific rendering differences fail CI.

## Minimum Versions

| Component | Minimum Version | Notes |
|-----------|----------------|-------|
| openpyxl | 3.1+ | Required for xlsx_build + xlsx_evaluate |
| python-pptx | 0.6.21+ | Required for pptx_build + pptx.edit |
| LibreOffice | 7.4+ | Required for xlsx_recalc (formula resolution) |
| OfficeCLI | 1.0.80+ | Required for all office operations via single binary |
