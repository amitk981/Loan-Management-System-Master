# Execution Plan

Selected slice: 006Y8-witness-maker-checker-and-browser-closure

Repair only the demonstrated trusted-browser failure from run
`2026-07-12_152923_repair`, preserving the quarantined 006Y8 implementation.

1. Reproduce from the prior trusted-browser logs and identify the rendered account/sign-out
   contract used by the real application shell after a full reload.
2. Add or adapt the narrowest browser-test helper so session switching uses a stable accessible
   control rather than assuming the signed-in email is visible; do not change witness business
   logic or production UI unless the shell itself is proven defective.
3. Run Playwright collection and the slice-specific browser contract when Chromium is available;
   retain honest evidence if the coding sandbox denies launch. Run the focused frontend tests and
   all configured frontend/backend gates required for the touched surface.
4. Save terminal evidence, changed-files, risk assessment, review packet, and final summary;
   update Ralph state/progress/handoff and keep the already-complete slice status accurate.

Feedback loop:
`E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/witness-correction-authority.e2e.spec.ts`

Red symptom: both trusted runs time out in `signOut()` waiting for visible text
`e2e.credit.finance@sfpcl.example` after the canonical reload, preventing the checker session and
third screenshot.
