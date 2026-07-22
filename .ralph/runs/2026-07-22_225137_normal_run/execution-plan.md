# Execution Plan

Selected slice: 011I-security-return-and-cdsl-unpledge-tracking

## Permission Check

- Writable scope: `sfpcl_credit/**`, `docs/working/**`, and this run's `.ralph/runs/2026-07-22_225137_normal_run/**` evidence.
- Read-only/untouched: `docs/source/**`, workflow scripts/config/permissions, Git metadata, orchestrator state/progress, and the selected slice status.
- Owner veto: none recorded for 011I. No new dependency is planned.

## Module Shape

- Keep one public closure interface for recording the return; it derives applicability and identity from the closure's security package.
- Keep custody facts in the existing SH-4, blank-cheque, and PoA owners, and put CDSL result validation/update behind the existing CDSL module seam.
- Persist one aggregate plus immutable item/transition evidence and expose only masked BO/account values.

## TDD Behaviours (one RED -> minimal GREEN at a time)

1. Physical-only closed loan derives required items and completes only with recipient, return facts, and governed acknowledgement.
2. Demat-only flow validates package/PSN/evidence, records full/partial URF and DP outcome through the CDSL owner, and cannot complete on pending/rejected/owner failure.
3. Mixed and no-security closures derive aggregate state without trusting caller applicability; missing item evidence remains pending.
4. Pre-close, mismatched/foreign evidence, wrong role/scope, and sensitive-value disclosure are rejected and audited.
5. Exact replay is zero-write; changed replay and stale concurrent updates conflict while item/aggregate state remains monotonic.
6. PostgreSQL same/different request races preserve one return and one complete transition; retain exactly two tests under the declared acceptance label.

## Implementation and Validation

- Add the closure models and single migration, then route/view/domain interface and security-owner integration.
- Update the maintained working API contract for the richer item/result request and masked response.
- Save each focused RED/GREEN command under `evidence/terminal-logs/` using the mandated Ralph Python interpreter.
- Run focused closure/security/reverse-consumer tests, PostgreSQL acceptance when available, Django check, and migration-sync check. Do not run the complete backend suite locally.
- Inspect targeted diff/stat, then complete risk assessment, traceability/review packet, and final summary. Set review result exactly to `Ready for independent validation` only after focused gates are green.
