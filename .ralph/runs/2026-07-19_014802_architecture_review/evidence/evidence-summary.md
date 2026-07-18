# Architecture Review Evidence Summary

## Reviewed Product Commits

`35dd95ce`, `4bdff96c`, `9b1113af`, and `4bebe1af`, after the prior reviewed product boundary
`e3d965ad`. Owner-maintenance commit `4fb0a5af` is outside product-slice attribution.

## Retained Regression Checks

- `terminal-logs/focused-reviewed-backend-tests.log`: 74 focused migration, worker, channel,
  provider-evidence, exception, and MP14 backend tests pass; six PostgreSQL-only race tests skip in
  the local SQLite lane.
- `terminal-logs/focused-reviewed-frontend-tests.log`: 10 MP14 and portal-selection tests pass.

## Independent Contract Probes

`review-probes/review_contract_probes.py` contains three read-only defect reproductions. All fail
on the intended contract assertion:

1. a blank required frozen-template fact with a recomputed checksum is promoted to `verified`;
2. advice-only authority reads a generic exception; and
3. advice-only authority resolves a generic exception.

Raw output is `terminal-logs/review-contract-probes.log`. The 200 response bodies also prove the
current dotted adapter path in `provider_code`. These failures support corrective slice 009H9D and
are not acceptance failures for review-authored product code.
