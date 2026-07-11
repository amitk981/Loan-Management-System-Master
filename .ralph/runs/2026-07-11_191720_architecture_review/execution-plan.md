# Execution Plan - Architecture Review 2026-07-11_191720_architecture_review

Selected slice: `architecture-review`

## Objective

Independently review the four completed corrective/product slices merged after prior
architecture-review commit `d5632d2` and through `HEAD` (`4d1351f`): `005E2`, `005FA3`, `006G4`,
and `006H5`. Do not modify production code.

## Review Method

1. Pin and save the review window, commit list, per-slice changed files, and run packets. Treat the
   intervening orchestrator-only commits as out of product-review scope while checking that they do
   not obscure slice diffs.
2. Read the four completed slice specifications, parent epic/digest requirements, cited source
   sections, and repository standards needed to assess API, architecture, frontend, and test
   fidelity.
3. Run independent Standards and Spec reviews in parallel, then personally verify every candidate
   finding against code, tests, and evidence. Check real assertions, edge cases, duplication,
   architecture drift, and closure of the previous review's corrective findings.
4. Reconcile functional requirement IDs for any epic completed in this window, verify
   `CONTEXT.md`, inspect every Blocked slice for stale prerequisites, and inspect the next two
   Not Started slices for implementation-ready sharpening.
5. Append the newest-first entry to `docs/working/REVIEW_FINDINGS.md`. Create or sharpen corrective
   slices for significant findings; record an ADR only if the review establishes a new durable
   architectural decision.
6. Run configured frontend/backend quality gates plus documentation/diff checks, saving terminal
   output under this run's `evidence/terminal-logs/`.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; update
   `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, and the architecture-review
   descriptor consistently for orchestrator validation.

## Permissions and Safety

- Allowed edits are limited to `.ralph/runs/**`, `.ralph/state.json`, `.ralph/progress.md`,
  `docs/working/**`, `docs/slices/**`, `docs/epics/**`, and `docs/adr/**` as permitted by
  `.ralph/permissions.json`.
- Production paths and all protected/read-only paths remain untouched.
- Backend commands use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` exactly.
