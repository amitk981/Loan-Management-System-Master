# Risk Assessment

Selected slice: `003D-secure-document-download-with-audit`

Mode: `normal_run`

Risk level: Medium

## Why Medium
- Adds a protected document-access endpoint for potentially sensitive files.
- Touches shared authentication behavior used by multiple protected backend views.
- Writes audit events for document access.

## Controls Applied
- Session-bound Bearer auth is required through the shared `http_auth` helper.
- Download requires `documents.file.download`; upload permission does not grant download.
- Failed auth, permission, and not-found requests do not write document-download audit rows.
- Not-found and failure responses do not leak document metadata.
- Success response includes only `download_url` and `expires_at`, never `storage_key`, checksum, raw bytes, or rendered content.
- Audit metadata omits storage key, checksum, signed secrets, and raw bytes.
- Sensitivity-specific object rules are recorded as A-020 until the source role/sensitivity matrix is implementable.

## Validation Evidence
- TDD red: `evidence/terminal-logs/red-document-download-test.log`
- TDD green: `evidence/terminal-logs/green-document-download-test.log`
- Targeted document/auth regressions: 26/26 passed.
- Backend tests: 144/144 passed.
- Backend coverage: 97%, above 85% floor.
- Backend check and migration sync passed.
- Frontend typecheck, lint, tests, and build passed.

## Residual Risk
- Local adapter descriptors are not true object-store signed URLs. This is documented in A-020 and `API_CONTRACTS.md`; production storage signing remains future adapter work.
- Public/internal/confidential/restricted documents currently share the same generic `documents.file.download` gate until source docs define a concrete sensitivity matrix.

Manual review required: no beyond normal Ralph/orchestrator validation.
