# Execution Plan

Selected slice: CR-012-epic-009-playwright-evidence-is-incomplete

1. [Complete] Preserve and classify the previous trusted-browser failure; treat its real HTTP 400 and partial
   screenshot set as the red feedback loop.
2. [Complete] Inspect the Playwright transfer request and the backend chronological validation just deeply enough
   to distinguish stale timestamp, precision/skew, seed, and stale-workspace hypotheses.
3. [Complete] Add or tighten the browser regression assertion before the fix so the request timestamp is proven
   to be later than the returned CFC authorisation evidence, retaining red evidence.
4. [Complete] Apply the smallest spec-only fix; do not alter production workflow, permissions, API shapes, seed
   truth, UI behavior, or screenshot validation.
5. [Complete] Run focused Playwright collection/browser feedback, relevant frontend tests, typecheck, lint, and
   build. Save red/green and quality evidence in this run folder.
6. [Complete] Review the bounded diff, record risk and traceability, and set the review result exactly to
   `Ready for independent validation` for Ralph's two authoritative browser runs and complete gates.
