# Slice 008K2: Sensitive Security Contract Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008K

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Close the remaining confidentiality, partial-update, object-scope, and boundary-proof gaps in the
central field-encryption and Stage-4 security read contracts before portal or staff UI consumers
are added.

## Source / Review References

- `docs/source/data-model.md` §§17.4-17.5 and 29-30
- `docs/source/api-contracts.md` §§5.1, 6-8, and 28.1-28.6
- `docs/source/auth-permissions.md` §§14.1 and 19.2-19.4
- `docs/source/codebase-design.md` §§9.3-9.4, 28.1, 36.2, and 39.1-39.2
- `docs/slices/008I2-security-poa-owner-and-read-contract-closure.md`
- `docs/slices/008I3-security-legal-evidence-seam-and-race-closure.md`
- `docs/slices/008I4-sensitive-field-encryption-and-cdsl-null-contract-closure.md`
- `docs/slices/008J-blank-dated-cheque-and-cancelled-cheque-custody.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-15_034859_architecture_review`

## Concrete Requirements

1. Change the versioned `shared.encryption` token so it contains no recoverable plaintext fragment,
   including BO-account or cheque-number suffixes. Authenticate field, version, and length as
   opaque associated data. If a source-authorised display suffix is required, model it separately
   from ciphertext under an explicit masked-projection policy; ordinary blank-cheque responses
   remain the fixed `******` mask and never expose a suffix.
2. Migrate all retained `field:v1` CDSL and blank-cheque values to the corrected token version with
   row-count, lookup-hash, decrypt/re-encrypt, and plaintext-absence reconciliation. Freeze the
   migration implementation rather than importing mutable production encryption behavior, retain
   current/previous-key rotation, and preserve exact replay/duplicate detection without plaintext
   in logs, history, errors, migrations, or evidence.
3. Make §28.6 blank-cheque PATCH genuinely partial: accept any non-empty subset of the documented
   mutable fields, reject unknown/immutable/empty shapes, merge against the locked current row, and
   revalidate the complete candidate state. Omitted values remain unchanged; explicit null is
   allowed only for source-nullable fields. Preserve exact replay and terminal custody rules.
4. Enforce the §19 object matrix, not Stage 4 alone, for package, PoA, SH-4, CDSL, blank-cheque, and
   checklist reads: Senior Manager Finance requires documentation-approved/pending-disbursement
   truth; Chief Financial Controller requires disbursement-ready truth. Credit, CFO/director,
   Auditor, Compliance, and Company Secretary keep only their documented canonical scopes.
   Permission strings never widen object scope; absent and inaccessible ids remain nondisclosing.
5. Keep masking/reveal policy and redaction owned by the existing central sensitive-access and
   evidence-recorder seams. Remove divergent local sensitive-key policy where it can leak protected
   values, but do not merge ordinary security mutation evidence with the separate reveal ledger or
   reverse the security/legal dependency direction.
6. Complete the promised architecture regressions: both-direction executable import guards for
   security/legal/approval owners; forged access-object rejection for PoA, SH-4, and CDSL public
   paths; duplicate-hash behavior; token plaintext searches; and finance-reader state transitions.

## Test Cases

- Ciphertext round trip, random nonce, tamper, wrong field/key/version, rotation, migration, and
  repository/database/evidence scans prove no full value or suffix is recoverable without a key.
- CDSL and blank-cheque create/change/replay/duplicate behavior remains correct after migration;
  fixed ordinary masks and audited reveal behavior remain unchanged.
- PATCH one field at a time, several fields, exact replay, explicit-null, empty, unknown, immutable,
  stale, cross-object, invalid terminal, and concurrent changed candidate matrices.
- Each documented reader role before and after documentation approval/disbursement readiness, with
  permission-only, inactive, unrelated, missing, and stale-cycle denial proving zero sensitive
  reveal/download or success evidence.
- Fresh-process import/AST checks scan both directions and public tests reject forged/alternate
  callbacks for PoA, SH-4, CDSL, cheque, masking, and reveal.

## Evidence Required

Failing-first confidentiality/PATCH/scope regressions, retained-token migration reconciliation,
plaintext scans, focused/full gates, and the affected PostgreSQL security races twice.

## Risk Level
High

## Acceptance Criteria

- Encrypted columns retain no recoverable plaintext suffix and migrate without identity loss.
- PATCH and scoped reads match their source contracts.
- Central sensitive-data ownership and executable dependency direction are proved, not inferred.
- All configured gates pass.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested
- [x] Audit events tested
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
