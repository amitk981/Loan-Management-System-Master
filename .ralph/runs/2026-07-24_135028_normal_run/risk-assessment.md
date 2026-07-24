# Risk Assessment

Risk level: High

- Selected slice: 012E3-field-encryption-key-separation
- Mode: normal_run
- Manual review required: independent Ralph validation and release-key custody review.

## Security and data-integrity controls

- Production settings require explicit current-version, key-map, key-reference, and lookup-key
  environment secrets. Missing, malformed, or incomplete key material fails before production
  settings finish loading; local defaults remain development-only.
- New identity and bank values use the existing authenticated `shared.encryption` interface.
  Sensitive runtime owners no longer derive field ciphertext or lookup hashes from `SECRET_KEY`.
- Rotation has a single registry covering every current model field ending in `_encrypted`.
  Registered values are authenticated with their field context, re-encrypted to the active version,
  and associated lookup hashes are rebuilt when reversible source truth is available.
- Each row update is an atomic compare-and-swap against the inspected ciphertext/hash values. A
  concurrent sensitive-field change fails closed and tells the operator to resume after the last
  successful checkpoint rather than overwriting it.
- Re-running rotation is idempotent. Current-version values remain untouched, unexpected versions
  and malformed/unreadable ciphertext stop the command, and reconciliation separates rotated,
  current, recovered legacy, and unrecoverable legacy values.
- CDSL, blank-cheque, SAP, member masking, and reveal-audit consumers retain the same public and
  audit behavior. Member reveal now decrypts authenticated values instead of returning storage
  tokens.

## Residual risks and operational decisions

- Historical `enc:v1`/`seal:v1` one-way values cannot be decrypted. The command preserves and
  counts them as `legacy_unrecoverable`; promotion must not claim successful reveal for those rows.
  Security/operations must recover values only from authorised source documents/workflows and
  record reconciliation. This is the source-required limitation, not a cryptographic fallback.
- `SFPCL_FIELD_LOOKUP_KEY` is separated from `SECRET_KEY` but is not versioned by this ciphertext
  rotation. Rotating it requires a separately governed rebuild of all lookup hashes from reversible
  source truth; the operations note explicitly prevents ad-hoc replacement.
- Old field-key versions must remain in the recovery secret store for as long as any live
  ciphertext or retained database backup may require them. Removing a key before both conditions
  are reconciled can make restored data unreadable.
- No schema migration was required. Independent validation still owns this High-risk slice's full
  backend coverage lane and configured coverage floor.

## Evidence

- Identity RED/GREEN: `evidence/terminal-logs/identity-field-key-red.log`,
  `evidence/terminal-logs/identity-field-key-green.log`
- Rotation/reconciliation RED/GREEN:
  `evidence/terminal-logs/rotation-reconciliation-red.log`,
  `evidence/terminal-logs/rotation-reconciliation-green.log`
- Resume RED/GREEN: `evidence/terminal-logs/rotation-resume-red.log`,
  `evidence/terminal-logs/rotation-resume-green.log`
- Legacy lookup migration RED/GREEN:
  `evidence/terminal-logs/legacy-lookup-key-migration-red.log`,
  `evidence/terminal-logs/legacy-lookup-key-migration-green.log`
- Production startup RED/GREEN:
  `evidence/terminal-logs/production-field-key-startup-red.log`,
  `evidence/terminal-logs/production-field-key-startup-green.log`
- Reverse consumers and final focused gates:
  `evidence/terminal-logs/identity-and-seed-reverse-consumers-green.log`,
  `evidence/terminal-logs/encryption-rotation-cdsl-cheque-green.log`,
  `evidence/terminal-logs/encryption-and-rotation-final-green.log`
- Configuration/migration checks:
  `evidence/terminal-logs/backend-final-checks.log`
