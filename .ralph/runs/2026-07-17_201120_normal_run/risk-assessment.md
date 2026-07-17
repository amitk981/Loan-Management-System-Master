# Risk Assessment

Risk level: High

- Selected slice: 009H2-advice-authority-current-truth-and-delivery-closure
- Mode: normal_run
- Standing approval: active; no owner veto is recorded.

## Risk Surface

- The slice sends borrower communication after a successful money transfer and therefore touches
  financial current truth, object authorization, external-provider idempotency, and borrower PII.
- A stale replay could otherwise bless an obsolete recipient/template/provider result, while a
  post-acceptance rollback could otherwise duplicate the logical email.
- The permission catalogue previously granted the source-forbidden CFC edge and omitted Credit
  Manager, and PostgreSQL locking differs materially from SQLite.

## Mitigations Verified

- The exact 009G2 pending UUID is reused as communication and provider/outbox identity; canonical
  payload facts and the Manual/Fake receipt are stable across fresh adapter instances.
- A forced failure after provider acceptance rolls back all sent truth, leaves the intent pending,
  and a fresh-adapter retry returns the same provider id/status/time before persisting one ledger.
- First send/replay lock and reconcile canonical email, current approved/effective template and
  rendering, provider facts, sender role/team, transfer/register/intent, audit/action/workflow, and
  request/network evidence. Drift conflicts without resend or new ledgers.
- Senior Finance requires exact initiating-maker and current SAP-assignee relations; Credit Manager
  requires canonical active-loan/application scope; CFC-only, wrong-scope, inactive, missing-grant,
  permission-only, and role-only paths are denied.
- Full email is retained only on the protected communication row. Audit uses a mask and digest;
  workflow/audit/content contain no full UTR.
- Both PostgreSQL race methods passed twice after the first run exposed and the repair corrected a
  nullable-join row-lock error. Forty-three impacted backend tests and all frontend gates pass.

## Residual Risk

- Manual/Fake adapters prove the source-required stable contract without calling a real provider;
  future SMTP/API adapters must preserve provider-side idempotency for the same interface.
- The orchestrator still owns complete backend coverage/floor, protected-path, queue, and repeat
  independent validation before commit/merge.
