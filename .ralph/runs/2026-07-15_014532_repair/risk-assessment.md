# Risk Assessment

Risk level: High

## Inherited risk

008I4 changes reversible protection, lookup hashes, retained-row migration, sensitive reveal
authority/audit behavior, and nullable legal evidence. A defect could disclose BO values, make
retained values unreadable, lose denial evidence, bypass object scope, or weaken terminal evidence.

## Repair scope and controls

- Production behavior changed only at the reveal coordinator's exception boundary: centrally owned
  denial evidence commits while the same validation/access/rate/ciphertext exception and HTTP status
  are preserved.
- Canonical object resolution and pledge row locking remain inside the same atomic transaction;
  success decryption/audit remains atomic and repeated reveal stays rate limited.
- Three failing tests now use the source-defined CDSL document type and assert setup responses,
  preventing error-envelope `KeyError` failures from hiding the real contract.
- The subprocess test uses Ralph's virtualenv entrypoint; guarded imports and fresh-process isolation
  remain unchanged. No production dependency direction was relaxed.
- Full SQLite coverage and the declared PostgreSQL concurrency matrix passed. Plaintext remains
  absent from production paths and denial/success audit payloads.

## Residual risk

Production secret-store provisioning and whole-repository key rotation remain owned by 012E3.
Independent Ralph validation still decides commit/merge/push. Standing owner approval applies; no
revoked entry or protected-path edit was found.
