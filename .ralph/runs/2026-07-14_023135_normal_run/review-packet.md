# Review Packet: 2026-07-14_023135_normal_run

## Result

Ready for independent orchestrator validation.

## Slice

`007L-sanction-workbench-contract-and-browser-closure`

## Outcome

- Added mandatory credit-owned `approval-review-v2` borrower identity and approval-owned S21
  `workbench_summary` without live per-row appraisal/member/configuration reconstruction.
- Enforced exact sanction collection filters and rendered all queue facts plus immutable S22 action
  actor/role/decision/comment/time evidence using existing page/card/badge patterns.
- Preserved resource-action plus `/auth/me` intersections, exact decision endpoints/payloads,
  mandatory reject/return comments, canonical success refetch, stale/conflict/meeting errors,
  historical cycle isolation, and separate sanction-decision permission.
- Moved multipart body creation/auth/envelope/error mechanics into the shared authenticated client.
- Removed General Meeting metadata-id reuse and required three fresh accepted uploads for every
  changed submission.
- Declared/asserted the exact seven-state production-route Playwright contract.

## Source traceability

- `screen-spec.md` S21 says the queue shows borrower/type, three amounts, approval path, exception/
  related-party flags, risk, status, submitted date, and TAT. Code returns/renders those fields from
  frozen `workbench_summary`; verified by
  `test_collection_projects_complete_frozen_s21_workbench_facts` and the sanction container test.
- S22 and M05-FR-007/008/011 say actions/history include decision or abstention, actor confirmation,
  mandatory reasons, and time. Code renders immutable `approval_actions` separately and preserves
  existing action guards; verified by the 111-test approval routing suite and 22 workbench tests.
- API §25.3 requires `current_status=pending&approval_type=sanction&assigned_to_me=true`. The feature
  sends that exact ordered query and the Playwright route asserts it.
- S24/M05-FR-012 requires special-case evidence and blocking. The UI never reuses exposed ids and
  always uploads three fresh application-scoped legal files before §25.11; the backend remains the
  final reference validator. Verified by the changed-existing-evidence container test.
- Codebase design §§23.5/24.4 require one frontend transport owner. Shared transport now owns JSON/
  multipart session, headers, FormData, envelope, and error behavior; raw-source regressions reject
  direct sanction token/fetch mechanics.

## Validation evidence

- Backend RED/GREEN: `evidence/terminal-logs/backend-s21-red.log`,
  `backend-s21-green.log`, and `backend-workbench-contract-green.log`.
- Frontend RED/GREEN: `frontend-multipart-red.log`, `frontend-workbench-red.log`,
  `frontend-multipart-fields-red.log`, and matching green/final focused logs.
- Backend: Django check/migration sync; 686 tests, 19 expected skips, 93% coverage.
- Frontend: production build, typecheck, ESLint, 253 tests.
- Browser: named spec collection succeeds. `sanction-playwright-local.log` records the genuine
  Chromium Mach-port sandbox denial; no screenshots are claimed.
- Diff review: no protected paths, no migration/dependency, 12 implementation/document files and
  428 lines before Ralph closeout artifacts; `git diff --check` clean.

## Recommended next action

Run independent Ralph validation, including the declared browser contract twice; commit/merge/push
only if it passes. Then execute 007M followed by 007N.
