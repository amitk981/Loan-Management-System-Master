# Failure Summary

- Run: 2026-07-22_131655_normal_run
- Mode: normal_run
- Slice: 011D-non-payment-note-workflow
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
  - sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.NonPaymentNotePostgreSQLAcceptanceTests
- FAIL: first independent run did not satisfy the slice contract and exact count.
- FAIL: second independent run did not satisfy the slice contract and exact count.
- FAIL: PostgreSQL environment evidence is missing.
```

## Changed files (git status)

```
.ralph/runs/2026-07-22_131655_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-22_131655_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-22_131655_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-22_131655_normal_run/changed-files.txt
.ralph/runs/2026-07-22_131655_normal_run/codex-settings.md
.ralph/runs/2026-07-22_131655_normal_run/diff-limits-results.md
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/approval-routing-regression.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/backend-final-checks.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/catalogue-seed-regression.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/default-recovery-reverse-final.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/default-recovery-reverse-focused.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/migrations-check.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-corrected-document-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-corrected-document-red.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-create-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-create-red.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-document-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-document-red.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-postgresql-class-final-discovery.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-postgresql-class-local-discovery.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-return-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-return-red.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-review-findings-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-review-transition-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-review-transition-red.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-submit-green.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-submit-red.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-workflow-final.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/non-payment-workflow-focused.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-22_131655_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-22_131655_normal_run/execution-plan.md
.ralph/runs/2026-07-22_131655_normal_run/final-summary.md
.ralph/runs/2026-07-22_131655_normal_run/no-op-check-results.md
.ralph/runs/2026-07-22_131655_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-22_131655_normal_run/preflight-results.md
.ralph/runs/2026-07-22_131655_normal_run/prompt.md
.ralph/runs/2026-07-22_131655_normal_run/protected-paths-check.md
.ralph/runs/2026-07-22_131655_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-22_131655_normal_run/review-packet.md
.ralph/runs/2026-07-22_131655_normal_run/risk-assessment.md
.ralph/runs/2026-07-22_131655_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-22_131655_normal_run/slice-status-transition-check.md
docs/working/API_CONTRACTS.md
docs/working/ASSUMPTIONS.md
sfpcl_credit/approvals/models.py
sfpcl_credit/approvals/modules/approval_actions.py
sfpcl_credit/approvals/modules/approval_case_engine.py
sfpcl_credit/approvals/modules/approval_case_selector.py
sfpcl_credit/approvals/modules/read_scope.py
sfpcl_credit/approvals/modules/recovery_handoff.py
sfpcl_credit/config/urls.py
sfpcl_credit/defaults/migrations/0004_non_payment_note.py
sfpcl_credit/defaults/models.py
sfpcl_credit/defaults/modules/default_workflow.py
sfpcl_credit/identity/catalogue.py
sfpcl_credit/legal_documents/modules/non_payment_note_document.py
sfpcl_credit/recovery/__init__.py
sfpcl_credit/recovery/modules/__init__.py
sfpcl_credit/recovery/modules/recovery_workflow.py
sfpcl_credit/recovery/views.py
sfpcl_credit/tests/test_default_recovery_postgresql_acceptance.py
sfpcl_credit/tests/test_non_payment_note_workflow_api.py
```
