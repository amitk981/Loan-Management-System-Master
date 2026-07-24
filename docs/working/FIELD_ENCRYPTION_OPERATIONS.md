# Field-Encryption Key Operations

This is the deployment working note for the field-encryption custody and rotation controls required
by `security-privacy.md` §§14–15 and `deployment-ops.md` §§9–10, 21.

## Custody and configuration

Field-encryption keys are independent of the Django application secret, JWT signing material,
object-storage credentials, and backup-encryption keys. Security/DevOps owns production field keys;
only authorised Security/DevOps operators may read or update them. Secret-manager access and
updates must be audited where the platform supports it. Do not commit, log, paste into evidence, or
store production values in an environment file.

Production requires all of these explicit secret-store/environment projections:

| Variable | Contract |
|---|---|
| `SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION` | Version identifier used by all new writes. It must be non-empty and contain no colon. |
| `SFPCL_FIELD_ENCRYPTION_PREVIOUS_VERSIONS` | Comma-separated readable versions retained during rotation and recovery. It is optional only when no older ciphertext or retained backup needs an older key. |
| `SFPCL_FIELD_ENCRYPTION_KEYS` | JSON object mapping every current/previous version to a URL-safe base64-encoded 32-byte key. |
| `SFPCL_FIELD_ENCRYPTION_KEY_REF` | Non-secret secret-manager custody reference/change-record locator. |
| `SFPCL_FIELD_LOOKUP_KEY` | Separate URL-safe base64-encoded 32-byte HMAC key for exact-match indexes. |

Production settings fail before Django starts when required variables, referenced versions, or key
material are absent or malformed. Local development has clearly marked non-production defaults.
The lookup key is not rotated by the field-ciphertext command: changing it requires a separately
governed rebuild of every affected lookup hash from authorised reversible source truth.

## Planned rotation

For a rotation from `N` to `N+1`:

1. Record the change/incident reference and verify a current encrypted database backup. Confirm the
   recovery secret store contains every key version required by that backup.
2. Generate `N+1` in the production secret manager. Deploy configuration with `N+1` current, `N`
   listed in previous versions, and both mappings present in `SFPCL_FIELD_ENCRYPTION_KEYS`.
3. Boot/smoke the application. New writes now use `N+1`; reads continue to accept `N`.
4. Run:

   ```text
   python manage.py rotate_field_encryption --from-version N
   ```

   Capture the emitted checkpoints and final reconciliation in the change record. `scanned` equals
   `rotated + already_current + legacy_unrecoverable`; `legacy_recovered` is the subset of
   `rotated` values recovered from older reversible plaintext storage. A non-zero
   `legacy_unrecoverable` count identifies retained one-way `enc:v1`/`seal:v1` values: recover them
   only through an authorised source/governance workflow, never by guessing or logging values.
5. If interrupted, rerun the same command; current-version fields are left untouched. To continue
   after a saved checkpoint, pass its exact value:

   ```text
   python manage.py rotate_field_encryption --from-version N \
     --resume-after members.Member:00000000-0000-0000-0000-000000000001
   ```

6. Rerun without a cursor. A reconciled completed rerun reports `rotated=0`; investigate any
   unexpected version, malformed ciphertext, or unrecoverable legacy count before promotion.
7. Keep `N` readable until both conditions hold: no live ciphertext requires it, and no retained
   database backup that may be restored requires it. Only then remove `N` from previous versions
   and the live key map under an audited Security/DevOps change.

The command updates registered database fields in small atomic row writes. It never writes
plaintext and safely preserves already-current ciphertext. For rollback, keep both versions,
configure `N` current and `N+1` previous, boot successfully, and rotate from `N+1` back to `N`;
never discard either key before reconciliation and restore evidence are complete.

## Backup and recovery

The recovery secret store must retain the full set of field-key versions needed to decrypt every
database backup inside the backup-retention window. Backup-encryption keys and field-encryption keys
remain separate: possessing one must not substitute for the other. A restore drill must provision
the restored database plus its referenced field versions, pass the production configuration check,
decrypt representative authorised fixture/evidence values, and record reconciliation without
printing plaintext or keys.

If a field key is lost, stop affected reads/writes and restore/correct key custody before resuming.
Do not fall back to `SECRET_KEY`, a JWT key, a backup key, local-development defaults, or plaintext.
