# Execution Plan

Selected slice: 006Z8-portal-limit-provenance-module-and-interaction-closure

1. Reproduce the independent gate's exact trusted-browser contract failure with
   `ralph_validate_trusted_browser_acceptance`, preserving the current implementation and recording
   the parser output in this repair run's terminal evidence.
2. Compare the slice's `## Trusted Browser Acceptance` entries with the validator grammar and the
   existing spec path; change only the malformed contract metadata demonstrated by the failure.
3. Re-run the focused validator and Playwright collection, then run the relevant workflow parser
   regression. Do not fabricate screenshots or treat sandbox Chromium limitations as product failure.
4. Run the configured quality gates in proportion to the metadata-only repair and refresh this run's
   changed-files, risk assessment, review packet, final summary, progress, state, and handoff records.

Risk controls: no production-code edits; no protected/source edits; preserve the uncommitted 006Z8
implementation; do not change browser assertions, screenshot names, or runtime capability.
