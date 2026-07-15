# Execution Plan

Selected slice: 008I4-sensitive-field-encryption-and-cdsl-null-contract-closure

1. Add public-interface RED tests for pending CDSL create/PATCH with null evidence, terminal
   rejection with null evidence, AES-GCM field-encryption round trip/tamper/version/rotation,
   and centrally owned reveal permission/object/reason/repeat/re-auth/rate/audit behavior.
2. Implement `shared.encryption` with independently configured current/previous versioned keys,
   authenticated AES-GCM ciphertext, field-bound associated data, lookup HMAC, and no
   `SECRET_KEY` fallback. Pin the slice-approved cryptography dependency.
3. Implement `documents.modules.sensitive_data_access` as the single masking/reveal policy and
   sensitive-audit owner. Route CDSL reveal through the top-level evidence coordinator so the
   security module supplies object facts without importing documents or decrypting values.
4. Update CDSL persistence and projections to use central encryption/masking, safely retain and
   serialize null pending evidence, while preserving terminal evidence requirements, replay,
   ordinary redacted evidence, projections, and no downstream side effects.
5. Add one data migration that reconciles retained `seal:v1` rows into the current ciphertext
   version with count/hash/last4 checks and no plaintext output; cover forward/backward behavior.
6. Run focused RED/GREEN tests, migration sync, backend checks and the configured backend/frontend
   gates. Save self-contained logs, plaintext/dependency scans, changed-files, risk assessment,
   review packet, final summary, and Ralph state/progress/handoff/slice updates.
7. Sharpen the next one or two Not Started slices only from already-opened Epic 008 material, and
   update the Epic 008 digest with any durable 008I4 implementation facts.
