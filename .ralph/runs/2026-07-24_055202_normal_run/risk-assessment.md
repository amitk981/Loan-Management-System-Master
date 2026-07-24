# Risk Assessment

Risk level: High

- Selected slice: 012C-export-masking-and-permission-checks
- Mode: normal_run
- Manual review required: yes; independent Ralph validation is required before commit.

## Security and Privacy Risks

- Sensitive output could bypass masking through a format-specific renderer. Mitigation: one central
  row projection runs before every renderer, with parsed CSV/JSON/XLSX/PDF tests for PAN, Aadhaar,
  bank account, cheque, and BO-account families.
- General export authority could imply sensitive authority. Mitigation:
  `reports.export_sensitive` is a separate Critical permission seeded with no role grant; safe
  nonblank reason is mandatory whenever unmasked output is explicitly requested.
- Idempotency replay could cross masking modes. Mitigation: replay compares classification,
  requested columns, masking mode, and reason digest and rejects a mismatch without creating a
  second job.
- Signed URL possession could outlive authority. Mitigation: status/download are actor-bound,
  current export/sensitive authority and the owning report selector are re-run, and expiry,
  revocation, invalid grant, cross-user, and unknown-job attempts fail closed and are audited.
- Audit or job metadata could retain secrets. Mitigation: jobs retain reason digest rather than
  reason text; audits never include rows, filter values, raw sensitive values, idempotency keys,
  storage keys, or tokens. The reason itself is stored only after central safe-audit-text
  validation.
- Repeated export attempts could become an exfiltration signal. Mitigation: the established
  actor-keyed cache throttle limits requests to 30 per 60 seconds and records safe rate metadata.

## Data and Migration Risks

- One additive migration extends `report_export_jobs` with classification, requested/permitted
  columns, masking decision, reason digest, and authority snapshot. It is non-destructive.
- Existing rows migrate with `confidential` as the conservative snapshot. Future current-access
  checks still fail closed if a job's classification does not match central policy.
- No plaintext sensitive data is added to the database.

## Governance Risk

- Source §32.3 does not classify every implemented report. A-172 records the conservative
  classification mapping and requires future governance confirmation. The mapping cannot grant
  access or reduce masking.
- Bulk KYC unmasking remains denied because the highest approved authority is unresolved.
- `audit.export` and `reports.export_sensitive` are granted to no role.

## Verification Risk

- Focused export tests, adjacent report/audit/download/catalogue tests, and existing reveal tests
  pass. Django system and migration checks pass.
- No frontend files changed, so frontend typecheck/lint/build are not impacted.
- The agent deliberately did not run the complete backend suite or coverage lane. The Ralph
  orchestrator must run the authoritative High-risk fail-closed validation before commit.
