# Slice 012E3: Field-Encryption Key Separation and Rotation

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, and UAT
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Separate sensitive-field encryption from the general Django `SECRET_KEY` with dedicated, versioned keys plus rotation and recovery evidence. Current identity-field protection derives from the application secret, while the source separates application, JWT, field, storage, and backup keys (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## User Value
Rotating or leaking the application secret does not expose or brick PAN/Aadhaar and other encrypted identity data; key custody matches the security specification.

## Depends On
- 012E2

## Source References
- docs/source/security-privacy.md key management, encryption-at-rest, and key-separation requirements
- docs/source/deployment-ops.md secret provisioning expectations
- docs/source/data-model.md encrypted field inventory (PAN/Aadhaar and related sensitive columns)
- docs/slices/004I-sensitive-masking-and-reveal-audit.md (current reveal/masking contract)

## Prototype Reference
None (backend/security slice).

## Concrete Requirements
1. Introduce a dedicated field-encryption key, provisioned via environment/secret store, independent of `SECRET_KEY` and the JWT signing key; document custody in deployment-ops working notes.
2. Key versioning: ciphertexts record the key version; decryption supports current plus previous versions during rotation.
3. Rotation path: a management command re-encrypts all affected columns from version N to N+1, idempotent and resumable, with row-count reconciliation evidence; run it in tests against fixture data.
4. Migration from the current SECRET_KEY-derived scheme: one-time re-encryption of existing data with reconciliation proof; no window where data is unreadable or plaintext.
5. Fail-closed startup check: production settings refuse to boot when the field key is missing/malformed; development keeps a safe local default clearly marked non-production.
6. Backup/recovery note: document which key versions must be retained to read backups; record in RELEASE_PROMOTION.md or deployment notes.
7. Masking/reveal (004I) behaviour unchanged; reveal audit events unaffected.

## Test Cases
- Encrypt/decrypt round-trip per key version; old-version ciphertext readable during rotation.
- Rotation command re-encrypts fixtures with reconciliation counts and is safely re-runnable.
- Production settings without the key fail to start; with the key, boot succeeds.
- Regression: no sensitive field falls back to SECRET_KEY-derived encryption.

## Out of Scope
Storage/backup encryption implementation (deployment scope, 012H+), JWT key rotation procedures (auth hardening owns), HSM/KMS integration beyond env-provisioned secrets (record as assumption if required).

## Risk Level
High

## Acceptance Criteria
- Sensitive-field encryption is provably independent of the application secret, rotatable with evidence, and fail-closed in production.
- All gates pass; rotation/reconciliation output saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] Database rules followed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
