# Ralph Handoff

## Last Run

2026-07-14_064206_architecture_review

## Current Status

Architecture review of completed 007O-007Q and 008A is complete with no production-code change.
Newly created terminal decisions/registers use frozen facts, S21 has authoritative pagination, the
S23/S25 fields and screenshots are reviewable, and 008A retains immutable template successors with
metadata-only responses and a passing PostgreSQL exact-successor race.

The review found older v2 approval packages lose readability after 007O's unversioned schema
expansion and older register rows can raise instead of returning legacy nulls. Formal approver names
also remain live until terminal generation. Corrective 007R owns history/remediation/frozen identity.
007S owns final-page validation, stale S21 responses, valid UI fixtures, shared screenshot analysis,
and restoration of an approved register table/detail pattern. 008A2 owns first-version overlap
races, provenance-aware template-file references, selector/transport locality, and explicit
borrower-template variant resolution. 008B now depends on 008A2.

## Validation

Review/gate evidence is in `.ralph/runs/2026-07-14_064206_architecture_review/evidence/`. Frontend
build, typecheck, lint, and all 269 tests pass. Django check/migration sync and all 700 backend tests
pass with 20 expected PostgreSQL-only skips at 93% coverage. Queue lint, state JSON, diff checks, and
the three reviewed 007Q screenshots pass inspection. This descriptor declares no browser/PostgreSQL
runtime; retained independent evidence was reviewed rather than fabricated or rerun.

## Next Run

Run 007R, then 007S; run 008A2 before sharpened 008B. 008B must consume 008A2's race-safe effective
selection, provenance-aware file reference, and explicit borrower-template variant resolver; it
must not guess FPC/FPO equivalence or treat template/file metadata as generation/download authority.
008C and 008D remain concretely sharpened. A-095/A-097/A-098 own the active-vs-approved, borrower-
variant, and change-rationale source questions.
