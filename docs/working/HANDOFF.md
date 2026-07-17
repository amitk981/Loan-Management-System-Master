# Ralph Handoff

## Last Run
2026-07-17_122058_repair

## Current Status
009E3's independent coverage failure is repaired pending full orchestrator revalidation. The
failure was test-only: a module-level specialized `TestCase` subclass caused Django to collect 13
inherited checklist tests against fixture overrides intended only for the final-documentation
setup. The helper now uses a non-test override mixin and constructs the concrete subclass inside a
factory. The module collects 57 intended tests instead of 70 and passes twice; the original 13
checklist tests and the 009E3 initiation/authorisation suites also pass. No production code changed
in the repair.

The retained 009E3 behavior remains complete. Payment initiation accepts positive
18,2 lesser amounts within immutable terms/sanction and freezes the exact amount through CFC review.
Initiation now reconciles and retains the public loan owner's creation history/audit/workflow ids;
the genuine documentation/SAP/readiness/bank fixture no longer inserts raw loan rows.

Source-bank activation is backed by a canonical unassigned Critical permission and database-required
activation proof. Replacement retains the original proof, appends predecessor/deactivation version
and audit facts, closes the effective range, and resolves only one complete coherent history. Twice-
run PostgreSQL five-caller first/replacement races retain one winner and no orphan evidence. The
normal run's focused backend, PostgreSQL, Django/migration, changed-scope Ruff, and frontend gates
remain green; the repair's focused regression and Django/migration checks are green.

## Next Run
Run 009F2 to restore current borrower/source-bank evidence, complete aggregate constraints,
scope/action parity, the full CFC role matrix, and reconciliation of 009E3's frozen loan-owner ids.
Then run 009G, which depends on 009F2 and must consume that exact typed current-evidence decision
before UTR, funding, and activation.
