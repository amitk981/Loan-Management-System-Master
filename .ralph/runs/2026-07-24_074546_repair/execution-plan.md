# Execution Plan

Selected slice: 012D-audit-explorer

## Permission check

- Work only in the active worktree.
- Candidate product edits remain permitted under `sfpcl_credit/**`.
- Repair evidence edits remain permitted under
  `.ralph/runs/2026-07-24_074546_repair/**`.
- Do not modify protected workflow/configuration/policy files, `docs/source/**`, orchestrator-owned
  state/progress/changed-files facts, slice status, Git metadata, or the preserved candidate outside
  the demonstrated backend validation domain.
- Do not install dependencies or run Git staging, commit, or push commands.

## Demonstrated failure

The authoritative backend coverage gate failed only
`ReportExportApiTests.test_request_status_authentication_validation_and_not_found_contracts`.
For a request containing both an unsupported `report_code` and an invalid `format`, the candidate
returns only the `format` error; the existing API contract expects unsupported-report validation to
take precedence and expose `field_errors.report_code`.

## Bounded repair

1. Reproduce the exact failing Django test with the mandated Ralph virtualenv interpreter and save
   RED output.
2. Inspect only the report-export request validation path and its existing tests, rank falsifiable
   causes, and identify the smallest contract-preserving fix.
3. If the existing failed coverage test is already a red-capable regression seam, do not duplicate
   it. Make the smallest implementation correction in the report-export validation domain.
4. Rerun the exact failed test to GREEN, then run the focused report-export API module to reveal and
   correct any additional errors in that same validator domain.
5. Save repair evidence, update the repair risk assessment/review packet/final summary, and leave
   full-suite coverage plus commit/state/status bookkeeping to the independent orchestrator.
