# Slice 012E3: Field-Encryption Key Separation and Rotation

## Status
Complete

## Parent Epic
Epic 012: Reports, Exports, Hardening, and UAT
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Separate sensitive-field encryption from the general Django `SECRET_KEY` with dedicated, versioned keys plus rotation and recovery evidence. Current identity-field protection derives from the application secret, while the source separates application, JWT, field, storage, and backup keys (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## User Value
Rotating or leaking the application secret does not expose or brick PAN/Aadhaar and other encrypted identity data; key custody matches the security specification.

## Depends On
- 012E2
- 008I4

## Runtime Capabilities

- `none`

## Source References
- docs/source/security-privacy.md key management, encryption-at-rest, and key-separation requirements
- docs/source/deployment-ops.md secret provisioning expectations
- docs/source/data-model.md encrypted field inventory (PAN/Aadhaar and related sensitive columns)
- docs/slices/004I-sensitive-masking-and-reveal-audit.md (current reveal/masking contract)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012E2 / §012E3

## Prototype Reference
None (backend/security slice).

## Concrete Requirements
1. Extend the central `shared.encryption` interface established by 008I4; do not create a second
   field-encryption module. Introduce a dedicated field-encryption key, provisioned via
   environment/secret store, independent of `SECRET_KEY` and the JWT signing key; document custody
   in deployment-ops working notes.
2. Key versioning: ciphertexts record the key version; decryption supports current plus previous versions during rotation.
3. Rotation path: a management command re-encrypts all affected columns from version N to N+1, idempotent and resumable, with row-count reconciliation evidence; run it in tests against fixture data.
4. Migration from the current SECRET_KEY-derived one-way identity tokens and any retained older
   field formats: one-time governed migration where reversible source truth exists, with
   reconciliation proof and no window where data is unreadable or plaintext. Preserve 008I4 CDSL
   ciphertexts through the shared key-version interface rather than reimplementing them.
5. Fail-closed startup check: production settings refuse to boot when the field key is missing/malformed; development keeps a safe local default clearly marked non-production.
6. Backup/recovery note: document which key versions must be retained to read backups; record in RELEASE_PROMOTION.md or deployment notes.
7. Masking/reveal (004I) behaviour unchanged; reveal audit events unaffected.

## Test Cases
- Encrypt/decrypt round-trip per key version; old-version ciphertext readable during rotation.
- Rotation command re-encrypts fixtures with reconciliation counts and is safely re-runnable.
- Production settings without the key fail to start; with the key, boot succeeds.
- Regression: no sensitive field falls back to SECRET_KEY-derived encryption.
- Regression: CDSL BO-account and blank-cheque adapters still cross the same shared encryption and
  sensitive-reveal seams after whole-repository rotation support lands.

## Out of Scope
Storage/backup encryption implementation (deployment scope, 012H+), JWT key rotation procedures (auth hardening owns), HSM/KMS integration beyond env-provisioned secrets (record as assumption if required).

## Evidence Required
Saved RED/GREEN key-version, missing-key startup, rotation/resume, reconciliation, and legacy-format
output; no-plaintext/no-SECRET_KEY fallback proof; CDSL and reveal-audit reverse-consumer results;
backup key-retention note and configured full gates.

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
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
