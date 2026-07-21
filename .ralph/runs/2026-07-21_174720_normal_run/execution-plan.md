# Execution Plan

Selected slice: `010N-global-search-api-and-ui`

1. Map the six existing result owners, their established permission/object-scope selectors, sensitive keyed-hash helpers, response envelope, frontend transport, and current S02/Header prototype without altering protected or source files.
2. Write focused backend tests first for the grouped response contract, all 15 search inputs, deterministic per-group pagination/caps, compliance-provider emptiness, audit authority, object-scope nondisclosure, safe query validation/rate limiting, masking, and absence of raw sensitive query material from audit/log payloads. Save the expected RED output under `evidence/terminal-logs/`.
3. Implement one registered global-search provider seam and a thin API coordinator over the existing domain owners. Reuse stored hashes/suffixes and owner selectors, expose only server-owned card projections/actions, and add no more than one non-destructive index migration if query-plan inspection demonstrates a missing contracted index.
4. Write/update frontend request and render tests before production UI changes, then wire `GlobalSearchResults.tsx` and Header search navigation to the API while preserving existing design patterns and loading, empty-query, partial-group, no-results, safe-error, and unauthorised states. Remove only the mock search paths owned by 010N.
5. Add the declared Playwright contract and deterministic mocked-network states for `global-search-results.png` and `global-search-empty.png`; locally collect/test without treating a sandbox Chromium launch denial as product failure.
6. Update the working API contract and prototype inventory/gap ledger, then run focused backend GREEN tests with the mandated interpreter, impacted frontend tests, typecheck, lint, build, Django check, and migration-sync checks. Save terminal logs plus query-plan/index and mock-removal proof.
7. Inspect changed-file/line limits and targeted diffs, complete `risk-assessment.md`, `final-summary.md`, and `review-packet.md`, and set the packet result exactly to `Ready for independent validation` without changing Ralph-owned mechanical state, progress, slice status, or Git metadata.
