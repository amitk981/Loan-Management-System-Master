# Risk Assessment

Risk level: High.

- Selected slice: 010E2-effective-rate-versioning-and-borrower-notices
- Mode: normal_run
- Manual review required: yes; independent Ralph validation remains mandatory.

## Financial and data-integrity risk

Rate history is a financial calculation input. The implementation fails closed on missing or
ambiguous history, serializes activation under PostgreSQL locks, rejects insertion into approved
history, prevents gaps after explicit period closure, and retains immutable invoice/accrual consumer
snapshots. Two real PostgreSQL runs passed the three declared races. Remaining risk is concentrated
in future 010F/010G callers using the consumption interface correctly; they must not bypass it or
recalculate old periods from a current loan field.

## Communication and privacy risk

Activation uses the existing communications dispatcher and requires its send authority. Queueing is
not delivery: pending, retrying, failed, and provider-accepted sent truth remain distinct. Missing
borrower contact creates a visible failed obligation rather than suppressing the duty. Rate audit and
API projections omit contact details and message bodies. Activation requires approved effective
`interest_rate_change_email` and `interest_rate_change_sms` templates when an address is available;
missing template configuration rolls back the local activation/fan-out transaction.

## Concurrency and migration risk

One non-destructive migration adds configuration, loan-history, notice-linkage, and consumption
snapshot tables with period/status/value/uniqueness constraints. The PostgreSQL lock acquires all
existing rate rows in deterministic order, which intentionally serializes rare governance actions.
The cost is acceptable for low-volume configuration changes but should not be reused for high-volume
financial posting. Rollback before production use can reverse the migration; after retained consumer
or delivery evidence exists, rollback requires a governed data-preservation plan.

## Policy risk

Benchmark formula, reset cadence, spread calculation, penal interest, and a broader notice population
are not source-defined. A-145 records the decision to store only supplied metadata, use the approved
explicit effective rate, and notify canonical `active` floating-rate loans. Future governance must
version those policies prospectively and preserve existing calculations/notices.
