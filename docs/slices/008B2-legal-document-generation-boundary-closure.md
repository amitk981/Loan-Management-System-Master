# Slice 008B2: Legal Document Generation Boundary Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008B

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Place loan-document generation/read ownership behind the source-defined legal-documents deep-module
boundary, with module-enforced permission/object authority and selector-owned collection queries,
before checklist and execution workflows build on it.

## Source / Review References

- `docs/source/codebase-design.md` §§6.3, 7.2-7.4, 9.1-9.2, 14.1, 26.1-27.1, 36.1-37.2, and 42.2
- `docs/source/api-contracts.md` §§3, 6-8, and 26.1-26.5
- `docs/source/data-model.md` §§16.1-16.3, 30, and 34
- `docs/slices/008A2-template-effective-integrity-and-file-reference-boundary.md`
- `docs/slices/008B-document-generation-shell.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_093142_architecture_review`

## Concrete Requirements

1. Establish the source dependency direction for generation: legal-document orchestration may
   consume approvals, applications, document storage/reference, identity/audit, and workflow
   boundaries; the foundation `documents` owner must not import approval/application business
   modules. Preserve the public v1 routes and database rows during any ownership move.
2. The public generation module itself must require `documents.loan_document.generate`, canonical
   application object scope, sanctioned state, and `documents.template.file_reference`. Calling the
   module directly from a task, test, or future orchestration path without any one authority must be
   indistinguishable and zero-write; an HTTP-view check is not sufficient.
3. The legal-document read boundary must require `documents.loan_document.read` plus application
   object scope before count/pagination/serialization. Move loan-document filter, eager loading,
   deterministic ordering, count, page normalization, and slicing into a legal-document selector;
   remove the duplicate module pagination parser.
4. Preserve the 008A2 public template variant/reference decisions and do not add direct fallback
   queries for file authority. Keep generated/template bytes and storage descriptors out of list
   responses and audit payloads.
5. Reconcile `loan_account_id` with data-model §16.3's nullable foreign-key requirement without a
   destructive table rewrite or an unconstrained UUID becoming an accepted live reference. If the
   Epic 009 loan aggregate is not yet installable, keep the field explicitly unusable/null through
   one database-enforced transition and hand the final FK to 009C; record the exact deferred state.
6. Preserve exact replay, one generated file/audit/workflow set, application locking, retained
   template/output identity, and the existing five-request PostgreSQL result. No checklist,
   signature, stamp, notarisation, or download action belongs here.

## Database / Migration Impact

At most one non-destructive migration. Any Django app/model ownership transfer must retain the
existing `loan_documents` table and relations without parallel writable model owners, row copying,
or loss of migration history.

## Test Cases

- Direct module calls lacking generate permission, reference permission, application ownership, or
  active actor authority fail before template/file/frozen-fact reads and leave zero bytes/rows/events.
- API and direct-module success return the same exact contract; replay and PostgreSQL five-request
  races retain one result/evidence set after the boundary move.
- Reader/list direct and HTTP matrices prove object scope is applied before count/page and metadata
  serialization; selector tests use real ordering and out-of-range pages.
- Dependency tests prove the foundation documents package has no approval/application business
  imports and the legal owner has no view/HTTP transport imports.
- Migration/fresh-database tests prove retained 008B rows and nullable loan-account integrity.

## Evidence Required

Backend RED/GREEN output, dependency and authority matrices, fresh-migration evidence, two
PostgreSQL race passes, sanitised API examples, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Legal generation has one deep authoritative boundary with source-compliant dependency direction.
- Direct callers cannot bypass permission or object scope.
- Collection reads are selector-owned and relational integrity is honest.
- All configured gates pass.

