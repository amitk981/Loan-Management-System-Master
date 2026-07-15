# Execution Plan

Selected slice: 008L3-portal-action-and-resubmission-contract-closure
Mode: repair

1. Preserve the quarantined 008L3 implementation and use the trusted Playwright failure at
   `member-portal-deficiency-response.e2e.spec.ts:50` as the exact feedback signal.
2. Change only the stale post-resubmission status assertion: scope it to the application header and
   expect the shared `StatusBadge` label `Submitted - Pending Completeness Check`. Preserve the
   following exact absence assertion for the `Deficiency Response` heading and every prior selector.
3. Run focused Playwright collection/static verification and the proportionate frontend quality
   gates. Do not change backend, database, or production application code for this acceptance-only
   mismatch.
4. Save repair evidence and update the run review packet, risk assessment, changed-files list, and
   final summary. Leave full outside-sandbox browser revalidation to the orchestrator.
