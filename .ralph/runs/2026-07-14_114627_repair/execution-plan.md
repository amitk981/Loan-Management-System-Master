# Execution Plan

Selected slice: 008B3-document-renderer-and-output-proof-closure

## Repair boundary

Preserve the quarantined 008B3 implementation and repair only the independently demonstrated PDF
content-validation failure in the legal-document renderer. Do not alter the established generation
authority, replay identity, storage cleanup, DOCX handling, A-101 blocker, or A-102 constraint.

## Feedback loop

Run the two failing PDF API tests with the orchestrator-managed backend interpreter. Capture their
current deterministic `borrower_name` readability failure as RED evidence, then reduce to a direct
renderer/content-extraction probe that distinguishes font extraction loss from whitespace,
pagination, and markup hypotheses.

## Implementation

1. Add or tighten the smallest regression assertion at the real renderer/API seam before changing
   renderer behavior.
2. Correct only the verified PDF render-or-validation defect, keeping bounded entry/text/value,
   page-count, and output-size enforcement intact.
3. Capture targeted GREEN evidence, parse the generated PDF again with pypdf, and retain exact
   Unicode, Indian-currency, long-text, and safe-value assertions.

## Validation and closeout

Run frontend build/typecheck/lint/tests and backend check, migration sync, full coverage suite, and
the focused renderer tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`. Save terminal
logs, generated artifact proof, changed-files, risk assessment, review packet, and final summary.
Reconcile Ralph state/progress/handoff/slice status only after all local gates pass; leave commit,
merge, push, and full independent revalidation to the orchestrator.
