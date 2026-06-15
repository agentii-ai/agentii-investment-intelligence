# xlsx-financials — Tool Fallbacks

Extracted from SKILL.md for progressive disclosure (US5).

| Tool | Failure Mode | Fallback Action | Coverage Annotation |
|------|-------------|-----------------|---------------------|
| `get_statement` | Endpoint unavailable | Use `search_xbrl_facts` with individual concept queries; structure manually from `get_statement_structure` tree | "Statement endpoint unavailable; built from individual XBRL facts" |
| `get_statement_structure` | Timeout | Use `list_xbrl_concepts` for concept discovery; flat structure without hierarchy | "Statement tree unavailable; flat concept list used" |
| `Bash` / `openpyxl` | `python3 -c "import openpyxl"` fails (exit ≠ 0) | TRUE LAST RESORT only: output the `.md` summary with full data tables + `data_availability: degraded` annotation; report the exact `pip install openpyxl` command | "openpyxl unavailable; markdown summary provided. Install openpyxl: pip install openpyxl" |
