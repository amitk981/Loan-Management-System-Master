# Risk Assessment

Risk level: High

- Selected slice: `010N-global-search-api-and-ui`
- Mode: `normal_run`
- Standing approval: applicable; no `[revoked]` entry was found for 010N.

## High-risk surfaces

- Global search crosses member, application, loan, document, repayment, compliance-provider, and audit boundaries. A scope error could disclose whether another user's record exists.
- PAN, Aadhaar, bank suffix, and cheque-number inputs are sensitive. Query-string transport, raw-field projection, logging, scanning encrypted columns, or partial matching would create a privacy incident.
- The migration adds searchable suffix/index state to existing member/bank data. An incorrect backfill could make exact suffix lookup incomplete or unindexed.
- Server-projected quick actions cross frontend module routes and must not imply authority the backend did not grant.
- The UI and Header previously built a browser-side index over mock sensitive data; incomplete removal would retain the original leak.

## Controls implemented

- Search is a read-only authenticated POST whose JSON body is not included in Django access paths or browser history. Request validation rejects short, oversized, wildcard, control-character, unknown-field, and malformed inputs; actor-keyed cache throttling returns a safe 429 after 30 requests/minute.
- PAN/Aadhaar exact lookup uses the existing keyed identity hash. Cheque lookup uses the owning `FieldEncryption.hash_for_lookup` namespace. Aadhaar/bank suffixes and share count use stored indexed columns; no encrypted value is decrypted or scanned.
- Member scope is applied before related matches become results. Applications reuse application authority; accounts/repayments reuse the canonical account candidate selector; documents require both document and application-read authority; audit requires its separate high-risk permission. Denied groups are absent, including counts.
- Every group is capped at 100, independently paginated, deterministically ordered, and projected through one non-sensitive card contract. The compliance provider is registered but default-empty until 011M3 owns real rows.
- One non-destructive migration adds/backfills `aadhaar_last4` from authenticated token metadata and adds the measured suffix/share indexes. Migration sync is green; query-plan assertions show index searches for PAN, Aadhaar, Aadhaar last four, share count, and bank last four.
- Header no longer imports or searches `mockData`; S02 uses the shared authenticated transport and transient component state only. Static scans confirm no local search index, URL/local-storage query caching, or raw-sensitive response fields.

## Residual risk and independent gates

- The cache backend determines whether throttling is process-local or shared in a multi-worker deployment; production must use its configured shared cache for a globally enforced actor limit.
- Name-prefix search relies on the database's indexed text behavior; exact sensitive/suffix paths have explicit query-plan evidence, while representative PostgreSQL performance remains part of deployment monitoring.
- Chromium was not launched inside the coding sandbox. The exact declared Playwright spec collects successfully and requires `global-search-results.png` and `global-search-empty.png`; Ralph's trusted localhost browser contract must run it twice and is authoritative.
- Compliance records remain deliberately absent until dependency-ordered 011M3 registers a provider using `build_result_card`; complete seven-group S02 acceptance is not claimed here.

## Conclusion

The candidate is suitable for independent High-risk validation. No protected files, source documents, external services, deployments, or Git metadata were changed.
