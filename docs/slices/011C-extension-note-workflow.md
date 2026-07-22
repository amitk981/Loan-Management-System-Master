# Slice 011C: Extension Note Workflow

## Status
Complete

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Grant one auditable one-year extension to an unpaid, non-intentional default and retain its Extension
Note in the governed loan file.

## User Value
Eligible borrowers receive the source-mandated extension while Credit retains defensible evidence.

## Depends On
- 011B

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.ExtensionNotePostgreSQLAcceptanceTests`
- Expected tests: 2

## Source References
- `docs/source/api-contracts.md` §35.5
- `docs/source/data-model.md` §21.3
- `docs/source/product-requirements.md` §11.26 (`DEFAULT-AC-003-004`)
- `docs/source/screen-spec.md` S54
- `docs/source/component-spec.md` §17.4
- `docs/source/auth-permissions.md` §§12.10, 20.3, 25.8
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011C

## Scope
- Add one `ExtensionNote` per default case and `DefaultWorkflow.grant_extension` behind POST
  `/api/v1/default-cases/{id}/grant-extension/`.
- Require an expired/unpaid grace period, current non-intentional assessment recommending extension,
  reason, start date immediately after grace, end exactly one calendar year later, and a valid
  loan-scoped Extension Note document.
- Preserve preparer, configured approver when required, draft/approved/active/expired state, and
  immutable effective dates once active. Do not invent an approval route when configuration is absent.
- Add retry-safe extension-expiry processing that marks review required but does not create a
  Non-Payment Note automatically.

## Permissions and Audit
- Credit Manager with `defaults.extension.grant`; configured checker remains distinct when enabled.
  Credit Assessment and Auditor receive scoped read only.
- Create/approve/activate/expire/cure actions append audit/workflow evidence and document linkage.

## Acceptance and Negative Tests
- Eligible non-intentional case creates one one-year note and stores it in the exact loan file;
  payment during extension cures the default without deleting the note.
- Reject intentional/unclear or stale assessment, pre-grace-expiry, already-paid/closed case, wrong
  dates, missing/foreign document, self-check when configured, changed replay, and second extension.
- Exact replay and concurrent grants converge on one note/transition; expiry processor is retry safe.
- Reverse consumers: 011A/B history remains readable and unchanged; document permission/download
  tests remain green; extension cannot mutate ledger or KYC facts.

## Non-Goals
Generating new document infrastructure, defining source-silent intentionality criteria, repeated
extensions, Non-Payment Note (011D), recovery, or staff frontend.

## Evidence
RED/GREEN eligibility/date/service/API/document/permission tests; migration and PostgreSQL uniqueness
proof; expiry retry proof; audit trace; full backend gate and response/document metadata examples.

## Risk Level
Medium

## Acceptance Criteria
- `DEFAULT-AC-003-004`, `MOD-DEF-005-007`, and `API-DEF-004` pass.
- Extension authority, dates, evidence, and uniqueness are enforced by the backend owner.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Model/migration/service/API/document and scheduler integration completed
- [ ] Negative, race/retry, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
