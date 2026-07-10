# Execution Plan

Selected slice: 004K2-borrower-360-bank-holder-contract-hardening

## Scope
- Fix only the Borrower 360 frontend bank-account DTO mismatch identified by architecture review.
- Keep the backend/API contract field `account_holder_name` canonical.
- Preserve masked-only bank account rendering with `can_view_full: false` and no bank reveal affordance.
- Do not change backend behavior, database models, permissions, audit behavior, or visual styling.

## TDD Plan
1. Update the Borrower 360/frontend API tests first so the bank-account fixture uses backend response shape `account_holder_name`.
2. Add/strengthen a regression that fails when Borrower 360 does not render `account_holder_name`.
3. Capture the failing frontend test output under `evidence/terminal-logs/`.
4. Update the frontend `MemberBankAccountDetail` type, bank-account normalizer, and Borrower 360 rendering to use `account_holder_name`.
5. Re-run the focused frontend tests and save green output.

## Verification Plan
- Run the focused Borrower 360 test suite.
- Run frontend typecheck, tests, lint, and build from `sfpcl-lms/`.
- Run backend gates even though no backend code is expected to change: `manage.py check`, backend tests, migrations check, and coverage with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Save changed files, risk assessment, review packet, final summary, and terminal logs in the run folder.

## Documentation/State Updates
- Update this slice status and checklist after gates pass.
- Update `.ralph/state.json`, `.ralph/progress.md`, and `docs/working/HANDOFF.md`.
- Sharpen the next 1-2 `Not Started` slices using already-opened digest/source context only.
