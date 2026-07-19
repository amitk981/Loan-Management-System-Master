# Slice 011O: Auditor Read-Only Views

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Give Internal Auditor a coherent read-only view of Epic 011 cases, evidence, controls, and histories
without adding operational authority or bypassing document classification.

## User Value
Auditors can sample lifecycle and compliance evidence directly while owners remain accountable for changes.

## Depends On
- 011N
- 011M2

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/auditor-read-only-epic-011.e2e.spec.ts`
- Screenshot: `auditor-epic-011-populated.png`
- Screenshot: `auditor-epic-011-empty.png`
- Screenshot: `auditor-epic-011-unauthorised.png`

## Source References
- `docs/source/auth-permissions.md` §§15.11, 19-20, 22-23, 26.7
- `docs/source/functional-spec.md` M14-FR-012-013
- `docs/source/security-privacy.md` §34
- `docs/source/design-system.md` §36.6
- `docs/source/test-plan.md` §§13.17-13.20, 37.2-37.5
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011O

## Scope
- Audit all Epic 011 GET/list/detail/query services for explicit `audit_readonly` scope across default/
  assessment/extension/note/recovery, closure/NOC/return/archive, controls/tasks/evidence/calculations/
  KYC reviews, and grievances. Add only missing read projections; do not duplicate write services.
- Return masked/safe summaries, complete immutable workflow/audit references, evidence metadata, and
  no mutating `available_actions`. Restricted document content still requires the existing category,
  object-scope, permission, reason/audit, and signed-download path.
- Add a focused auditor route/view using existing tables, filters, status badges, timeline, evidence
  links, loading/empty/error/unauthorised states, and read-only styling; reuse existing components.
- Assert every Epic 011 POST/PATCH/DELETE and operational service method remains forbidden to the
  auditor, including evidence review unless governance explicitly confirms that optional role later.
- Keep audit observations, exports, and broad Audit Explorer work in Epic 012.

## Permissions and Audit
- Use existing `audit.*`, `reports.compliance.read`, owner read permissions, and `audit_readonly` scope;
  never grant operational manage/create/update/approve/invoke/close/issue/return/archive permissions.
- Sensitive/restricted detail and downloads are audited; normal list reads avoid excessive per-row audit noise.

## Acceptance and Negative Tests
- Auditor can filter/open each Epic 011 aggregate, trace immutable history, and access only authorised
  evidence metadata/downloads; masked fields stay masked.
- Full method matrix proves every mutation returns 403 with zero write/audit side effect beyond the
  denied-access event; hand-crafted UI calls cannot bypass it.
- Other broad-read roles do not inherit auditor scope; borrower and staff object filters remain unchanged.
- Reverse consumers: all prior Epic 011 authority/object-scope suites, sensitive reveal/download,
  dashboard navigation, and generic mutation endpoint tests remain green.

## Non-Goals
Audit observation mutation, exports/reports/Audit Explorer (Epic 012), changing evidence review policy,
new visual language, or staff operational UI (011P).

## Evidence
Saved RED/GREEN backend GET/mutation permission matrix and object-scope tests; frontend component/route tests,
typecheck/lint/build; trusted-browser screenshots for populated/empty/unauthorised views; full gates.

## Risk Level
Medium

## Acceptance Criteria
- Internal Auditor can inspect required Epic 011 truth while every operational mutation stays impossible.
- Evidence access remains classified, scoped, masked, signed, and audited through existing owners.

## Done Checklist
- [ ] Execution plan and permission matrix saved
- [ ] Missing read projections and focused auditor UI completed
- [ ] Mutation-denial, scope/masking, reverse-consumer, visual, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
