# Review Packet: 2026-07-17_102143_normal_run

## Result
Complete pending independent Ralph validation and commit.

## Slice
`009F-cfc-authorization-rejection`

## Standards Review

- One deep module interface: callers use `DisbursementWorkflow.authorise`; validation, authority,
  locking, reconciliation, replay, evidence, audit, workflow, and task completion remain local.
- HTTP translation stays in `disbursements/views.py`; the module owns all multi-row financial policy.
- The response uses the standard envelope and strict unknown-field/query validation.
- One migration extends the existing aggregate with nullable historical fields and a terminal tuple
  constraint. No dependency, frontend production file, protected file, or source document changed.
- Audit/workflow/task evidence is safe and attributable; no bank/member plaintext or token material is
  returned or logged.

## Spec Review and Traceability

- Source API §31.3 says POST decision/comments only; the route accepts exactly those fields and is
  verified by `test_payload_permission_governance_and_maker_checker_fail_closed`.
- Integrations §§9.1/9.2/9.6 say CFC approval/rejection is independent manual-bank authorisation, not
  execution; `test_cfc_approval_is_terminal_evidence_but_not_bank_execution` and
  `test_rejection_closes_task_without_transfer_or_account_side_effects` prove pending transfer and
  zero account/communication side effects.
- Auth §§15.7/16.3/26.5 require active governed CFC authority, explicit permission, exact scope, and
  maker-checker separation; the permission/maker test, governed non-finance-primary test, and
  nondisclosing missing/invalid-authority test prove the matrix.
- Slice validation requires exact 009E2 and current governed source-bank evidence;
  `test_replaced_source_bank_governance_conflicts_without_decision_writes` and the changed-ledger
  test prove fail-closed, zero-write behavior without re-running upstream readiness owners.
- Source concurrency/replay requirements are covered by exact/changed/opposite replay tests, retained
  evidence corruption, and two PostgreSQL tests that each race five distinct governed CFC callers
  through the real source-bank owner.

## Evidence

- RED: `authorisation-red.log`, `authorisation-stale-red.log`,
  `authorisation-replay-integrity-red.log`.
- GREEN: `authorisation-final-green.log`, `backend-focused-post-format.log`, and
  `authorisation-postgresql-final-green.log`.
- Gates: `django-check.log`, `migration-check.log`, `frontend-lint.log`,
  `frontend-typecheck.log`, `frontend-tests.log`, `frontend-build.log`.
- Sanitized responses: `evidence/api-examples.md`.

## Recommended Next Action
Run independent full backend coverage/queue/protected-path validation, commit through Ralph, then run
the due architecture review before sharpened 009G.
