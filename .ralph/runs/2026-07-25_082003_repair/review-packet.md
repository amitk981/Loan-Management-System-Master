# Review Packet: 2026-07-25_082003_repair

## Result
Ready for independent validation

## Slice
012G-critical-e2e-uat-smoke-scenarios

## Recommended Next Action
Run the exact trusted-browser validator twice from fresh seeds. Confirm the repaired subsidiary
request returns HTTP 200, complete every subsequently exposed assertion in the same validator
domain, and retain both declared screenshot manifests. Then run the orchestrator-selected backend
and reverse-consumer/security lanes.

## Authoritative Failure Repaired

- The trusted browser previously reached the application and failed at
  `critical-uat-smoke.e2e.spec.ts:227`: subsidiary repayment returned 409 instead of 200.
- Diagnosis found the retained synthetic tri-party agreement was still `pending` execution, so the
  canonical current-evidence selector returned no agreement.
- The critical seed now advances only that retained synthetic agreement to `executed`, validates
  it through the canonical selector, and fails closed if the owner-backed fixture is missing or
  otherwise invalid.

## Verification

- TDD RED: canonical tri-party precondition was unexpectedly absent.
- TDD GREEN: guarded seed is idempotent and retains current verified agreement evidence.
- Public-boundary regression: seeded Credit Manager login and subsidiary repayment return HTTP 200
  with `pending_statement`.
- Focused backend tests: 6 passed.
- Frontend seed selection/order tests: 5 passed.
- Django system check: passed.
- Migration drift check: no changes detected.
- Frontend typecheck: passed.
- Frontend lint: passed.
- Frontend production build: passed; existing chunk-size advisory only.
- Debug instrumentation: none added.

## Browser Evidence Boundary

The exact slice-specific command was rerun twice during repair. Both current attempts aborted Chrome
before a page existed, and the current browser probe independently showed the same launch failure.
No screenshots or passing browser result were fabricated. The prior orchestrator-owned log remains
authoritative for the post-launch 409; the trusted validator must decide browser acceptance after
this repair.

## Traceability Note

The source says subsidiary repayment requires a tri-party agreement and must be exercised through
the public workflow (`test-plan.md` §16.12 and `product-requirements.md` §11.23). The guarded
critical-UAT seed now exposes the existing synthetic agreement as current executed and verified
loan-term evidence. The public API assertion in
`CriticalUatE2eSeedTests.test_seed_is_idempotent_and_builds_only_public_journey_preconditions`
verifies that the exact seeded actor and subsidiary payload reach `pending_statement` without
weakening production permissions or capture rules.

## Evidence Index

- `evidence/repair-diagnosis.md`
- `evidence/terminal-logs/tri-party-precondition-red.log`
- `evidence/terminal-logs/tri-party-public-api-green.log`
- `evidence/terminal-logs/backend-focused-green.log`
- `evidence/terminal-logs/frontend-seed-focused-green.log`
- `evidence/terminal-logs/frontend-typecheck.log`
- `evidence/terminal-logs/frontend-lint.log`
- `evidence/terminal-logs/frontend-build.log`
- `evidence/terminal-logs/backend-check.log`
- `evidence/terminal-logs/backend-migrations-check.log`
- `evidence/terminal-logs/trusted-browser-acceptance-1.log`
- `evidence/terminal-logs/browser-infrastructure-probe-current.log`
