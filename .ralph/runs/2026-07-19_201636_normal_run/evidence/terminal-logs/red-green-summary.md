# TDD Red/Green Evidence

All backend commands used `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

## Transfer checksum nondisclosure

- RED: the public checksum-drift regression observed `(total_count=1, one list row, detail=200)`
  where `(0, empty, 404)` was required.
- GREEN: after binding the transfer document checksum in the post-transfer selector, the exact
  regression passed and the existing mutation owner continued to reject the stale identity.

## Stale Senior Finance initiation

- RED: the combined workspace returned `(total_count=1, rows=[])` for a retained stale initiation.
- GREEN: after adding the pre-pagination initiation identity filter, the exact regression returned
  `(0, [])`; the approved-drift regression also asserts a zero total.

## Runtime fixture boundary

- RED: strengthened runtime source inspection found the production builder importing
  `sfpcl_credit.tests` and depending on `TestCase` setup/private helpers.
- GREEN: source-boundary and real endpoint/idempotency tests passed with the public synthetic
  fixture builder.

## Legacy SAP checksum reconciliation

- RED: the historical migration-state regression failed because migration `0002` exposed no
  reconciliation callable and left every historical checksum blank.
- GREEN: coherent sent/completed retained-file evidence is backfilled; missing, mismatched, and
  malformed evidence remains blank. The focused migration regression passed.

## Seed family composition

- RED: a real Epic-009-then-portal seed sequence raised the governed `DocumentTemplate` uniqueness
  constraint.
- GREEN: the permanent reverse-order/idempotency regression passed after portal seeding reused the
  existing domain identity.
