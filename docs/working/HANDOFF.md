# Ralph Handoff

## Last Run
2026-07-13_143342_normal_run

## Current Status

007D2 is complete. Approval-case collection, detail, and action responses now share one history-
aware projection, and detail/POST consume one canonical action-availability decision. Ordinary
stale, acted, excluded, closed, contradictory, unassigned, read-only, and permission denials retain
stable contracts and exact zero-write ledgers.

The action transaction retains application -> appraisal -> case locking and evaluates all owner
states through the shared transition guard before mutation. Terminal outcomes cross the
communication-owned internal adapter to persist one pending Communication, one linked Credit
Assessment notification, and one metadata-only audit; adapter failure rolls the outcome back.
Both authoritative PostgreSQL races passed twice with one serial winner and stable stale loser.

## Validation

Evidence is under `.ralph/runs/2026-07-13_143342_normal_run/`. Retained RED/GREEN logs cover
projection parity, owner transition guards, communication persistence, adapter rollback, and the
full denial matrix. Two separate PostgreSQL logs each run both action races successfully. Frontend
build/typecheck/lint and 208 tests pass. Backend check/migration sync and 621 tests pass with 18
expected PostgreSQL-only skips in SQLite and 93% coverage.

## Next Run

Run `007D3-returned-approval-cycle-and-resubmission-closure`. Then 007E can add conflict exclusions
and abstentions on the history-aware, communication-backed, multi-cycle action boundary.
