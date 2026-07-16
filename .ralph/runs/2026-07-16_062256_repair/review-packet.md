# Review Packet: 2026-07-16_062256_repair

## Result

Pass pending Ralph's independent validation and commit.

## Slice

`009B-sap-customer-code-confirmation-and-reuse`

## Repair Diagnosis

The newest available failure summary was the old 008M2 changed-line failure, already repaired by
later successful runs. No 009B product diff or abandoned worktree existed. The fresh 009B tight loop
was the public flow test: it first failed at the exact missing `/send/` route with 404, then passed
unchanged after implementation.

## Standards Review

- Protected/source paths are untouched; one migration, no dependency, and no frontend change.
- API responses use standard envelopes and stable nondisclosing 400/403/409 errors.
- Permissions are separate create/send/complete/read grants and service-layer persisted role/object
  checks; broad Finance strings alone do not authorize an action.
- Communication/task creation uses the communications owner, workflow events use the canonical
  recorder, document evidence uses immutable upload provenance, and Annexure bytes use the Finance
  encrypted-storage owner.
- Final `git diff --check`, debug/TODO scan, Django check, migration drift, full gates, and protected-
  path scan are clean. Production changed surfaces have 90% scoped coverage; repository coverage is
  91%.

## Spec Review and Traceability

| Source requirement | Implementation | Verification |
|---|---|---|
| API §29.2 / M07-FR-006: send retained request to Senior Manager Finance | Owner-only draft→sent with verified Annexure and one direct communication/task | `test_send_replay_change_owner_and_terminal_state_are_zero_write` |
| API §29.3 / BR-050 / INT-SAP-003: assigned Senior Manager confirms | Frozen active assignee plus exact current sanction-cycle locks | happy-path and invalid-state/assignee/stale-cycle tests |
| BR-047/048 and §19.2: unique new code or same-member reuse | Upper/trim normalization, database `Lower(Trim(code))`, one active member constraint, A-124 reuse policy | new/reuse/inactive/global-duplicate/database-normalization tests |
| Optional restricted confirmation evidence | Exact immutable upload provenance, uploader, category, sensitivity, and request/application scope | `test_restricted_confirmation_evidence_must_match_actor_and_scope` |
| API §29.4: scoped masked member read | Completed-assignee scope; masked code-only projection; missing/out-of-scope parity | `test_member_read_is_masked_assignee_scoped_and_nondisclosing` |
| Replay and concurrency retain zero loser artifacts | Locked exact replay and pending-before-winner conflict | three PostgreSQL race tests, twice-run, two rounds each |
| No downstream finance truth | Service writes only request/code/communication/task/audit/workflow rows | focused artifact counts and full regression suite |

## Defects Found and Closed During the Run

1. PostgreSQL rejected a request lock that joined nullable completion fields. `FOR UPDATE OF self`
   now locks only the request row; related authorities are explicitly locked at their seams.
2. A direct finance→latest-approvals migration dependency broke the historical credit ownership
   migration state. Immutable sanction/approval UUID snapshots replaced the unnecessary FK and the
   exact two-test migration regression is green.
3. A caller outside the frozen request ownership could distinguish a non-terminal sanction through
   a 409 state error. The request's frozen owner or assignee is now checked before terminal-state
   evaluation, so inaccessible and absent objects both return 403 without leaking lifecycle state.

## Recommended Next Action

Run Ralph's independent gates and commit 009B. Because four slices are complete since the last
architecture review, run that review before already-sharpened 009C; 009D is now concrete as well.
