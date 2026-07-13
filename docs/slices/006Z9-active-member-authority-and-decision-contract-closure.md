# Slice 006Z9: Active-Member Authority and Decision Contract Closure

## Status
Complete

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z7
- 006Y16

## Runtime Capabilities

none

## Goal

Replace inferred system-role member scope with an explicit reviewable authority projection, enforce
that relaxation evidence persists only a relaxation decision, and close the public verification
matrix including maker-checker evidence ownership.

## Source / Review References

- `docs/source/functional-spec.md` BR-003 through BR-007 and M02-FR-004 through M02-FR-006
- `docs/source/auth-permissions.md` §§3-3.1, §§18-19, §25.1, and §34.2
- `docs/source/data-model.md` §§11.5-11.6 and §34
- `docs/source/codebase-design.md` §§22.1, 26.1-27.1, and 42.2
- `docs/slices/006Z7-active-member-relaxation-authority-and-evidence-race-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_025409_architecture_review`

## Concrete Requirements

1. Define one explicit member scope result (`created_by`, assigned/team when persisted, documented
   global management/verification authority, or denied). `Role.is_system_role` and an unowned row
   are not substitutes for global authority; caller flags and hard-coded role bypasses remain forbidden.
2. Registry read/update/identity approval and active verification must consume that projection and
   expose identical owner/global/permission/object categories for equivalent public calls. If source
   documents do not name a write-global role, keep it configurable/denied and record the open decision.
3. A calculated `member_active_check = relaxation` may be persisted only with
   `decision = relaxation`; `decision = active` returns stable `INVALID_DECISION` with no status,
   pointer, history, audit, or workflow evidence. Ordinary pass results cannot be mislabeled relaxation.
4. Evidence creator/updater and active-status verifier must satisfy maker-checker separation. A user
   cannot create or materially update qualifying supply/service/relaxation evidence and then verify
   the resulting decision; both the projection and write denial must agree.
5. Complete independently selectable module and HTTP rows for active, inactive, relaxation,
   mismatched decision, missing/future date, unknown/non-object payload, permission/object/maker-
   checker denial, stale member/result/evidence, repeat, unsupported decision, and chronology.

## Test Cases

- System/custom roles with the same permissions do not gain different object scope merely from role provenance.
- Relaxation result + active decision and pass result + relaxation decision fail with complete zero evidence.
- The creator/updater of qualifying relaxation/service evidence cannot verify that same result.
- Every module row has a matching API result/envelope and full before/after evidence assertion.

## Evidence Required

Failing authority, decision-mismatch, maker-checker, and API-matrix tests; green public matrices;
dependency scan; and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Member object scope is explicit and source-reviewable rather than inferred from role metadata.
- Stored active-member status cannot contradict the qualification route or maker-checker history.

## Execution Notes

- Do not transfer 006Y16's Credit Manager application rule into member scope: auth §19.2 makes that
  authority conditional on an existing application's Credit Assessment stage, while §19.1 requires
  member-global authority to be an explicit, independently reviewable scope.
- Preserve `OBJECT_ACCESS_DENIED` nondisclosure for an unowned or unresolved member until the cited
  source pass identifies a row-independent member-global assignment; role provenance alone is not
  that assignment.
