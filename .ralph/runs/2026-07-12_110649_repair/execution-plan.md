# Repair Execution Plan

Selected slice: 006Y4-witness-correction-and-resource-action-closure

1. Use the trusted browser witness test as the exact feedback loop and inspect only the capture
   request, seeded witness/shareholding facts, and the returned `400` validation envelope.
2. Rank and test narrow hypotheses for the deterministic capture failure, preserving the existing
   uncommitted 006Y4 implementation.
3. Add or tighten a regression assertion at the correct seam if the existing test does not catch
   the demonstrated fixture/contract mismatch, then apply only the minimal repair.
4. Re-run the focused browser contract (or the closest deterministic collection/API seam if local
   Chromium services are denied), followed by the configured frontend/backend gates needed to
   ensure the repair does not regress the completed slice.
5. Save repair evidence and refresh changed-files, risk-assessment, review-packet, final-summary,
   state, progress, handoff, and slice status without committing, adding, or pushing.

Permissions check: the expected repair is limited to `sfpcl-lms/e2e/**` and Ralph run artifacts;
these are allowed by `.ralph/permissions.json`. If diagnosis instead demonstrates a product defect,
edits will remain within allowed `sfpcl-lms/src/**` or `sfpcl_credit/**` paths. No protected,
approval-required, forbidden, or `docs/source/**` path will be modified.
