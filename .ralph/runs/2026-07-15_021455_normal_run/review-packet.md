# Review Packet: 2026-07-15_021455_normal_run

## Result

Complete; ready for independent Ralph validation.

## Slice

`008J-blank-dated-cheque-and-cancelled-cheque-custody`

## Reviewer focus

1. Confirm `security_instruments.modules.blank_dated_cheque` owns policy while the top-level process
   alone imports application/document/legal owners and issues the immutable evidence callbacks.
2. Confirm fixed masking and recursive redaction keep plaintext out of ordinary response,
   audit/version/workflow, exceptions, package/checklist projection, and denial evidence.
3. Confirm terminal custody consumes the exact retained Compliance material with a distinct Company
   Secretary and does not re-encrypt/rewrite the retained number.
4. Confirm migration constraints keep one cheque per package, a unique lookup hash, bounded
   collected/held status, distinct maker/checker, and null later-lifecycle facts.
5. Re-run the declared PostgreSQL class twice and inspect sole-winner request/actor/workflow plus
   loser-request absence assertions.

## Traceability

- V10 p.14 and Epic 008 digest say one blank-dated cheque is security and the cancelled cheque
  verifies the applicant account; auth §16.4/V10 p.6 give Company Secretary custody. Code resolves
  the application-retained bank/cancelled-cheque decision, allows Compliance collection and distinct
  Company Secretary held custody. Verified by the public create/custody, stale/conflict, provenance,
  projection, and PostgreSQL race tests.
- API contracts §28.6 names POST/GET/PATCH and the seven request fields. Code implements those exact
  routes/fields, six-digit number, non-future collection date, collected/held states, and strict
  unknown/later-lifecycle rejection. Verified by the API matrix.
- Data model §17.5/§29 requires encrypted cheque plus lookup hash, protected package/member/bank/file,
  indexed status/date, custody, and restricted defaults. Migration 0005 implements these with
  null-only invocation/presentation/return constraints. Verified by migration sync and full tests.
- Security/privacy and slice rules require masked ordinary reads and separately audited reveal.
  Code reuses `shared.encryption` and `documents.modules.sensitive_data_access`, with no-store,
  scope/reason/rate/expiry, success/denial audit, and missing-key closure. Verified by RED/GREEN
  cycle 3 and reveal authority tests.
- Slice acceptance says capture must not complete checklist or change readiness/bank/loan facts.
  Code projects only the masked version ledger and locks the pending item without overwriting its
  owned fields. Verified by the replay/projection preservation test.

## Gate evidence

- `evidence/terminal-logs/tdd-red-cycle-{1,2,3}.txt` and matching green logs.
- `evidence/terminal-logs/scoped-api-boundary-tests.txt`: 11/11 pass.
- `evidence/terminal-logs/postgresql-race-run-{1,2}.txt`: 2/2 pass twice, zero skips.
- `evidence/terminal-logs/backend-full-tests.txt`: 849 pass, 38 expected SQLite skips.
- `evidence/terminal-logs/backend-coverage-report.txt`: 92%, floor 85%.
- Django check/migration sync and frontend lint/typecheck/293 tests/build logs are green.

## Recommended next action

Run independent validation. If green, let the orchestrator commit/merge/push, then run the due
architecture review before 008K.
