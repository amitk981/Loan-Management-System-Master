# Execution Plan

Selected slice: 006Y9-member-form-real-session-closure
Mode: repair

1. Preserve the quarantined implementation and reproduce the demonstrated trusted-browser failure
   from the prior run's exact Playwright log.
2. Tighten only the ambiguous masked-Aadhaar assertion in
   `e2e/member-governance-variants.e2e.spec.ts`; do not change production behavior because the log
   proves the canonical refetch and masked render succeeded.
3. Run Playwright collection, the slice-specific browser scenario when Chromium is available, and
   the configured frontend/backend gates with the mandated interpreters.
4. Save self-contained red/green evidence and complete changed-files, risk, review, final-summary,
   state, progress, handoff, and slice-status artifacts for independent revalidation.
