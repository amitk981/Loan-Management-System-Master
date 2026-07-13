# Review Packet: 2026-07-10_201119_normal_run

## Result
Complete on all configured gates; PostgreSQL concurrency execution remains explicit residual
validation because the AFK sandbox denied the host socket.

## Slice
`006G-submit-to-sanction`

## Delivered behavior

- Strict source §24.5 POST accepts only non-blank `remarks`.
- Active Credit Manager role, independent `credit.appraisal.submit_sanction`, and credit-domain
  object scope are all required.
- Reviewed appraisal, complete frozen prerequisites/risk, and exact latest immutable review
  consistency are checked without reading current eligibility or loan-limit rows.
- One pending case is created under application -> appraisal -> history -> case lock order; frozen
  exception input is flagged, both statuses advance, and all writes/evidence are atomic.
- Approval matrix, approver assignment/actions, exception decisions, documents, meetings,
  communication, and sanction decisions remain out of scope.

## Traceability

- Source `api-contracts.md` §3/§24.5 says explicit backend-enforced actions require actor, reason,
  status, audit, completed Credit Manager review, and exception flag/route. The endpoint and
  `AppraisalWorkflow.submit_to_sanction` implement those gates; tests
  `test_reviewed_appraisal_creates_one_pending_case_and_metadata_only_evidence` and
  `test_exception_flag_is_frozen_and_audit_failure_rolls_back_every_write` verify them.
- Source `functional-spec.md` M04-FR-010 and roadmap R2-AC-008 require Credit Manager review before
  sanction. The workflow rejects missing/draft/returned/review-pending/rejected or inconsistent
  review evidence, verified by
  `test_invalid_or_inconsistent_appraisal_states_and_repeat_have_no_side_effects` and the missing
  appraisal test.
- Source `auth-permissions.md` §12.5/§20.1/§34.4 names the independent submit permission and Credit
  Manager action. `test_payload_permission_role_and_object_scope_are_independent` proves role,
  permission, and object-domain outcomes separately.
- Source `data-model.md` §15.3/§30/§34 and codebase design §12.3 require a case return seam,
  operational indexes, uniqueness, and atomic state/evidence. `ApprovalCase` provides the minimal
  unique pending shell; forced case/audit rollback and repeat tests verify all-or-nothing behavior.
- The slice's rejection requirement is verified by
  `test_rejected_appraisal_preserves_unsent_rejection_note_byte_for_byte`.

## Validation

- TDD red: endpoint missing, expected failures saved in `tdd-red-sanction-submission.txt`.
- Focused sanction tests: 6 functional tests passed; PostgreSQL-only race skipped under SQLite.
- Final focused sanction/migration: 8 passed, one PostgreSQL-only skip.
- Full backend: 372 passed, five PostgreSQL-only skips; coverage 93% (floor 85%).
- Django check and `makemigrations --check --dry-run`: passed.
- Frontend: lint passed; typecheck passed; 107 tests passed; build passed.
- `git diff --check`: passed; one migration; protected/source files untouched.
- PostgreSQL command: one test found, zero executed because socket access failed before database
  creation with `Operation not permitted`; see `postgresql-sanction-concurrency.txt`.

## Recommended next action
Proceed to sharpened 006H frontend integration. Independently execute the PostgreSQL-only sanction
race when a host-permitted runner is available, then keep 006X bounded to the Epic 006 journey
ending at one pending case.
