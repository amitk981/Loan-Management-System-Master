# Execution Plan

Selected slice: 006Y9-member-form-real-session-closure

1. Reproduce the trusted-browser failure with the existing real-session Playwright spec and use
   its exact missing identity-governance control as the repair feedback loop.
2. Inspect the seeded actors' server-projected member actions and the profile container's rendering
   predicate; rank and test hypotheses without changing production authority.
3. Add or tighten the smallest regression assertion at the real profile-container seam, capture a
   failing result, then make only the demonstrated rendering/selector repair and capture green.
4. Re-run the slice-specific Playwright scenario locally when Chromium is available; otherwise run
   collection plus the focused interaction test and record the sandbox limitation for independent
   trusted-browser validation.
5. Run all configured frontend/backend gates, save evidence and review artifacts, verify protected
   paths/diff limits, and update Ralph progress/state/handoff without committing or pushing.
