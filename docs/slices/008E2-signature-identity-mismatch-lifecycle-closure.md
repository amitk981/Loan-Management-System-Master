# Slice 008E2: Signature Identity and Mismatch Lifecycle Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008D2
- 008E

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make legal signatures immutable, application-owned identity evidence and make mismatch resolution
the only path that can clear an unresolved mismatch, with nondisclosing authority and proven races.

## Source / Review References

- `docs/source/api-contracts.md` §§6-8 and 26.7-26.8
- `docs/source/data-model.md` §§16.3, 16.6, 30, and 34
- `docs/source/functional-spec.md` M06-FR-016/M06-FR-017
- `docs/source/auth-permissions.md` §§15.4-15.5, 18.1-18.2, 19.2-19.4, and 26.4
- `docs/source/codebase-design.md` §§6.3-6.4, 7.2, 9.1-9.2, 14.2-14.3, and 37.2
- `docs/slices/008E-signature-mismatch-workflow.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_155832_architecture_review`

## Concrete Requirements

1. Once the current signer identity is recorded as `mismatch`, the capture action may replay the
   exact capture but must not change it to pending/signed, replace the signer snapshot, or otherwise
   clear the active blocker. Only the Company Secretary mismatch-resolution action may clear owner
   truth; resolved evidence remains immutable and cannot be reopened.
2. Resolve borrower, nominee, witness, and user ids through their canonical application/identity
   owners before creating a row. Freeze the exact party id/type/name at first capture; do not accept
   arbitrary UUID/name pairs or refresh a retained snapshot from mutable display data. Preserve the
   nullable source case only where the cited schema genuinely permits no governed identity.
3. Enforce maker-checker identity across capture and resolution, including multi-role users. A
   Compliance recorder cannot also resolve the same mismatch; no implicit override is allowed.
4. Resolve mutation authority and accessible Stage-4 parent scope before exposing signature-row
   existence. Authorized unknown, wrong-stage, and unrelated signature ids must follow one
   nondisclosing contract, while callers lacking the action permission/role remain 403 before owner
   queries.
5. Parse §26.7-§26.8 shape and simple fields at the legal HTTP serializer seam while retaining
   direct-module validation. Return the §6.3 action-response envelope for mismatch resolution,
   including previous/new state, workflow event identity, and available actions; metadata-only file
   identity still grants no download.
6. Replace the duplicated application-wide signature query with one legal-documents-owned selector
   consumed by capture-time projection, checklist refresh, and 008F/008G. Keep owner semantics in
   the application fact module and centralise action/role authority in the legal permission module.
7. Preserve same-document/current-renderer evidence, adequate stamped-declaration rules,
   completion-conflict rollback, exact replay, immutable audit/version/workflow history, and the
   A-107 signed-copy/bank-attestation limitation without claiming checklist/disbursement readiness.

## Test Cases

- The reproduced mismatch-to-signed same-identity capture returns conflict and preserves the row,
  Bank Verification Letter blocker, and ledgers; exact mismatch replay remains zero-write.
- Canonical borrower/nominee/witness/user ids and frozen names succeed; arbitrary, wrong-party,
  cross-application, conflicting, and changed-name identities fail without rows or evidence.
- Distinct Compliance maker and Company Secretary checker succeed; same-user/multi-role resolution,
  capture-only resolver, resolve-only recorder, inactive, permission-only, and unrelated actors fail.
- Unknown, inaccessible, wrong-stage, and unrelated signature ids are indistinguishable at the
  accessible-owner boundary; tests assert status/error shape and zero queries/writes past denial.
- §6.3 resolution response and serializer/direct-module matrices cover strict fields, malformed
  datetimes/UUIDs, both evidence types, exact replay, and changed replay.
- Genuine five-worker capture and resolution races each pass twice on PostgreSQL with one current
  outcome and complete attributable winner/loser history.

## Evidence Required

Backend RED/GREEN reproduction logs, identity/authority/error matrices, exact action-response
examples, twice-run PostgreSQL capture/resolution races, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- An unresolved mismatch cannot be cancelled through ordinary capture.
- Signature identities and snapshots come from canonical owners and remain immutable.
- Resolution is nondisclosing, maker-checker safe, contract-shaped, and concurrency-proven.
- All configured gates pass.
