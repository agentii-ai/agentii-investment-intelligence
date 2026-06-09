# xlsx-read Tool Contract

`xlsx-read` is a shared MCP/API tool that reads `.xlsx` files from the workspace and returns structured JSON. It is symmetric to `xlsx-author` (output) and enables skills to consume existing analyst workbooks as data sources.

## Tool Surface

```
xlsx-read(path: string) → XlsxReadResult
```

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `path` | Yes | string | Workspace-relative path to `.xlsx` file |

## Response Shape

```json
{
 "path": "assumptions.xlsx",
 "sheets": [
 {
 "name": "Inputs",
 "rows": 45,
 "columns": 12,
 "tables": [
 {
 "range": "B5:D20",
 "headers": ["Metric", "Value", "Source"],
 "row_count": 15,
 "column_types": ["string", "number", "string"]
 }
 ]
 }
 ],
 "formulas": [
 {
 "sheet": "DCF",
 "cell": "C10",
 "formula": "=Inputs!B5*(1+Inputs!B6)^C9",
 "precedents": ["Inputs!B5", "Inputs!B6", "DCF!C9"],
 "dependents": ["DCF!C15", "DCF!C20"]
 }
 ],
 "named_ranges": {
 "WACC": "Inputs!B8",
 "TerminalGrowth": "Inputs!B9",
 "ProjectionYears": "Inputs!B10"
 },
 "file_metadata": {
 "created": "2026-05-15T10:30:00Z",
 "modified": "2026-06-01T14:22:00Z",
 "author": "Analyst Name"
 }
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `sheets[].name` | string | Worksheet name |
| `sheets[].rows` | int | Total row count |
| `sheets[].columns` | int | Total column count |
| `sheets[].tables[]` | object | Auto-detected table ranges with headers and column types |
| `formulas[]` | object | Cell references with formula text, precedent cells, and dependent cells |
| `named_ranges` | dict | Workbook-level and worksheet-level named ranges → cell reference |
| `file_metadata` | object | File creation/modification timestamps and author |

## Security Constraint

The tool operates on workspace-relative paths only. Absolute filesystem paths are rejected. The effective path is resolved as `<workspace_root>/<path>`.

## Skills That Use xlsx-read

| Skill | Use Case |
|-------|----------|
| `dcf-model` | Read analyst's existing WACC/growth assumptions, compare against XBRL-derived values |
| `comps-analysis` | Read peer universe list from analyst's tracking workbook |
| `3-statement-model` | Read historical data from analyst's existing model for projection baseline |
| `audit-xls` | Read workbook for formula auditing and calculation arc cross-validation  |

## Integration Pattern

Skills add `xlsx-read` to their `allowed_tools` frontmatter and use it in their Protocol section:

```
1. Check workspace for existing assumptions workbook: `ls *.xlsx`
2. If found, read via `xlsx-read(path="assumptions.xlsx")`
3. Extract relevant named ranges (WACC, growth rates, projection years)
4. Compare against XBRL-derived values from `search_xbrl_facts`
5. Flag divergences >5% as audit findings
```

## Cross-Reference

- ****: xlsx-financials skill (Excel output)
- ****: Calculation arc cross-validation
- ****: This contract
