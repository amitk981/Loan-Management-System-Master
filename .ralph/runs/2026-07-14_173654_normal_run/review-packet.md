# Review Packet: 2026-07-14_173654_normal_run

## Result
Ready for independent validation

## Slice
008F-power-of-attorney-workflow

## Recommended Next Action
Run Ralph independent validation, then commit/merge/push only if it passes.

## Outcome

- Added §28.1-§28.3 package/PoA routes with strict envelopes, fields, permissions, sanctioned scope,
  exact replay, one-current identity, retained history, and authority-first mutation denial.
- Compliance prepares drafts; the retained distinct Company Secretary attorney activates only from
  genuine renderer output, exact locked 008D2 maker/checker stamp/notary, and exact locked 008E2
  borrower/nominee signatures with frozen capture identity.
- PoA/package/checklist responses are metadata-only. Activation preserves completion, verifier,
  remarks, approvals, package status, file authority, invocation/release, and false readiness.
- A-110 documents the honest transition for later SH-4/CDSL/cheque owners. 008G and 008H were
  sharpened from the completed selector/package seams and the opened source extracts.

## Two-axis independent review

### Standards

The independent reviewer reported three hard closeout/test gaps and two judgement calls. Closeout
artifacts/state/handoff/status and next-slice/digest sharpening are now complete. Permission-first
denial, zero-evidence denial, genuine lifecycle activation, and projection rollback regressions were
added. Repeated actor checks were consolidated behind one module helper. Model invariants remain
database-enforced while the public deep-module interface performs richer cross-owner validation;
direct ORM construction is limited to controlled migrations/tests.

### Spec

The independent reviewer reported five gaps, all addressed before final gates: activation now uses
008E2 frozen signature snapshots rather than mutable names; document/stamp/notary/signature evidence
is resolved and row-locked through legal-owned selectors; negated purpose text is rejected; the
positive tracer uses genuine renderer bytes plus real 008D2/008E2 modules; and IP/user-agent now
appear in audit, version, and workflow metadata. No scope creep was found.

Summary: Standards 3 hard + 2 judgement findings reviewed (hard findings resolved; one database-
validation judgement retained). Spec 5 findings resolved; worst high issues were frozen identity
and locked owner evidence.

## Traceability

- Functional M06-FR-007/008 and SOP V10 p.14 §4.3 require PoA for borrower + nominee, in favour of
  Company Secretary, stamped and notarised. `test_company_secretary_activates_only_with_current_maker_checker_and_signatures`
  drives genuine renderer, 008D2, 008E2, and HTTP activation while proving legacy/frozen identity.
- API §28.1-§28.3 requires package GET/refresh and PoA POST/GET/PATCH. Package replay/read and strict
  draft/active tests verify exact response and zero-write contracts; API examples are saved in
  `evidence/api-response-examples.md`.
- Data model §17.1-§17.2 requires protected one-package/one-PoA security tables. Migration 0008 adds
  the protected links, indexes, bounded states, nullable-only 009C transition, and no-release rule;
  PostgreSQL races prove one current outcome and complete history.
- Auth §§12.8/16.4/25.6 require Compliance preparation and Company Secretary verification. Focused
  denial, maker-checker, role, replay, and evidence tests prove mutation authority without granting
  downloads, invocation, release, completion, or readiness.

## Gates

- Frontend: build, typecheck, lint, and 293/293 tests passed.
- Backend: Django check and migration sync passed; 796/796 tests passed with 28 expected PostgreSQL-
  only skips; coverage 93% >= 85%.
- PostgreSQL: five-worker exact-create and changed-draft races passed in repeated runs, including
  after the final owner-row lock review.
- `git diff --check` passed; 20 changed/non-bookkeeping paths and 1 migration remain under Ralph's
  30-file/2,000-line/1-migration caps; no protected/source file changed.
