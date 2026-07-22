# Execution Plan

Selected slice: 011K-compliance-control-tracker-foundation
Mode: same-worktree repair
Failed validation domain: backend complete-suite coverage

1. Preserve the current 011K candidate and reproduce the reported schema failure with the exact
   focused test
   `sfpcl_credit.tests.test_witness_evidence_migration.WitnessEvidenceMigrationTests.test_backfill_is_idempotent_and_reverse_preserves_legacy_rows`.
2. Inspect only the witness model/migration state and the failing historical-migration test to find
   why its historical database schema no longer matches the model class used to create legacy rows.
3. Rank and test bounded hypotheses; add or adjust the migration regression first so it remains
   red-capable for this exact missing-column failure, then make the smallest schema-state fix.
4. Save focused RED/GREEN output under this run's `evidence/terminal-logs/`, then run the complete
   witness migration test class, Django migration-sync check, and the slice-focused compliance tests.
5. Rerun the exact failed validator command from the prior gate:
   `/Users/amitkallapa/LMS/scripts/ralph-parallel-backend-coverage.sh /Users/amitkallapa/LMS/.ralph/venv/bin/python /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-23_014100_normal_run sfpcl_credit 6 85`.
6. Update this run's risk assessment, review packet, evidence summary, and final summary. Set the
   review-packet Result exactly to `Ready for independent validation` only after all focused checks
   and the exact validator pass.

Permissions checked: product/test/migration files under `sfpcl_credit/**` and run evidence under
`.ralph/runs/**` are writable. Protected workflow files, `docs/source/**`, orchestrator-owned state,
slice status, changed-files, progress, and mechanical handoff will not be edited.

## Completion

- Exact focused failure reproduced and saved RED.
- Historical projection repair applied and the same test saved GREEN.
- Django check, migration sync, and 11 focused migration/compliance tests passed.
- Exact six-worker backend coverage validator passed 1,674 tests with 89% coverage.
- Risk assessment, review packet, evidence summary, and final summary completed.
