# Review Packet: 2026-07-15_011600_normal_run

## Result

Ready for orchestrator dependency installation and independent validation.

## Slice

`008I4-sensitive-field-encryption-and-cdsl-null-contract-closure`

## What changed

- Added the `shared.encryption.FieldEncryption` AES-GCM interface with independent current/previous
  keys, lookup HMAC, field binding, masking metadata, and strict configuration failures.
- Added the central `documents.modules.sensitive_data_access` owner for CDSL masking, reveal reason,
  permission/role, canonical object access, expiry, rate/re-auth decisions, and sensitive audit.
- Extended the immutable coordinator contract with a central masking callback and locked reveal;
  strengthened the AST boundary to reject security imports of documents as well as legal/approvals.
- Added one idempotent retained-row migration from `seal:v1` with count/hash/last-four reconciliation
  and removed the legacy reversible production adapter.
- Restored nullable pending evidence through public POST/PATCH while preserving terminal evidence,
  exact replay, masked projections, and side-effect exclusions.

## Traceability for a non-developer

- Codebase design §§9.4/39.1-39.2 says encryption and sensitive reveal belong behind central deep
  interfaces. Code adds those exact owners; `FieldEncryptionTests` and the CDSL reveal tests verify
  field-bound encryption, rotation, tamper/wrong-key failures, authority, expiry/rate/re-auth, and
  plaintext-free audit.
- Data model §§17.4/29 says CDSL evidence is nullable and BO accounts are encrypted, hashed, and
  masked. `test_pending_pledge_accepts_null_evidence_and_projects_null_metadata` verifies pending
  null POST/PATCH plus zero-write terminal rejection; the migration regression verifies retained
  count/hash/last-four reconciliation.
- Auth §§6.5/12.8/19.4/21 says reveal needs explicit permission, object scope, reason, short-lived
  return, and audit. `test_explicit_company_secretary_reveal_is_one_time_and_separately_audited`
  and `test_central_reveal_validates_reason_and_denies_lost_object_scope` cover that matrix.
- Deployment §§9.2/10 separates field keys from Django/JWT secrets. The missing-key regression
  proves there is no `SECRET_KEY` fallback; 012E3 remains responsible for production secret-store
  boot enforcement and repository-wide rotation.

## Validation evidence

- RED nullable crash: `evidence/terminal-logs/008i4-red-null-evidence.log`
- GREEN nullable tracer: `evidence/terminal-logs/008i4-green-null-evidence.log`
- RED repeated reveal: `evidence/terminal-logs/008i4-red-central-reveal-rate.log`
- Encryption RED/dependency-pending: `evidence/terminal-logs/008i4-red-field-encryption.log` and
  `008i4-green-field-encryption-dependency-pending.log`
- Static: Python compile, dependency-boundary, production plaintext/legacy scan, and local database
  scan logs under `evidence/terminal-logs/`
- Frontend: lint/typecheck/build clean; 293 tests pass.
- Backend: check/migration/full coverage logs all record only the expected absent newly pinned
  `cryptography` module. Independent validation must rerun focused/full/PostgreSQL twice after install.

## Recommended next action

Install from `sfpcl_credit/requirements.txt`, run independent configured gates including the
declared PostgreSQL races twice, then let Ralph commit/merge/push. Next eligible slice is sharpened
008J.
