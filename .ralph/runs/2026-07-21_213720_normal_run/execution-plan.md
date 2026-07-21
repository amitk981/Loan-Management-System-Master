# Execution Plan

Selected slice: 010N3-interest-portfolio-completeness-closure

## Scope and permissions

- Modify only permitted frontend modules/tests and this run's evidence artifacts.
- Preserve the existing interest-management visual patterns; introduce no new styling or backend
  business rules.
- Keep the canonical backend interest owner responsible for permission, object scope, money,
  eligibility, and idempotency decisions. The client may submit only explicit, disclosed batches of
  canonical loan identifiers already returned by that owner.

## TDD tracer bullets

1. RED then GREEN: add a shared authenticated complete-pagination interface that traverses 1/100/101
   records and rejects malformed, discontinuous, or changing pagination instead of returning a
   partial collection.
2. RED then GREEN: add loan/invoice complete-collection adapters and a portfolio-accrual interface
   that submits explicit batches of at most 100, uses stable per-batch replay keys, combines results,
   and exposes partial progress if a later batch is denied or fails.
3. RED then GREEN: update Interest Management component tests for record 101 reachability, canonical
   count/page/batch disclosure, backend available-action gating, replay, denial, and visible partial
   failure; minimally wire the page to the new interfaces.

## Verification and evidence

- Save each focused RED and GREEN command/output under `evidence/terminal-logs/` using the required
  frontend test selectors.
- Run the original architecture-review reproducer command exactly and retain its green output.
- Run focused frontend tests, typecheck, lint, and build; save concise evidence.
- Inspect targeted diff/stat, complete `risk-assessment.md`, `review-closure-evidence.md`,
  `review-packet.md`, and `final-summary.md`.
- Run the exact review-closure validator repeatedly until it prints PASS.
