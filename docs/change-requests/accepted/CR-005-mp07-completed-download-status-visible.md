# Show completed document status alongside retained downloads

## Type
bug-frontend

## Severity
High

## What Is Happening
On the member portal My Documents screen, a documentation action with status `complete` does not display the Complete status when it also retains a downloadable document. The MP07 renderer only shows the status badge when download, upload, and re-upload are all unavailable. The trusted 008L3 browser test therefore times out waiting for Complete, the fourth required screenshot is not produced, and Ralph stops without accepting the slice.

## Expected Behaviour
A completed documentation action must visibly show Complete while retaining its authorised Download control. Upload and re-upload controls must remain absent after completion. The existing approved MP07 composition and styling must be reused.

## Steps To Reproduce
1. Sign in as a borrower portal member with a sanctioned application.
2. Open My Documents and upload the pending Term Sheet.
3. Move to Documentation and return after the server projection reports the Term Sheet as complete while retaining its download descriptor.
4. Observe that Download remains visible but the Complete status is missing.
5. Run the two declared 008L3 Playwright specs and observe `getByText('Complete', { exact: true })` time out in both trusted runs.

## Where It Appears
Member Portal MP07 My Documents (`sfpcl-lms/src/pages/borrower/portal/documents/MP07_DocumentChecklist.tsx`) and the 008L3 trusted browser contract (`sfpcl-lms/e2e/member-portal-documentation-actions.e2e.spec.ts`).

## Source Document Reference
`docs/source/screen-spec-member-portal.md` MP07 and MP13; `docs/slices/008L3-portal-action-and-resubmission-contract-closure.md` visual acceptance and browser evidence requirements. The observed failure is preserved in `.ralph/runs/2026-07-15_140951_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log` and `trusted-browser-acceptance-2.log`.

## Acceptance Criteria
- A completed documentation action visibly renders the canonical Complete status even when its Download control remains available.
- The completed action exposes neither Upload nor Re-upload.
- A frontend regression test proves the completed-and-downloadable state through the rendered MP07 interface.
- Both declared 008L3 Playwright specs pass twice using the trusted browser command.
- All four declared screenshots are genuine, non-empty, and saved, including `portal-documentation-complete-upload-denied.png`.
- Full frontend and backend quality gates run once after the focused E2E loop is green.
