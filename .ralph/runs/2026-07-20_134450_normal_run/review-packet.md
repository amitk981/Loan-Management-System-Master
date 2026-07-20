# Review Packet: 2026-07-20_134450_normal_run

## Result
Ready for independent validation

## Slice
`010H2-interest-calculation-payment-and-replay-owner-closure`

## Architecture Finding Closure

- Finding: `AR-010-INTEREST-001`
- Root: `ROOT-010-INTEREST-CALCULATION-OWNER`
- Closure evidence: `review-closure-evidence.md`

The retained reproducer's four failures are closed: calculations segment retained rate/principal
periods, payments are bound through exact schedule applications, capitalisation uses gross interest
less eligible interest payments exactly once without tax/fee leakage, and every owner transition
replays a stored response instead of a live provider projection.

## Source Traceability

- Product requirements §11.24 and user flows §§29.3–29.6 say annual interest, monthly accrual, and
  post-30-April capitalisation must be controlled servicing operations. The code exposes one
  `decide_interest_as_of` seam and keeps the existing invoice/accrual/capitalisation owner
  interfaces. Tests: segmented annual/leap/principal and monthly-rate tests.
- Functional spec BR-060–065 and M10-FR-001–011 require idempotent, auditable interest processing.
  The code stores immutable generation/issuance/posting/capitalisation responses and atomically
  retains account, schedule, ledger, payment, invoice, email, document, audit, and hard-copy task
  truth. Tests: replay, reclassification, and PostgreSQL owner acceptance.
- Data model §§18.5, 19.7–19.9, 34, 35.3 require effective versions and transactional financial
  evidence. Migration `interest.0004_interest_accounting_owner` adds only evidence fields/relations;
  the two PostgreSQL passes verify exact/changed-key races.
- API contracts §45.2 says exact idempotent replay returns the original response. Later SAP or
  communication status changes now leave `original_response` byte-stable; changed and cross-owner
  keys retain conflict/zero-write behavior.

In plain language: the source says interest must be calculated from the facts that were true on each
day and capitalised only once after the cutoff. The implementation records those daily-boundary
facts and the exact payments used, and the tests prove later rate, SAP, or email changes cannot
rewrite the original financial answer.

## Verification

- Focused reverse consumers: 44 tests passed, exit 0.
- PostgreSQL acceptance pass 1: 5 tests passed, exit 0.
- PostgreSQL acceptance pass 2: 5 tests passed, exit 0.
- Django system check: exit 0.
- Migration drift check: no changes detected, exit 0.
- `git diff --check`: clean.
- The complete backend suite/coverage was deliberately not run locally; Ralph performs it once as
  the authoritative independent gate.

## Scope and Design Review

- No frontend/API route redesign and no new dependency.
- The deep module interface is one as-of decision; configuration and loan modules expose bounded
  rate/principal period readers rather than leaking their private models to callers.
- Existing general interest-module split debt remains deferred to Epic 010 closure as required.
- Current product diff is within the 2,000-line, 30-file, four-dependency, and one-migration limits.

## Recommended Next Action
Run Ralph's independent complete backend coverage, migration, protected-path, diff-limit, and
declared PostgreSQL capability gates; commit/merge only if they all pass.
