# Ralph Handoff

## Last Run

2026-07-16_052448_repair

## Current Status

009A is complete pending Ralph's independent validation and commit. It adds the Finance-owned
manual SAP customer-profile request boundary after exact terminal sanction, freezes canonical
borrower/sanction/current verified-bank facts, retains an authenticated-encrypted restricted
Annexure-I workbook, and creates one replay-safe request with atomic audit/workflow evidence.

The run began as a repair because `2026-07-16_052447_normal_run` stopped at preflight with
`No slice files found`; it had no worktree or implementation to salvage. Independent Standards and
Spec reviewers found and then reverified closure of physical workbook encryption, active-code
replay, persisted-actor locking, verified-bank coverage, canonical workflow recording, and Ralph
evidence/bookkeeping issues.

## Validation

Evidence is in `.ralph/runs/2026-07-16_052448_repair/evidence/`. Focused 009A has 13 green tests
(one PostgreSQL-only skip under SQLite). The PostgreSQL five-caller race ran twice after the final
changes and passed both times; each test contains two race rounds. The final backend suite passes
928 tests with 49 skips at 91% coverage; Django check and migration drift are clean. Unchanged
frontend gates pass build, typecheck, lint, and all 319 tests. RED/GREEN logs include the initial
route tracer, migration-graph regression, and review-discovered security/authority defects.

## Important Continuation Notes

- 009B must decrypt retained workbooks only through
  `finance.modules.annexure_storage.EncryptedAnnexureStorage` before governed send/download.
- Historical one-way `enc:v1` member identity values remain ineligible for full Annexure export;
  see A-120. The fixed single-sheet renderer decision and replacement seam are in A-123.
- 009B is already concrete. 009C was sharpened in this run from already-opened Epic 009 sources;
  A-121 forbids inventing a default role grant for its Critical create permission, and A-122 records
  its conservative pre-disbursement zero-balance default.

## Next Run

Run 009B-sap-request-send-and-code-confirmation, then 009C-loan-account-creation-from-sanctioned-application.
