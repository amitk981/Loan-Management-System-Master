# Slice 008I4: Sensitive Field Encryption and CDSL Null Contract Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008I3

## Goal

Move CDSL BO-account protection and reveal behind the source-defined central sensitive-data and
field-encryption seams, and restore nullable pending evidence without weakening terminal acceptance.

## Source / Review References

- `docs/source/codebase-design.md` §§9.4, 15.3, and 39.1-39.2
- `docs/source/api-contracts.md` §§6-8 and 28.5
- `docs/source/data-model.md` §§17.4, 29-30, and 34
- `docs/source/auth-permissions.md` §§6.5, 12.8, 19.4, and 21
- `docs/source/deployment-ops.md` §§9.2 and 10
- `docs/slices/008I-cdsl-pledge-workflow.md` and assumption A-115
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_234031_architecture_review`

## Concrete Requirements

1. Introduce the central `shared.encryption` interface named by source: encrypt, decrypt, and
   hash-for-lookup by field name. Use an approved pinned authenticated-encryption implementation,
   versioned ciphertext, a dedicated field-encryption key/config reference independent of Django
   `SECRET_KEY` and JWT signing, and explicit current/previous-key handling. Never retain the custom
   XOR/HMAC counter-mode construction as a production adapter.
2. Move masking, reveal permission, canonical object access, reason validation, expiry semantics,
   rate/re-auth policy decision, and success/denial auditing behind one
   `documents.modules.sensitive_data_access` interface. The CDSL module supplies its object facts but
   must not decrypt, role-check, or write reveal audit rows directly.
3. Migrate retained `seal:v1` CDSL values to the new versioned ciphertext with row-count/hash/last4
   reconciliation and no plaintext/log exposure. Preserve exact replay by lookup hash. Keep 012E3
   responsible for whole-repository key rotation and older PAN/Aadhaar/bank migrations; sharpen its
   tests to consume this seam rather than create a second encryption module.
4. Honour §17.4 nullable `evidence_document_id` during pending create/change. Null pending evidence
   returns 200 with null metadata and never dereferences a missing legal document; submitted/terminal
   acceptance continues to require current same-application evidence and all existing PSN/DP/BO/
   count/agreement/future-share rules.
5. Preserve masked ordinary reads/evidence, explicit separately audited Company Secretary reveal,
   no plaintext in database logs/errors/history, terminal replay/immutability, package/checklist
   projections, and zero invocation/unpledge/balance/readiness side effects.
6. Add corruption, wrong key/version, key rotation, duplicate hash, migration reconciliation,
   repeated reveal, missing reason, denied object scope, and plaintext-search regressions. No test or
   setting may silently fall back to `SECRET_KEY` for reversible CDSL data.

## Test Cases

- Public pending create/PATCH with null evidence succeeds; acceptance with null evidence fails 400
  and writes nothing.
- Approved-encryption round trip/tamper/key-version/rotation and retained migration reconciliation.
- Central reveal interface success/denial/object/reason/expiry/rate/re-auth decisions and audit.
- Exact replay, terminal acceptance, masking, projections, and all existing CDSL races remain green.

## Evidence Required

RED reproduction of the nullable-evidence 500, encryption/reveal seam proof, migration reconciliation,
plaintext repository/database/evidence scans, focused CDSL tests, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Reversible BO data uses the central, independently keyed, versioned encryption interface.
- Sensitive reveal policy and auditing have one deep owner.
- Valid pending CDSL requests with null evidence no longer produce an internal error.
- All configured gates pass.
