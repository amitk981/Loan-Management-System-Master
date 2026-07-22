# Execution Plan

Selected slice: 011G-closure-readiness

## Permission and scope check

- Preserve the existing 011G candidate and repair only the failed complete-backend validator domain.
- Product edits, if required, are limited to `sfpcl_credit/**`; repair evidence is limited to
  `.ralph/runs/2026-07-22_200332_repair/**`.
- Do not edit protected files, source documents, state/progress, slice status, mechanical handoff,
  scripts, gate configuration, or unrelated future slices.
- No frontend work is required.

## Demonstrated failure

The complete backend coverage validator failed in
`DefaultGraceAssessmentApiTests.test_early_paid_closed_foreign_and_unauthorised_assessments_are_rejected`.
The test attempts to reopen a closed loan with an ordinary queryset `update()`, which 011G now
correctly rejects under the source-mandated closed-account immutability guard.

## Repair sequence

1. Run the single failing Django test with the mandated Ralph Python interpreter and retain the RED
   output as the tight deterministic reproducer.
2. Confirm the existing sanctioned fixture transition pattern and change only this legacy test's
   setup transition so it no longer asks the public mutation path to violate closed-loan
   immutability; preserve every API rejection assertion.
3. Rerun the single test GREEN, then rerun the containing default-grace assessment test module and
   the focused closure/direct-repayment mutation tests to guard both sides of the interaction.
4. Run Django system check and migration consistency. Do not run the complete suite or coverage
   locally; Ralph's independent validator owns the authoritative complete lane.
5. Inspect targeted diff/stat and protected-path status, then finish repair evidence,
   risk-assessment.md, review-packet.md, and final-summary.md. Set the review result exactly to
   `Ready for independent validation` only after focused validation is green.
