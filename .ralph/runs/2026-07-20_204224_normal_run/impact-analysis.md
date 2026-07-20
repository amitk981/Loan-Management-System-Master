# Impact Analysis

## Affected backend pieces

- Configuration owner: effective-rate resolution, current Loan Account projection publication,
  audit/replay evidence, and rate-history validation.
- Loan read composition: canonical list count/window and detail must not suppress a valid account
  solely because its mutable scalar is stale at a successor boundary.
- Interest consumers: invoice, monthly accrual, and capitalisation remain calculation owners but
  must consume the same public effective-rate decision.
- Runtime: the existing Celery worker/beat surface needs one bounded, server-date-only entry point.
- Persistence: one immutable current-rate projection decision is required to enforce exact replay,
  changed-key conflict, cross-account key conflict, and account/version race uniqueness in
  PostgreSQL.

## Blast radius across modules

- `configurations`: High. Financial configuration and immutable evidence are changed; activation,
  rate histories, notices, and historical resolution must remain unchanged.
- `loans` / Loan Account 360 reads: Medium. Selection ordering, permission/object scope, pagination,
  and detail nondisclosure must remain unchanged while stale scalar filtering is corrected.
- `interest`: Medium. No arithmetic changes; focused tests must prove invoice/accrual/capitalisation
  version parity and unchanged replay behavior.
- `processes` / Celery config: Medium. Task discovery and existing communications periodic task must
  remain intact; the new task must delegate only to the public rate owner.
- Frontend and public API shapes: None expected. Existing list/detail envelopes and fields remain
  byte-compatible.

## Regression tests by affected module

- Configuration owner: early future-date rejection, server-date before/date/after convergence,
  exact replay, changed key, cross-account key, competing successor, audit/decision immutability,
  bounded repeated runs, permissions, and five PostgreSQL race tests.
- Loan reads: stale current scalar remains in list count and row, is converged before serialization,
  and detail returns the same current rate without weakening object scope.
- Interest: invoice, accrual, and capitalisation boundary tests assert the retained rate version/rate
  equals the canonical resolver decision.
- Runtime: Celery discovery/beat registration and delegation test for the bounded current-rate owner;
  existing communications task registration remains asserted.

## Data and migration risk

The new evidence table is append-only and additive. It does not rewrite existing Loan Accounts,
interest histories, invoices, accruals, or capitalisations. Database uniqueness is the final arbiter
for competing idempotency/account-version decisions; transaction locks provide deterministic
single-account updates.
