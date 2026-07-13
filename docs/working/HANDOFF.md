# Ralph Handoff

## Last Run
2026-07-13_225742_normal_run

## Current Status

007H3 is complete. Approval-case validity now checks the internally complete frozen loan-limit
provenance only; it never compares an existing cycle with the mutable live appraisal snapshot or
assessment-id field. Credit-owned enrichment remains the single point that validates the locked
appraisal/source before the approval owner freezes provenance and review facts.

The explicit coherence/reader projection now narrows database candidates only. Every candidate
crosses the same frozen-validity and actor-scope decision before case/register filters, counts,
page normalization, or serialization. Pending detail/queue/actions and terminal
detail/decision/register reads remain unchanged after a live appraisal policy edit. A malformed
frozen terminal case with a stale true flag/index fails closed at all four boundaries with zero
count leakage or action writes. Returned cycle 1 retains its original provenance/review facts while
corrected cycle 2 carries its independently frozen facts.

No signal, cross-table model-save side effect, schema change, dependency, or frontend production
change was introduced. 007I and 007J were sharpened with exact old/new-cycle and pre-count
nondisclosure container regressions. The prior CR-004 hosted-CI evidence caveat remains an
owner/orchestrator promotion check; it is unrelated to this slice.

## Validation

Retained RED/GREEN public probes and all 106 approval-routing tests pass. Frontend
build/typecheck/lint and all 208 tests pass. Backend check/migration sync and all 679 tests pass with
19 expected PostgreSQL-only SQLite skips; coverage is 93% against the 85% floor. Queue/state/path
checks and final Ralph artifact validation remain for the orchestrator.

## Next Run

Run `007I-sanction-workbench-ui`, consuming only the server-frozen cycle projection and the exact
pre-count scope semantics documented by 007H3. Then run 007J for register/configuration wiring.
