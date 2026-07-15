# Slice 008L4: Portal Production Boundary and Browser Proof

## Status
Not Started

## Parent Epics
Epic 008: Documentation, Legal Documents, and Security Package; Epic 005: Application Intake and
Completeness (portal continuation)

## Depends On
- 008K5

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make the portal documentation/deficiency browser contract exercise the real authenticated Django
boundary, keep read/write authority on one locked current-document decision, and align the retained
portal audit vocabulary with the source before staff wiring reuses these seams.

## Source / Review References

- `docs/source/screen-spec-member-portal.md` MP07, MP11, MP13, §§8.2-8.4, 10, 11, and 14.3-14.4
- `docs/source/functional-spec.md` M03-FR-010 through M03-FR-012 and M06-FR-018-019
- `docs/source/api-contracts.md` §§3, 5-8, 26-28, and 44
- `docs/source/auth-permissions.md` §§19.2, 19.4, and 21-23
- `docs/source/codebase-design.md` §§4.2, 20.7, 21, 23, and 26.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/008L3-portal-action-and-resubmission-contract-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-15_181520_architecture_review`

## Concrete Requirements

1. Replace the catch-all Playwright `/api/v1/**` interception with a real Django test server, real
   portal login/session, persisted application/checklist/submission/deficiency fixtures, and real
   upload, projection refetch, signed download, tamper denial, crafted POST denial, lifecycle guard,
   and resubmission calls. Mock only genuine external adapters; browser booleans/fixture responses
   cannot stand in for backend outcomes.
2. Make GET and POST consume one application/checklist-locked portal action-authority interface.
   Projection must not combine pre-lock application status with post-lock checklist truth. A
   completion/upload race returns one coherent state, and every denied writer leaves no file,
   submission, audit, workflow, or version artifact.
3. Resolve published Term Sheet/Loan Agreement downloads through the canonical latest current
   renderer, not a stale checklist-item pointer. A production generation successor must invalidate
   the old descriptor/capability and immediately drive the borrower-safe projection; tests may not
   simulate replacement by assigning the checklist FK directly.
4. Retain exactly one source-defined portal audit action for each critical upload/download through
   the central document audit writer: `portal.document.uploaded` and
   `portal.document.downloaded`, with actor/member/application/document/version/category/
   sensitivity/reason/request/network/outcome facts. Do not double-write a parallel portal and
   generic event, and do not expose sensitive or storage facts.
5. Keep deficiency-response history honest after resubmission: the borrower projection and retained
   workflow evidence must agree on whether the current immutable response is `responded` or
   `submitted_for_review`, while the staff-owned deficiency remains open until staff resolution.
   Re-upload extends the immutable chain and never rewrites a submitted response.
6. Preserve the approved MP07/MP11/MP13 composition and CR-005 independent status/download rule.
   Run the real-boundary trusted browser specs twice at the declared desktop/mobile viewports and
   produce all four screenshots from production responses.

## Trusted Browser Acceptance

- Spec: `e2e/member-portal-documentation-actions.e2e.spec.ts`
- Spec: `e2e/member-portal-deficiency-response.e2e.spec.ts`
- Screenshot: `portal-documentation-upload-modal.png`
- Screenshot: `portal-documentation-complete-upload-denied.png`
- Screenshot: `portal-deficiency-mobile-response.png`
- Screenshot: `portal-deficiency-resubmitted.png`

## Test Cases

- Real login/session and own-scope data drive both Playwright specs with no catch-all API route.
- Current completion versus upload and generation versus descriptor/content reads are coherent and
  zero-write for losers.
- A real successor generation invalidates the old signed token without direct ORM pointer edits.
- Portal upload/download create exactly the source-defined single audit event with complete safe
  metadata; tamper, cross-scope, expiry, and replacement create none.
- Upload, re-upload, resubmit, replay, and staff resolution expose truthful response/deficiency
  states and preserve the application transition guard.

## Evidence Required

Failing-first real-boundary/browser, lock-parity, current-generation, audit-vocabulary, and response-
state probes; focused/full gates; real API examples; Playwright collection; twice-run trusted logs;
and all four genuine non-empty screenshots.

## Risk Level
High

## Acceptance Criteria

- Browser evidence proves the production authentication/API/state boundaries end to end.
- Portal read/write/download authority is locked to current server truth.
- Retained audit and response-state facts match source vocabulary without parallel ledgers.
- Existing visual composition and privacy constraints remain unchanged.
- All configured gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
