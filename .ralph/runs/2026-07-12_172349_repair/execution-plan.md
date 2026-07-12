# Execution Plan

Selected slice: `006Y9-member-form-real-session-closure`

1. Reproduce the trusted-browser declaration failure with Ralph's read-only parser helper and save
   the red output. Compare the selected slice with a known-passing browser contract.
2. Repair only the selected slice's `Trusted Browser Acceptance` declaration grammar: use the
   project-relative spec path and exact screenshot basenames required by the existing Playwright
   implementation. Do not alter production code or the preserved browser scenario unless a later
   trusted run demonstrates a separate runtime failure.
3. Re-run the parser/contract validator as the tight green loop, then run Playwright collection and
   the configured frontend/backend quality gates. Save evidence with the mandated backend Python.
4. Update repair artifacts, changed-files, risk/review/final summaries, and Ralph state/handoff only
   to reflect the independently revalidatable repair. Preserve all prior slice implementation.
