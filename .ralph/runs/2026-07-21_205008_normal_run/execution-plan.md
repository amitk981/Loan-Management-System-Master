# Execution Plan

Selected slice: `010N2-epic-010-terminal-servicing-recurrence-repair`

## Boundary

- Repair only the inherited CR-015 terminal contract for MIS cutoff truth and servicing acceptance seams.
- Preserve the already-closed reminder delivery owner and its five-case PostgreSQL contract.
- Do not change frontend styling, financial allocation policy, reminder policy, protected files, source documents, or orchestrator-owned state/status bookkeeping.

## TDD sequence

1. Add a public servicing builder and convert the direct-repayment regression away from importing or invoking another `TestCase.setUp`; run the exact recurrence contract probe RED before the edit and GREEN after it.
2. Add real-model invoice lifecycle regressions for generated before/on/after cutoff, including issued-after-cutoff truth; run the focused selector RED, then minimally correct quarterly MIS invoice admission/status using immutable `generated_at` and `issued_at`.
3. Extend the permanent public-seam matrices required by AC-E10-R2 through AC-E10-R4 only where current coverage is incomplete: historical mutable-source/replay truth, repayment replay/effect assertions, statement concurrency, borrower-safe export, approved instructions, and portal/reminder 1/100/101 completeness.
4. Replay the two recurrence commands and all three original CR-015 review commands exactly, retaining each command and positive exit evidence in this run.
5. Run the focused backend regression module, Django checks and migration sync, the exact five-test PostgreSQL class twice, and applicable frontend focused tests/typecheck/lint/build without running the complete backend suite.

## Evidence and closure

- Save distinct RED/GREEN terminal logs with exact permanent test selectors.
- Create `review-closure-evidence.md` mapping both finding IDs and AC-E10-R1 through AC-E10-R5.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md` with source-to-code-to-test traceability.
- Run the mandated review-closure validator until it prints `PASS`, leaving `review-packet.md` Result exactly `Ready for independent validation`.
