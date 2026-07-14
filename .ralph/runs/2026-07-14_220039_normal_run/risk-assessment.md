# Risk Assessment

Risk level: High

- Selected slice: `008H-sh-4-physical-share-security-workflow`
- Mode: `normal_run`
- Standing approval: applicable; no 008H revocation exists.

## Material risks and controls

- Security custody and maker-checker identity: Compliance owns preparation/current-maker facts;
  only a distinct active Company Secretary can record terminal custody, and the checker must differ
  from the SH-4, current stamp, and current signature makers.
- Legal evidence integrity: signed/custody states consume only current-renderer SH-4 output, exact
  borrower/witness signatures, and adequate non-legacy stamp evidence through legal-owned selectors.
  Terminal consumption blocks later stamp/signature mutation.
- Object and permission scope: package read and SH-4 mutation permissions remain distinct, canonical
  latest-cycle Stage-4 scope is required, and authority is checked before request shape parsing.
- Database/concurrency: one row per protected package, bounded/check-constrained lifecycle fields,
  null-only invocation/return facts, package row locking, atomic projection/ledger writes, and
  twice-green five-worker PostgreSQL create/custody races.
- Information exposure: responses are metadata-only and provide no storage key, download action, or
  file authority. Audit/version/workflow facts contain ids and attribution, not document bytes.

## Explicit non-effects

No share reservation/decrement, invocation, return, loan account, checklist completion/approval,
package completion, disbursement readiness, frontend, external integration, or nominal stamp amount
was introduced. Missing/mixed frozen share mode remains blocked. No protected/source file changed.

Manual review remains appropriate because this is a Critical-permission security-custody workflow;
independent orchestrator gates and commit/merge/push remain pending.
