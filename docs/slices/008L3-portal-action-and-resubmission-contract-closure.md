# Slice 008L3: Portal Action and Resubmission Contract Closure

## Status
Complete

## Parent Epics
Epic 008: Documentation, Legal Documents, and Security Package; Epic 005: Application Intake and
Completeness (portal continuation)

## Depends On
- 008K4
- CR-005

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make portal upload/download authority exactly match the server projection, route deficiency
resubmission through the application lifecycle owner, and restore the approved MP07/MP11/MP13
interaction composition with real browser proof.

## Source / Review References

- `docs/source/screen-spec-member-portal.md` MP07, MP11, MP13, §§8.2-8.4, 10, and 11
- `docs/source/functional-spec.md` M03-FR-010 through M03-FR-012 and M06-FR-018-019
- `docs/source/api-contracts.md` §§3, 5-8, 26-28, and 44
- `docs/source/auth-permissions.md` §§19.4 and 21-23
- `docs/source/codebase-design.md` §§4.2, 20.7, and 21
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/008L-member-portal-documentation-actions.md`
- `docs/slices/008L2-member-portal-deficiency-response-and-resubmission.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-15_085859_architecture_review`

## Concrete Requirements

1. Use one active-portal-account/member/application scope resolver for MP07/MP11/MP13 reads and
   actions. Missing, cross-member, internal-user, suspended, expired, and claimed-member attempts
   remain nondisclosing and never receive internal permissions, security ids, or success evidence.
2. Compute documentation upload/re-upload authority once in the backend and reuse it for GET and
   POST under the checklist/application lock. Reject a crafted upload whenever the canonical
   projection advertises both flags false, including reconciled completion, stale/current-evidence
   blockers, wrong stage/cycle, non-applicable actions, and concurrent completion. Portal evidence
   never reopens or appends to an internally complete item.
3. Replace caller-editable `expires_at` content authority with the central signed, short-lived,
   document-and-scope-bound download capability already used by 008L2. Bind portal account, member,
   application, action/deficiency, and current document; reject tamper, expiry, replay after current-
   document replacement, cross-action, and cross-member use. Keep checksum verification and no-store
   responses; never expose storage keys or raw local-document URLs.
4. Put `incomplete_returned -> submitted` behind an application-owned `resubmit` transition using
   the 002H guard and canonical audit/workflow writer. Keep staff-only deficiency resolution honest:
   borrower response/submission events must target the response aggregate (or another source-backed
   response state), not claim `ApplicationDeficiency open -> responded` while the deficiency remains
   open. Re-upload and resubmit histories must state the actual old/new aggregate states exactly.
5. Align portal upload/download audit events with the central document vocabulary and required
   actor/member/application/document/version/category/sensitivity/reason/request/network/outcome
   metadata. Preserve portal-specific attribution without creating parallel audit semantics.
6. Restore MP07's approved existing upload modal/drop-zone composition and preserve MP11/MP13 cards,
   badges, spacing, typography, colours, loading/empty/401/403/validation/upload/success/error states.
   Use the existing safe browser-download interaction so object URLs remain valid until navigation
   consumes them. Add structural and interaction tests; introduce no styling or mock fixture path.
7. Carry CR-005's independent status/control contract through the routed proof: after reconciliation
   the completed Term Sheet must show canonical `Complete` beside its retained authorised Download,
   while Upload and Re-upload are absent. Capture that exact state in
   `portal-documentation-complete-upload-denied.png` in both trusted runs.

## Trusted Browser Acceptance

- Spec: `e2e/member-portal-documentation-actions.e2e.spec.ts`
- Spec: `e2e/member-portal-deficiency-response.e2e.spec.ts`
- Screenshot: `portal-documentation-upload-modal.png`
- Screenshot: `portal-documentation-complete-upload-denied.png`
- Screenshot: `portal-deficiency-mobile-response.png`
- Screenshot: `portal-deficiency-resubmitted.png`

## Trusted Browser Scenario

At 1280x720, sign in through the real portal session, open MP07/MP13, capture the preserved upload
modal, upload once, refetch, then prove a reconciled-complete action has no control and a direct
crafted POST is denied. Download a published Term Sheet through a fresh signed capability and prove
tampering fails. At a 390x844 viewport, open MP11 for a returned application, capture the response
form, upload every required correction, resubmit through the guarded lifecycle, and capture the
canonical returned-to-review state. Each spec and screenshot must run twice outside the sandbox.

## Test Cases

- GET/POST predicate parity for upload, re-upload, completed, stale, concurrent, non-applicable,
  wrong-stage, missing, and cross-member actions with exact zero-success evidence assertions.
- Signed capability issue/read/tamper/expiry/replacement/cross-scope matrices for both documentation
  and deficiency downloads; authenticated fresh content and audit metadata remain exact.
- Application transition guard is invoked for resubmit; invalid state/permission and concurrent
  resubmits are zero-write, while one success reopens the canonical completeness queue.
- Deficiency response/re-upload/resubmit workflow rows match the response/application aggregate
  states and leave staff resolution plus all Stage-4 evidence untouched.
- Frontend tests click upload/re-upload/download/resubmit, cover 401 and 403 separately, preserve the
  modal structure, refetch exactly once, and prove no immediate blob-URL revocation race.
- The routed MP07 assertion observes `Complete` and `Download Term Sheet` together and observes no
  Upload/Re-upload control before taking the declared completed-state screenshot.

## Evidence Required

Failing-first upload-predicate, signed-capability, lifecycle-guard, event-consistency, and modal
fidelity probes; API response examples; focused/full gates; and the declared browser outputs twice.

## Risk Level
High

## Acceptance Criteria

- Portal actions cannot exceed the canonical advertised authority.
- Downloads are signed and scope bound; resubmission uses the application lifecycle owner.
- MP07/MP11/MP13 retain the approved visual/interaction language with real browser evidence.
- All configured gates pass.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested
- [x] Audit events tested
- [x] Visual evidence contract implemented; local browser attempt recorded and trusted execution deferred
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
