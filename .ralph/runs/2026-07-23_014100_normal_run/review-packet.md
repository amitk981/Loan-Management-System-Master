# Review Packet: 2026-07-23_014100_normal_run

## Result
Ready for independent validation

## Slice
011K-compliance-control-tracker-foundation

## Scope and traceability
The source requires owner/frequency/due/evidence controls, one task per period, maker-checker review,
overdue escalation, and annual money-lending evidence (`functional-spec.md` M14; API §§37.1-37.4,
37.7). The compliance models and `ComplianceTaskEngine` implement those behaviors; focused tests in
`test_compliance_task_engine.py`, `test_compliance_api.py`, and the exact PostgreSQL acceptance class
verify them. Existing document, scheduler, notification, audit, stamp, recovery, and archive owners
remain authoritative; reverse-owner tests are green.

## Independent review
Standards and spec reviews initially found lifecycle, scope, persistence, exact-evidence, effective-
dating, notification uniqueness, and action-projection gaps. The candidate now transitions existing
due tasks to overdue, binds FY/task/evidence identity, persists current evidence and control versions,
locks audited writes, scopes lists/actions, validates cross-owner source references, and uses durable
task notification pointers. R7 is deliberately source-mapped (the slice permits seed/source-map).

## Verification
Combined compliance/catalogue/archive/stamp/recovery: 53 tests OK (2 documented skips). Django
check, compile, migration sync, and diff check are green.
Ralph should run the declared PostgreSQL acceptance and authoritative selected backend lane.
