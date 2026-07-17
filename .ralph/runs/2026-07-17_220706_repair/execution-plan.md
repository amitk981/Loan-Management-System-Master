# Execution Plan

Selected slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure

1. Preserve the quarantined 009G3 implementation and diagnose only the two failures recorded in
   `2026-07-17_220014_repair/failure-summary.md`.
2. Use `makemigrations --check --dry-run` as the tight deterministic feedback loop and save its RED
   output; confirm whether the model/schema mismatch also explains the coverage worker's missing-
   column error.
3. Add only the missing disbursements-owned migration for the already-implemented protected
   `register_update` relation and amended success-evidence constraint, preserving existing ids and
   behavior.
4. Re-run the migration check, focused 009G3 transfer-success tests, Django check, and migration
   plan/apply feedback with the mandated backend interpreter; save GREEN output.
5. Review the final diff for protected paths and repair-scope drift, then complete changed-files,
   risk, review, final-summary, state/progress/handoff, and slice-status artifacts for independent
   orchestrator validation. Recheck the next concrete Not Started slices without speculative edits.
