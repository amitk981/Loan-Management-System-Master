# Dependency Graph Evidence

Canonical allowed business-app edge:

`sfpcl_credit.approvals.modules.sanction_handoff`
→ `sfpcl_credit.credit.modules.appraisal_workflow`

Forbidden edges:

- `sfpcl_credit.credit**` → `sfpcl_credit.approvals**`
- `sfpcl_credit.approvals**` → any `sfpcl_credit.credit**` reference other than the exact public
  appraisal-workflow module or one of its exported names

The repository scan resolves each source path to its containing Python package before resolving
`ast.ImportFrom.level`. It found zero forbidden production edges and positively observed the exact
public handoff edge. See `terminal-logs/006G5-green-relative-import-matrix-and-repository-scan.log`.
