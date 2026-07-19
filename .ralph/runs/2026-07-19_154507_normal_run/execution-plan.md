# Execution Plan

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`

1. Preserve scope and safety: verify the selected CR is concrete, dependencies are complete, paths
   are permitted, and the worktree has no unexpected product changes. Record affected modules in
   `impact-analysis.md` before code edits.
2. Write failing backend seed regressions first. Prove the doubly guarded Epic 009 fixture is
   idempotent, creates deterministic Credit Manager/Senior Finance/CFC actors and real owner state,
   and exposes that state through the real Loan Account/workspace endpoints. Save RED output.
3. Implement the smallest guarded, isolated fixture composition needed by the trusted flow, using
   existing models/services/evidence contracts without changing production API, permission, money,
   workflow, or UI behavior. Run the focused tests and save GREEN output.
4. Rewrite the Epic 009 Playwright spec to log in through the real staff form, consume only real
   Django responses for owned APIs, capture the account list plus eight retained states, assert exact
   state evidence immediately before each capture, and write/check a deterministic manifest whose
   nine SHA-256 values are all distinct.
5. Run Playwright collection/non-browser checks locally, the focused backend seed/API tests, impacted
   frontend tests, typecheck, lint, and build. Do not fabricate screenshots if Chromium cannot launch;
   the orchestrator will execute the trusted browser contract twice outside the sandbox.
6. Audit the targeted diff for forbidden routes/stubs, sensitive fixtures, scope creep, and protected
   paths. Save terminal evidence, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`, with
   the review result exactly `Ready for independent validation`.
