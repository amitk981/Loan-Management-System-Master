# Review Packet: 2026-07-13_232007_normal_run

## Result

Success

## Slice

007I-sanction-workbench-ui

## Outcome

The Sanction Workbench is now a real authenticated approval-case container. It preserves the
prototype composition while rendering server-frozen cycle facts and driving only server-projected
resource actions. Special-case evidence uses the existing document and §25.11 owners; terminal
terms use §25.8 only when the current user has its separate permission.

## Standards review

The first independent review found client-synthesized partial status, a redesigned multi-button
decision surface, incorrect terminal badge semantics, self-seeding screenshot comparisons, and
client-derived action/meeting authority. Corrections now:

- render `current_status` and immutable action counts without inventing workflow state;
- retain the prototype's single decision button and radio-grid modal;
- use outcome-specific badge semantics and keep field errors in the open modal;
- write screenshots only to Ralph evidence, never bless a generated baseline;
- use case resource actions for all decisions, including the backend-projected meeting action.

Raw-source checks find no owned mock import, hard-coded ₹5 lakh authority matrix, role-slot match,
or legacy `approve_sanction` gate. The frontend has one typed sanction service boundary; no register
or live-appraisal workaround exists. No protected/source file changed and `git diff --check` passes.

## Spec review and traceability

- Screen S21/S22 and M05-FR-002/007/008/011 require the queue, ten-point review, joint decisions,
  conflict and mandatory reason behavior. `SanctionWorkbench.test.tsx` proves exact queue/detail and
  action URLs/bodies, partial/final states, reasons, stale/gate/conflict errors, role scope, and
  returned-old/corrected-new cycle isolation.
- Screen S24 and §25.11 require related-party meeting status plus bounded evidence recording. The
  case detail projects `record_general_meeting_approval`; the frontend test proves three legal
  uploads followed by the exact distinct-id record body. Backend tests prove enabled and disabled
  actor decisions without changing ordinary case actions.
- §25.8 and 007H2 require independent sanction permission/object scope. The UI requests terminal
  terms only with `approvals.sanction.read`, preserves denied/not-found errors, and never falls back
  to the Credit Sanction Register.
- §44 requires resource action objects. Both the decision modal and meeting form fail closed on
  missing/disabled actions and use `/auth/me` only as the usability intersection.

The remaining documents-selection gap is recorded as A-090: absent a documents-owned referenceable
list, the UI will upload new evidence or reuse the case's accepted three ids, never solicit arbitrary
UUIDs. This is a deliberate fail-closed boundary, not an invented business rule.

## Validation

- RED/GREEN: frontend real-container replacement and backend meeting-action authority cycles saved.
- Focused: 21 Sanction Workbench tests; 105 approval-routing tests after compatibility correction.
- Full backend: 680 tests, 19 expected SQLite skips, 93% coverage (floor 85%).
- Full frontend: 227 tests plus build, typecheck, and lint.
- Browser: contract collection succeeds; sandbox launch denial is recorded honestly for the
  orchestrator's external two-run acceptance.

## Recommended Next Action

Run independent Ralph validation, commit/merge/push the passing slice, then execute 007J.
