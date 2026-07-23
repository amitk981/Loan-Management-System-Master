# Failure Summary

- Run: 2026-07-23_164006_normal_run
- Mode: normal_run
- Slice: 011N-grievance-workflow
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

- Contract expected tests: 2
- Contract labels:
  - sfpcl_credit.tests.test_compliance_postgresql_acceptance.GrievanceWorkflowPostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
.ralph/runs/2026-07-23_164006_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-23_164006_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-23_164006_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-23_164006_normal_run/changed-files.txt
.ralph/runs/2026-07-23_164006_normal_run/codex-settings.md
.ralph/runs/2026-07-23_164006_normal_run/diff-limits-results.md
.ralph/runs/2026-07-23_164006_normal_run/evidence/api-responses/grievance-contract.md
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/01-create-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/01-create-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/02-scoped-read-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/02-scoped-read-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/03-assignment-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/03-assignment-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/04-resolution-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/04-resolution-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/05-escalation-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/05-escalation-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/06-011k-integration-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/06-011k-integration-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/07-negative-contract-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/07-negative-contract-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/08-postgresql-local-contract.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/09-document-download-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/09-document-download-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/10-acknowledgement-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/10-acknowledgement-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/11-focused-grievance-pack.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/12-reverse-consumers-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/12-reverse-consumers.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/13-portal-primitive-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/13-portal-primitive-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/14-notice-truth-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/14-notice-truth-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/15-django-migration-gates.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/16-final-grievance-and-catalogue-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/17-final-reverse-consumers-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/18-django-check-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/19-migration-drift-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/20-postgresql-contract-local.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/21-review-boundaries-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/21-review-boundaries-red.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/22-final-review-fixes-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/23-final-acceptance-green.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/24-final-django-check.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/25-final-migration-drift.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-23_164006_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-23_164006_normal_run/execution-plan.md
.ralph/runs/2026-07-23_164006_normal_run/final-summary.md
.ralph/runs/2026-07-23_164006_normal_run/no-op-check-results.md
.ralph/runs/2026-07-23_164006_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-23_164006_normal_run/preflight-results.md
.ralph/runs/2026-07-23_164006_normal_run/prompt.md
.ralph/runs/2026-07-23_164006_normal_run/protected-paths-check.md
.ralph/runs/2026-07-23_164006_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-23_164006_normal_run/review-packet.md
.ralph/runs/2026-07-23_164006_normal_run/risk-assessment.md
.ralph/runs/2026-07-23_164006_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-23_164006_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/compliance/migrations/0004_grievance_grievancedocument_and_more.py
sfpcl_credit/compliance/models.py
sfpcl_credit/compliance/modules/compliance_task_engine.py
sfpcl_credit/compliance/modules/grievance_workflow.py
sfpcl_credit/compliance/views.py
sfpcl_credit/config/urls.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/tests/test_compliance_postgresql_acceptance.py
sfpcl_credit/tests/test_grievance_workflow.py
```
