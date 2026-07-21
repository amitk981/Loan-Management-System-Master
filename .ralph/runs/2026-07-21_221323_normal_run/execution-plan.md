# Execution Plan

## Slice

010N4-global-search-sensitive-authority-closure

## Scope and permissions

- Work only in the active Ralph worktree and only on the selected slice.
- Production/test edits are limited to permitted `sfpcl_credit/**` and `sfpcl-lms/src/**` paths.
- Evidence and run artifacts are limited to `.ralph/runs/2026-07-21_221323_normal_run/**`.
- Do not edit protected paths, source documents, orchestrator-owned state/progress/status, or unrelated slices.

## Implementation sequence

1. Map the current global-search public API, frontend request lifecycle, tests, owner modules, and the original failing review probe.
2. Identify the smallest public owner-facade changes that enforce each domain's permission/object scope and nondisclosing sensitive matching before aggregation, ordering, counts, caps, or pagination.
3. TDD tracer bullet: add a permanent public regression for CFO blank-cheque nondisclosure, run it RED, and retain the exact command/output.
4. Implement the minimal canonical security-instrument search facade and aggregate integration, then rerun the tracer GREEN.
5. Repeat narrow RED/GREEN cycles for independent group authority, scope-before-cap/count/page, sensitive input coverage, action suppression, input validation/boundaries, and representative query-plan/index behavior required by AC-E10-S1/S2/S4.
6. Add or refine frontend tests for raw-query non-retention and safe pagination, observe RED, implement minimal query clearing/opaque continuation behavior, and retain GREEN evidence for AC-E10-S3.
7. Run the original architecture-review probe command exactly and save a current passing log; run focused backend/frontend regressions, Django checks/migration sync, frontend typecheck/lint/build, without running the complete backend suite.
8. Inspect diff stats and targeted hunks for scope/protected-path compliance, then write review-closure-evidence.md, risk-assessment.md, review-packet.md, and final-summary.md.
9. Run the exact review-closure validator until it prints PASS; leave the review packet result exactly `Ready for independent validation`.

## Required evidence

- Distinct RED and GREEN logs with exact permanent test selectors and explicit exit codes.
- Acceptance evidence for AC-E10-S1 through AC-E10-S4.
- Exact original reproducer replay with a positive pass signal and exit code 0.
- Focused backend/frontend quality-gate logs and self-review artifacts.
