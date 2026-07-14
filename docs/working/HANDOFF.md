# Ralph Handoff

## Last Run

2026-07-14_051852_normal_run

## Current Status

Slice 007Q is complete. S23 and S25 now expose their missing source-required facts from immutable
register snapshots, including a formal sanction-register entry number, borrower/loan/purpose/risk,
per-approver comments and timestamps, frozen terminal rejection/condition facts, communication
metadata, and exception borrower/impact/requester/date facts. Later live owner mutations do not
rewrite either projection. Both screens retain the established semantic table composition with
four grouped columns, strict shared pagination, metadata-only documents, and no inferred download.

## Validation

Evidence is in `.ralph/runs/2026-07-14_051852_normal_run/evidence/`. Django check/migration sync and
all 693 backend tests pass with 19 expected PostgreSQL-only skips at 93% coverage. Frontend
build/typecheck/lint and all 269 tests pass. Both trusted specs collect. Local Chromium hit the
expected macOS Mach-port denial before test execution; independent validation owns both declared
browser runs and the three final screenshot verdicts.

## Next Run

Complete independent full validation and both trusted browser runs for 007Q, then start sharpened
008A followed by 008B. Their metadata/action boundary is explicit: stored template/generated
document metadata never grants file download; only canonical enabled actions may do so. A-095 still
owns the unresolved S72 active-versus-approved question.
