# Review Packet: 2026-07-13_202809_normal_run

## Result
Ready for independent validation

## Slice
007F2-exception-routing-coherence-and-explicit-projection-closure

## Outcome

- Non-forced exception routing now requires reviewed amount above frozen final eligible amount and
  an agreeing exception flag; both contradiction directions return stable zero-write 409 responses.
- `reason_for_approval` and Exception Register `business_reason` remain distinct. Case detail exposes
  the latter as frozen `exception_reason`; same-case register/matrix/limit facts govern coherence.
- A public workflow test reaches CFO + two Directors, closes the Exception Register, and reads the
  sanction decision and Credit Sanction Register without manually attaching exception evidence.
- The appraisal `post_save` receiver is deleted. Projection synchronization occurs only through the
  approval-owned interface after submission linkage, enrichment, and approval actions.

## Traceability

- The source says M05-FR-003/M05-FR-006 apply the matrix from amount/exception truth and require CFO
  plus two Directors with an Exception Register above the permissible limit. The code compares the
  reviewed recommendation with frozen `final_eligible_loan_amount` before routing and verifies the
  same predicate in case coherence. Verified by
  `test_contradictory_frozen_exception_predicates_are_stable_zero_write_denials` and
  `test_above_limit_exception_completes_public_three_approver_and_register_workflow`.
- Data model §15.3 owns `reason_for_approval`; §15.7 separately owns Exception Register
  `business_reason`/`risk_assessment`. The code no longer equates the reasons and binds the generated
  same-case row to the case exception projection. Verified by the distinct-reason public tracer and
  replay mismatch assertions.
- Codebase design §§13.1/26/27/42 require the approval module interface to own workflow/projection
  behavior and tests to cross public interfaces. The hidden appraisal signal and its registration
  are removed; direct saves are inert. Verified by
  `test_plain_appraisal_save_does_not_mutate_frozen_case_projection` and the existing case-save test.
- M05-FR-009 requires a Credit Sanction Register after decision. The public tracer asserts the exact
  terminal sanction decision/register ids and exception reference after three approvals.

## Evidence

- RED: `evidence/terminal-logs/01-exception-tracer-red.log`
- Predicate RED/GREEN: `04-contradictory-predicate-red.log`,
  `05-contradictory-predicate-green.log`
- Hidden-save RED/GREEN: `08-appraisal-save-projection-red.log`,
  `09-appraisal-save-projection-green.log`
- Full tracer/affected tests: `07-full-exception-tracer-green.log`,
  `12-approval-modules-green.log`
- Gate evidence: backend check/migration/coverage logs 13-15 and frontend logs 16-19.

## Validation

- Backend: Django check and migration sync pass; 670 tests pass, 19 expected PostgreSQL-only skips,
  total coverage 93% (floor 85%).
- Frontend: build, typecheck, lint, and 208 tests pass.
- Diff: 17 tracked files including Ralph state/docs, 515 changed lines; no dependency or
  migration; protected/source files unchanged; `git diff --check` passes.

## Recommended Next Action
Run independent Ralph validation and commit/merge if it passes, then execute 007G2.
