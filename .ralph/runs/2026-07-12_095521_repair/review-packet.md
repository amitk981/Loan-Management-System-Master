# Review Packet: 2026-07-12_095521_repair

## Result
Ready for independent validation

## Slice
006Y3-member-registry-and-identity-change-approval-closure

## Demonstrated Failure and Fix

Both prior trusted runs executed an obsolete 006Y2 visual-baseline flow and failed on
`member-reverification.png`; none of the five filenames declared by 006Y3 could be emitted. The
spec now performs the exact declared real-session journey and writes:

- `member-create-submitted.png`
- `member-update-refetched.png`
- `member-identity-change-requested.png`
- `member-identity-change-approved.png`
- `member-governance-denied.png`

The isolated E2E Credit Manager now receives member read plus the dedicated approval permission,
allowing a distinct checker without assigning that permission to any production role.

## Traceability

- M02-FR-012 requires an approved identity-change request: the browser contract requests as Deputy
  Manager Finance and approves as a distinct Credit Manager synthetic actor.
- The slice requires canonical refetch after success: the test awaits and asserts the member GET
  after create, update, request, and approval.
- The slice requires denial proof: the zero-permission real session has no member navigation and a
  direct mutation returns one `403 PERMISSION_DENIED` response.
- The slice's Trusted Browser Acceptance section names the spec and five outputs exactly; the new
  contract matches all six declarations.

## Validation

- Focused E2E checker fixture: failing first, then passing.
- Playwright collection: one contract collected successfully.
- Local Playwright execution: Chromium blocked before the test body by macOS Mach service denial;
  log retained, screenshots not fabricated.
- Frontend: build, typecheck, lint, 171/171 tests pass.
- Backend: Django check, migration sync, 414/414 tests pass; coverage 94% (floor 85%).

## Recommended Next Action
Run the declared browser contract twice outside the sandbox and accept only if all five screenshots
are non-empty on both runs; then proceed to already-sharpened 006Y4.
