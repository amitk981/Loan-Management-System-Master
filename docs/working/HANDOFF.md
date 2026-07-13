# Ralph Handoff

## Last Run
2026-07-13_174603_normal_run

## Current Status

007F adds the generated, case/cycle-specific Exception Register. Assessment-required limit
exceptions use `exceeds_loan_limit`; forced within-limit callers must state `stage_bypass` or
`waiver`, preventing false limit-breach records. Enrichment requires a distinct business reason,
optional risk assessment, and the Critical system-generation permission, and creates exactly one
pending entry with audit/workflow evidence.

Approval/rejection projects the entry outcome and closure inside the locked action transaction.
Return and conflict-blocked cycles copy closure time but remain pending because source §15.7 names
no fourth status. Exact replay compares type/reason/risk and creates no duplicate. Denied conflict
writes leave the entry unchanged.

The read-only Exception Register filters by status/type with standard pagination and delegates to
the canonical original/effective/acted approval-case selector before count. Rows expose exact
cycle linkage, conflict facts, authority summary, route/effective replacement projection, and all
immutable actions without consulting live committee membership.

## Validation

Retained RED/GREEN logs cover entry creation/replay, status projection, generated-view
permission/scope/filtering, distinct exception validation, and seeded permissions. Independent
review found and repaired forced-route misclassification, risk replay, return/conflict closure,
and a historical migration dependency interaction.

Frontend build/typecheck/lint and all 208 tests pass. Backend check and migration sync pass; the
full 656-test suite passes with 19 expected PostgreSQL-only SQLite skips and 93% coverage.

## Next Run

Run `007G-general-meeting-evidence-for-special-cases` next. It is sharpened to preserve 007F's
case/cycle entry identity and locked status projection. Then run 007H in dependency order.
