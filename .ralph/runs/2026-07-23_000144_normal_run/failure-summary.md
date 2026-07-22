# Failure Summary

- Run: 2026-07-23_000144_normal_run
- Mode: normal_run
- Slice: 011J-archive-record-and-retention
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
postgresql-acceptance-results.md:- FAIL: first independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: second independent run did not satisfy the slice contract and exact count.
postgresql-acceptance-results.md:- FAIL: PostgreSQL environment evidence is missing.
```

## Last 50 lines: postgresql-acceptance-results.md

```
# PostgreSQL Acceptance Results

- Contract expected tests: 1
- Contract labels:
  - sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.ArchiveRecordPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_000144_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_000144_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_000144_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_000144_normal_run/changed-files.txt
.ralph/runs/2026-07-23_000144_normal_run/codex-settings.md
.ralph/runs/2026-07-23_000144_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_000144_normal_run/evidence/archive-manifest-example.json
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-behavior-matrix-green.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-behavior-matrix.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-detail-read-green.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-detail-read-red.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-final-focused.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-happy-path-green.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-happy-path-red.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-permissions-green.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-permissions-red.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-postgresql-contract-local.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-search-green.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/archive-search-red.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/backend-check-final.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/backend-check.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/catalogue-regression.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/impacted-regressions.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/migrations-check-final.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/migrations-check.txt
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_000144_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_000144_normal_run/execution-plan.md
.ralph/runs/2026-07-23_000144_normal_run/final-summary.md
.ralph/runs/2026-07-23_000144_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_000144_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_000144_normal_run/preflight-results.md
.ralph/runs/2026-07-23_000144_normal_run/prompt.md
.ralph/runs/2026-07-23_000144_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_000144_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_000144_normal_run/review-packet.md
.ralph/runs/2026-07-23_000144_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_000144_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_000144_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
sfpcl_credit/closure/migrations/0004_archive_record.py
sfpcl_credit/closure/models.py
sfpcl_credit/closure/modules/loan_closure.py
sfpcl_credit/closure/views.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/tests/test_archive_api.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
```
