# Ralph Handoff

## Last Run

2026-07-14_152156_normal_run

## Current Status

008E is complete. The exact §26.7 signature-capture and §26.8 mismatch-resolution POST routes now
retain one current signature per legal document/signer identity with bounded database facts,
protected links, immutable name history, exact replay, action-specific Compliance/Company Secretary
authority, and attributable audit/version/workflow evidence. Resolved rows cannot be reopened by a
later capture replay or changed capture.

Verified unresolved mismatches publish through the application-owned fact seam and atomically make
only the Bank Verification Letter applicable. Resolution with a same-application current-renderer
bank-letter file or adequately stamped borrower declaration clears that applicability without
changing checklist completion, verifier/time/remarks, approval signatures, status, file authority,
or readiness. Completed-evidence reversals conflict and roll back the owner mutation and ledgers.
A-107 records the conservative evidence-file interpretation until a signed-copy/bank-attestation
aggregate is governed.

## Validation

Evidence is in `.ralph/runs/2026-07-14_152156_normal_run/evidence/`. Focused RED/GREEN logs and API
examples are saved. Django check and migration sync pass; all 773 backend tests pass with 24 expected
PostgreSQL-only skips and 93% coverage against the 85% floor. Frontend build, typecheck, lint, and all
293 tests pass. Final Standards/Spec review found and fixed resolved-history reopening and ordinary-
signature cancellation of active mismatch truth; the re-review has no open findings.

## Next Run

Run the now-due architecture review, then 008F. 008F now consumes distinct borrower/nominee signed
rows without treating mismatch resolution as PoA execution. 008G has been sharpened from its stub to
the source-defined conditional tri-party verification path without inventing a subsidiary identity
aggregate or repayment authority. A-101 still blocks the real M05-to-full-Term-Sheet path.
