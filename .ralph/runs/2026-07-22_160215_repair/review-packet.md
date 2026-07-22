# Review Packet: 2026-07-22_160215_repair

## Result
Ready for independent validation

## Slice
011E-recovery-decision-approval

## Repair Delivered

- Preserved the complete 011E recovery-decision candidate.
- Isolated the pre-credit-ownership migration projection from the new downstream `recovery` leaf,
  restoring historical `applications.EligibilityAssessment` and `LoanLimitAssessment` state.
- Isolated the pre-witness-evidence migration projection from the same leaf, restoring agreement
  between the historical Witness model and its reversed physical schema.
- Made no recovery product-rule, API, schema, permission, frontend, or protected-file change.

## Diagnosis

The new `recovery.0001` leaf depends on current approvals and defaults. Its forward dependency plan
therefore includes current `applications` and `credit` migrations. Historical tests that projected
all graph leaves except a fixed downstream list accidentally included that leaf, so their model
registry outran the database schema after migration rollback. Adding `recovery` to those two
existing exclusion boundaries is the minimal repair.

## Verification

- Credit ownership focused RED: 2 errors with missing historical `EligibilityAssessment`.
- Credit ownership focused GREEN: 2 tests passed.
- Witness migration focused RED: 1 missing-column error for `verification_folio_number`.
- Witness migration focused GREEN: 1 test passed.
- Django system check: passed.
- Migration sync: passed, no changes detected.
- Exact failed validator: 1,619 tests passed, 160 skipped, 90% coverage versus 85% floor, exit 0.
- `git diff --check`: passed.
- Debug residue/protected-path review: passed.

## Source Traceability

The repair does not alter source behavior. The original candidate still enforces the slice's
source-authorised recovery decision chain (`api-contracts.md` §35.8; `data-model.md` §§15.2-15.4,
21.5; `product-requirements.md` §11.27; `auth-permissions.md` §§16-18, 20.3, 25.8; and
`security-privacy.md` §23.2). The repair only keeps two legacy migration proofs scoped to the
historical model states they explicitly test, verified by the focused migration tests and the full
coverage lane above.

## Recommended Next Action
Run Ralph's independent High-risk validation against this same candidate and commit/merge only if
every configured gate, including PostgreSQL acceptance, passes.
