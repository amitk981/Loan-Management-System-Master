# Slice 008D2: Stamp and Notary Verification Authority Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008D

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make stamp-duty and notarisation outcomes a true Compliance-maker/Company-Secretary-checker
workflow, and restore legal evidence policy to the legal-documents owner without changing the
§26.9-§26.10 routes.

## Source / Review References

- `docs/source/auth-permissions.md` §§15.4-15.5, 18.1-18.2, 19.2-19.4, and 26.4
- `docs/source/codebase-design.md` §§6.3-6.4, 9.1-9.2, 14.2, and 36.1-37.2
- `docs/source/api-contracts.md` §§6-8 and 26.9-26.10
- `docs/source/data-model.md` §§16.7-16.8, 30, and 34
- `docs/slices/008D-stamp-duty-and-notarisation-tracking.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_155832_architecture_review`

## Concrete Requirements

1. Compliance Team actors may create or change preparation facts only while the owner outcome is
   `pending`. Treat both `insufficient` stamp duty and `rejected` notarisation as Company Secretary
   verification decisions, just like `adequate`/`completed`; a preparer must not create, downgrade,
   replace, or erase any checker-owned outcome.
2. Enforce documentation maker-checker separation for verification. Retain attributable preparer
   and verifier identities (with the smallest additive migration if required), reject the same user
   acting as both on one instrument even through multiple active roles, and preserve all prior
   decision history. Do not invent an override path.
3. Keep exact replay zero-write for both maker and checker submissions. Changed checker outcomes
   remain possible only through Company Secretary authority and must retain old/new audit, version,
   workflow, checklist projection, and request/network/role/team facts atomically.
4. Move application/category/role-specific notary-evidence policy out of the foundation
   `documents` app. The documents owner may expose a generic immutable upload-provenance fact; the
   `legal_documents` module must own Stage-4 role, legal-category, same-application, and purpose
   decisions. Preserve metadata-only responses and separate download authority.
5. Parse §26.9-§26.10 request shape, types, dates, decimal strings, and enums at a legal HTTP
   serializer seam as required by codebase-design §§6.3-6.4. Keep the deep module interface safe for
   direct callers and centralise action/role authority in the legal-document permission module.
6. Preserve current-renderer target enforcement, one current row under the loan-document lock,
   source-owned status projections, completed-checklist conflicts, and the unresolved configurable
   stamp-rate policy.

## Test Cases

- Compliance pending create/change succeeds; Compliance `adequate`, `insufficient`, `completed`,
  `rejected`, verified-outcome downgrade, and verified-evidence replacement all fail zero-write.
- Company Secretary records each positive/adverse outcome; same-user/multi-role maker-checker,
  inactive, permission-only, wrong-stage, unrelated, unknown, and legacy targets remain denied or
  nondisclosing with no success ledger.
- Exact replay and checker correction preserve one current row plus complete preparer/verifier and
  old/new evidence; projection conflicts roll back every owner and ledger write.
- Notary evidence accepts only exact same-application legal upload provenance through the new legal
  seam; cross-application, duplicate/malformed upload ledgers, changed metadata, and download-only
  authority fail closed.
- Serializer and direct-module matrices prove identical strict fields and business outcomes.
- The five-worker changed-outcome race passes twice on PostgreSQL with one current decision and a
  complete attributable winner/loser ledger.

## Evidence Required

Backend RED/GREEN authority matrices, exact adverse/downgrade API examples, dependency proof,
twice-run PostgreSQL race output, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Only the Company Secretary can establish or change a stamp/notary verification outcome.
- Maker-checker identity and history are enforceable and attributable.
- Stage-4 legal evidence policy is local to the legal-documents deep module.
- All configured gates pass.
