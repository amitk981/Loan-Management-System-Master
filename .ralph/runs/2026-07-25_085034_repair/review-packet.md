# Review Packet: 2026-07-25_085034_repair

## Result
Ready for independent validation

## Slice
012G-critical-e2e-uat-smoke-scenarios

## Authoritative Failure Repaired

The trusted browser reached `UAT-014/015/016/017` but the FY2026-27 interest-invoice request
returned 409. A focused public-API reproducer proved the critical seed lacked the one approved
invoice calculation configuration required by the real service. The E2E spec also used Credit
Manager for the Accounts-owned action.

## Candidate Repair

- Seed one deterministic, immutable FY2026-27 invoice configuration.
- Propose and canonically activate one approved rate covering the full invoice period.
- Exercise invoice creation as the seeded Accounts actor and restore Credit Manager before the
  subsequent DPD/default steps.
- Retain the existing guarded seed boundary and all production permission/business contracts.

## Traceability

The source says interest invoice/capitalisation UAT belongs to Accounts and requires configured
rate snapshots, server-owned financial outcomes, idempotency, and public-boundary evidence
(`docs/source/test-plan.md` §§16.13, 20.3, 27.1-27.2, 29.4;
`docs/source/product-requirements.md` §§11.24, 11.32). The candidate supplies only deterministic
test preconditions, uses the Accounts actor, and verifies the public invoice response in
`CriticalUatE2eSeedTests.test_seed_is_idempotent_and_builds_only_public_journey_preconditions`.

## Evidence

- Exact RED: `evidence/terminal-logs/critical-interest-precondition-red.log`
- Exact GREEN: `evidence/terminal-logs/critical-interest-precondition-green.log`
- Focused backend: `evidence/terminal-logs/backend-focused-green.log` (6 passed)
- Django/migrations: `evidence/terminal-logs/backend-check-migrations-green.log`
- Focused frontend: `evidence/terminal-logs/frontend-seed-focused-green.log` (5 passed)
- Typecheck/lint/build: `evidence/terminal-logs/frontend-typecheck-green.log`,
  `frontend-lint-green.log`, `frontend-build-green.log`
- Playwright collection: `evidence/terminal-logs/critical-uat-spec-collection-green.log`
- Diagnosis: `evidence/repair-diagnosis.md`

## Independent Validation Note

Two post-fix exact Playwright attempts ended at `browserType.launch` before a page existed. Those
infrastructure logs are retained as `trusted-browser-acceptance-green.log` and
`trusted-browser-acceptance-green-2.log`. They contain no application assertion and produced no
screenshots; none were fabricated. Independent trusted validation must run the declared spec and
produce `critical-uat-standard-loan.png` and `critical-uat-permission-negative.png`.

## Recommended Next Action
Run the full independent validator against the preserved candidate. If Chrome launches, require
the complete declared spec, both screenshot manifests, and the normal risk-selected gates.
