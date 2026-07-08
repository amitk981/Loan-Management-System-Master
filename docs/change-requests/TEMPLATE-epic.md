# Epic <NNN>-<epic-slug>: <NNN>: <Epic Title>

<!--
HOW TO USE (delete this comment block when done):
- Use this template ONLY when an accepted change request is so large it needs its
  own family of slices (a new module or capability area). Most changes never need
  an epic — a single CR-NNN slice from ./scripts/ralph-intake.sh is enough.
- Save the finished file as docs/epics/<NNN>-<epic-slug>.md, using the next free
  epic number (check docs/epics/).
- An epic is planning context only — it is never implemented directly. Break the
  actual work into child slices under docs/slices/ using TEMPLATE-slice.md, each
  registered in docs/working/IMPLEMENTATION_SLICE_INDEX.md.
- Keep section names exactly as written; agents build digests from these sections.
-->

This parent epic preserves the broad planning context. Actual implementation work
is broken into smaller child slices under `docs/slices/`.

## Origin
<the accepted change request this epic came from — link the file in
docs/change-requests/accepted/ and the acceptance date>

## Goal
<one paragraph: the whole capability this epic delivers when all child slices are done>

## User Value
<plain sentences: which users benefit and what they can do once the epic is complete>

## Depends On
- <epic or slice IDs that must be Complete first>

## Source References
- <docs/source/... files and section numbers that define the behaviour>
- <for owner-approved changes with no source section, write: "Owner approved — see accepted change request">

## Screens Involved
- <screen names, or "None (backend only)">

## Prototype Reference
- <sfpcl-lms/src/... files, or "None">

## Frontend Scope
- <bullet list of the frontend work across the whole epic>

## Backend/API Scope
- <bullet list of the endpoints/services across the whole epic>

## Database/Model Impact
- <tables/fields this epic adds or changes, or "None">

## API Contracts
- <contract areas in docs/working/API_CONTRACTS.md this epic owns>

## Permissions
- <which roles may do what, per docs/source/auth-permissions.md>

## Validation Rules
- <the business rules this epic must enforce, each traceable to a source section>

## Test Cases
- <the major test areas child slices must cover between them>

## Visual Acceptance Criteria
- <what the owner should see when the epic's screens are reviewed>

## Evidence Required
- API tests and sample responses.
- Screenshots of the epic's key screens and states (self-contained evidence —
  see docs/working/AFK_RUNBOOK.md).

## Risk Level
<Low | Medium | High>

## Acceptance Criteria
- <observable outcome 1 for the epic as a whole>
- <observable outcome 2>

## Child Slices
<list the planned child slices in order, e.g.:>
- `<NNN>A-<kebab-title>` — <one-line scope>
- `<NNN>B-<kebab-title>` — <one-line scope>

## Done Checklist
- [ ] All child slices created in docs/slices/ and registered in docs/working/IMPLEMENTATION_SLICE_INDEX.md
- [ ] All child slices Complete
- [ ] Epic acceptance criteria verified against the running system
