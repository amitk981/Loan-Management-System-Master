# Review Packet: 2026-07-24_135028_normal_run

## Result
Ready for independent validation

## Slice
012E3-field-encryption-key-separation

## What changed

- Extended the established `sfpcl_credit.shared.encryption` owner with a repository-wide encrypted
  field registry and `rotate_field_encryption` management command.
- Moved member/nominee/witness/signatory identity values, bank/cancelled-cheque account values,
  lookup hashes, and E2E seed values away from `SECRET_KEY`-derived protection.
- Added production fail-closed validation for explicit current/previous field keys, key custody
  reference, and the separate lookup key.
- Preserved legacy `members.pan`/`members.aadhaar` authenticated ciphertext reads while new writes
  use canonical identity contexts. One-way legacy values are preserved and reported, never guessed.
- Added field-key custody, rotation, rollback, reconciliation, and backup-retention operations notes
  and linked them from release promotion.

## Source-to-code traceability

| Source requirement | Implementation | Verification |
|---|---|---|
| `security-privacy.md` §§14–15 says sensitive fields are encrypted, key types are separate, ciphertext carries a key version, new writes use the active version, and old versions remain readable during migration. | `shared.encryption`, `members.protected_identity`, production settings, and the encrypted-field registry use dedicated AES-GCM/lookup keys with current and previous versions; no sensitive runtime owner references `SECRET_KEY`. | `test_field_encryption`; `no-secret-key-fallback-proof.log` |
| `security-privacy.md` §15.3 requires background re-encryption and rollback planning. | `rotate_field_encryption` scans every registered encrypted model column, atomically compare-and-swaps rows, emits checkpoints/reconciliation, and safely reruns or resumes. | `test_field_encryption_rotation`; rotation and resume RED/GREEN logs |
| The selected slice requires migration of reversible older values and explicit handling where source truth is unavailable. | Raw reversible retained values are immediately re-encrypted and lookup hashes rebuilt; one-way `enc:v1`/`seal:v1` values remain unchanged and are counted as `legacy_unrecoverable`. | `test_rotation_recovers_plaintext_legacy_and_reports_one_way_tokens`; legacy RED/GREEN logs |
| `deployment-ops.md` §§9–10 requires secret-manager provisioning, separate custody, audit, rotation, and a recovery plan. | Production requires explicit secret projections and rejects local defaults; `FIELD_ENCRYPTION_OPERATIONS.md` assigns Security/DevOps custody and defines rotation, rollback, reconciliation, and recovery. | Production-startup RED/GREEN; operations note |
| `security-privacy.md` §27 and `deployment-ops.md` §21 require encryption keys in secure backup recovery. | The operations/release notes require retention of every version needed by live ciphertext or any restorable backup, separately from backup-encryption keys. | `FIELD_ENCRYPTION_OPERATIONS.md`; `RELEASE_PROMOTION.md` |
| Slice 004I and 008I4 behavior must remain unchanged for masking/reveal audits and CDSL/blank cheque. | Member reveal decrypts only for the immediate response and retains metadata-only auditing; CDSL, blank-cheque, SAP, search, governance, and seed consumers still pass. | 111-test reverse-consumer pack and focused CDSL/cheque log |

## Focused validation

- 13 encryption/rotation tests passed.
- 111 identity, governance, search, bank, member reveal, SAP, production isolation, and E2E seed
  tests passed; 5 environment-specific tests were skipped by their existing conditions.
- Focused CDSL and blank-cheque reveal regressions passed.
- `manage.py check`, `makemigrations --check --dry-run`, Python compilation, and `git diff --check`
  passed.
- The complete backend suite and coverage were deliberately not run by the implementation agent;
  Ralph independent validation owns the High-risk authoritative full lane.

## Review focus

- Confirm the registered model/column/context inventory is acceptable as the single rotation
  boundary and that a restored-backup drill retains every referenced key version.
- Treat any non-zero production `legacy_unrecoverable` result as an explicit remediation item; do
  not accept a plaintext, application-secret, or guessed-value fallback.
- Verify the independent complete-suite coverage lane and protected-path/diff checks.

## Recommended Next Action
Run Ralph independent High-risk validation; if green, commit and merge through the orchestrator.
