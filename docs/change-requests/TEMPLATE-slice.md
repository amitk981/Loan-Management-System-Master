# Slice <ID>: <Short Title>

<!--
HOW TO USE (delete this comment block when done):
- Use this template ONLY when a change is too big for the automatic CR-NNN slice
  that ./scripts/ralph-intake.sh generates — i.e. the work needs more than one
  narrow run. For ordinary bugs/features, use TEMPLATE-bug.md / TEMPLATE-feature.md
  and let intake create the slice for you.
- Save the finished file as docs/slices/<ID>-<kebab-title>.md
  (e.g. docs/slices/013A-notification-digest-api.md). Ralph picks the lowest
  filename-sorted "Not Started" slice, so the ID controls queue position.
- Register the slice in docs/working/IMPLEMENTATION_SLICE_INDEX.md (add a table row).
- Section names below must stay exactly as written — scripts and agents read them
  (e.g. "## Status" and "## Risk Level" are parsed by the run scripts).
- Keep the slice NARROW: one vertical, testable capability per run (~one sitting).
  If a section keeps growing, split it into two slices.
-->

## Status
Not Started

## Runtime Capabilities
- <`postgresql-five-race-acceptance` when the exact authoritative PostgreSQL race gate is required; otherwise `none`. Unknown values fail closed.>

## Parent Epic
Epic <NNN>: <Epic Title>
Epic file: `docs/epics/<NNN>-<epic-slug>.md`

## Origin
<why this slice exists — e.g. "Change request CR-007, accepted YYYY-MM-DD, split into an epic because it spans multiple modules" — link the accepted file in docs/change-requests/accepted/>

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
<one or two plain sentences: what a real user can do or trust after this slice that they could not before>

## Depends On
- <slice ID(s) that must be Complete first, or "None (independent)">

## Source References
- <docs/source/... file and section numbers that define the correct behaviour>
- <docs/working/digests/... digest if one exists for the parent epic>
- <for owner-approved design changes with no source section, write: "Owner approved — see accepted change request">

## Prototype Reference
- <sfpcl-lms/src/... files whose existing patterns must be reused, or "None">

## Screens Involved
<screen name(s), or "None (backend only)">

## Frontend Scope
<exactly what the frontend part does — which existing patterns to reuse, which states
(loading, empty, error, unauthorized, validation, success) must exist. Follow
docs/working/FRONTEND_DESIGN_RULES.md: reuse existing components/patterns, never
introduce new styling. Write "None" if backend only.>

## Backend/API Scope
<exactly which endpoint(s)/service(s) this slice implements, with method + path.
Just as important: list what this slice must NOT implement, so the agent does not
wander into neighbouring slices' territory.>

## Database/Model Impact
<new tables/fields/migrations, or "None". Non-destructive migrations only; follow
docs/working/DATABASE_RULES.md.>

## API Contracts
<which entries in docs/working/API_CONTRACTS.md to create or update, or "None">

## Permissions
<which permission codes gate each action; expected 401/403 behaviour. If the source
catalogue has no exact code, say which narrowest source-backed code to use and that
the assumption must be recorded in docs/working/ASSUMPTIONS.md.>

## Audit Requirements
<which actions must write audit logs / workflow events, or "None — record the
read/no-audit decision in the review packet">

## Validation Rules
<input validation and business rules this slice enforces, with the source section
that states each rule. Unknown query parameters/fields follow the standard
400 VALIDATION_ERROR pattern.>

## Test Cases
<TDD list: backend failing-test-first cases (success, validation, 401/403, edge
cases) and frontend state tests. Name at least one regression test that pins the
bug/behaviour this slice exists for.>

## Visual Acceptance Criteria
<what the owner should see when reviewing evidence, or "Not applicable (backend only)".
Match existing prototype patterns; include loading, empty, error, unauthorized,
validation, and success states where relevant.>

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.
<list the specific states/screens to capture. Evidence must be self-contained —
see "Evidence and Review" in docs/working/AFK_RUNBOOK.md.>

## Risk Level
<Low | Medium | High — High means auth, money, sensitive data, or cross-stack changes>

## Acceptance Criteria
- <observable behaviour 1 — plain words, testable>
- <observable behaviour 2>
- Source-doc business rules are enforced or documented as assumptions.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
