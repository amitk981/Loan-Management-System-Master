# Execution Plan

Selected slice: architecture-review

1. Pin the previous successful architecture-review commit and enumerate every merged slice and
   changed path in the review range.
2. Read only those completed slice specifications, their cited Epic 009/CR source material,
   relevant digests, architecture standards, and retained run evidence.
3. Run independent Standards and Spec review passes over the fixed three-dot diff, then inspect
   test assertions, edge cases, requirement-ID coverage, duplication, dependency direction, and
   architecture drift as the primary reviewer.
4. Execute focused read-only review probes where static inspection leaves a material question;
   save terminal output under this run's `evidence/terminal-logs/` directory.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`; create or sharpen concrete,
   dependency-valid corrective slices for every significant issue. Record an ADR only if this
   review establishes a new durable architecture decision.
6. Re-check blocked slices and the truthfulness of `docs/working/CONTEXT.md`, then update Ralph
   state, progress, handoff, review packet, risk assessment, changed-files list, and final summary.
7. Verify the documentation-only diff, queue structure, artifact completeness, and protected-path
   safety without modifying or rerunning unchanged production gates.

Production code, configuration, protected files, and `docs/source/` remain read-only throughout.
