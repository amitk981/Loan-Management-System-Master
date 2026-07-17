# Ralph Handoff

## Last Run
2026-07-17_105635_architecture_review

## Current Status
Architecture review independently examined 008M7, 009D4, 009E2, and 009F over
`24bfc4f4...277f6c8f` in isolated Standards and Spec passes. Four focused retained tests pass. Four
review-only probes fail as expected: active source-bank governance accepts null proof, a positive
lesser amount is rejected, beneficiary-bank drift still permits CFC approval, and pending rows with
pre-existing UTR/disbursed/register truth can be approved. No production code changed.

The review also found incomplete source-bank effective history and a missing production permission-
catalogue entry, under-constrained authorisation/transfer tuples, duplicated CFC scope/action
reconciliation, a private source-shape test, and a genuine-owner fixture that directly inserts the
loan account. 008M7/009D4 otherwise substantively meet their current-tail/role/signature targets.
Findings, source traceability, severity, probe output, and corrective ownership are retained in this
run and `REVIEW_FINDINGS.md`.

## Next Run
Run 009E3 to restore lesser-amount behavior, real loan-owner proof, a grantable unassigned Critical
source-bank permission, complete activation/deactivation history, and PostgreSQL race integrity.
Then run 009F2 to restore current borrower/source-bank evidence, complete aggregate constraints,
scope/action parity, and the full CFC role matrix. Only then run 009G, which now depends on 009F2 and
must consume its exact typed current-evidence decision before UTR, funding, and activation.
