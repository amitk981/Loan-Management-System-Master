# Execution Plan

Selected slice: `008M-documentation-hub-frontend-wiring`

Repair target: preserve the quarantined 008M implementation and correct only the demonstrated
diff-limit failure (2,084 changed lines against a 2,000-line cap).

1. Reproduce the exact validator arithmetic with the repository's own tracked-plus-untracked line
   counting rules, and record the failing count before any product edit.
2. Rank and test narrow reduction options in slice-owned implementation/tests/documentation. Remove
   redundant lines only; do not split the atomic workspace contract, weaken assertions, alter the
   source-required UI, or touch protected/source files.
3. Re-run the exact line-count loop until it is below 2,000, then run the focused backend workspace
   tests and frontend documentation tests to prove behavior is unchanged.
4. Run all configured frontend and backend quality gates with the mandated interpreter, saving
   outputs under this run's evidence directory. Confirm no protected paths or debug artifacts.
5. Complete current-run evidence, changed-files, risk assessment, review packet, final summary,
   state/progress/handoff, and the selected slice status. Retain the already-sharpened next slice
   unless an already-opened digest fact materially improves it.
