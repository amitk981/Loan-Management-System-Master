# Slice 010N5: Terminal Servicing Recurrence Owner Closure

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Depends On
- 010N4

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Architecture Review Recurrence Repair
- Epic: 010
- Root ID: ROOT-010-REMINDER-DELIVERY-OWNER
- Terminal finalizer: CR-015-epic-010-terminal-servicing-owner-finalizer
- Repair attempt: 1

## Goal
Finish the current CR-015 repair episode through one truthful server-owned servicing boundary: the
staff client accepts only the complete composite repayment result, while every inherited MIS,
reminder, and servicing finding remains bound to the terminal contract until independent review.

## Review Finding Closure
| Finding ID | Root ID | Reproducer | Acceptance IDs |
|---|---|---|---|
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/terminal-mis-carried.log | AC-E10-RR1 |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/terminal-reminder-carried.log | AC-E10-RR2 |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/servicing-composite-owner.log | AC-E10-RR3, AC-E10-RR4 |

## Source References
- `docs/slices/CR-015-epic-010-terminal-servicing-owner-finalizer.md` requirements 1–5
- `docs/slices/010N2-epic-010-terminal-servicing-recurrence-repair.md` requirements 1–5
- `docs/working/API_CONTRACTS.md` “Epic 010 terminal servicing owner contracts”
- `docs/source/codebase-design.md` §§17.3, 26, 38, and 42

## Concrete Requirements
1. Remove the capture-only compatibility branch from the staff client. The browser invokes only
   `direct-repayment-command`; a response without exact `{replayed,capture,allocation}` truth fails
   visibly as malformed and must not call SAP-posting or allocation endpoints.
2. Keep capture, retained SAP posting, principal-first allocation, exact replay, changed-payload
   conflict, and complete response inside the backend composite transaction. Convert the current
   review probe into a permanent service regression asserting one request and zero client-owned
   financial substeps for complete, replayed, malformed, and failure responses.
3. Retain the corrected `generated_at` MIS lifecycle and five reminder provider cases. Replay every
   current reproducer and the exact five-test PostgreSQL class without weakening its expected count.
4. Bind each acceptance row to substantive permanent tests and current-run RED/GREEN evidence. The
   grouped episode remains open until a later independent review closes all three inherited pairs.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer.Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests`
- Expected tests: 5

## Acceptance Criteria
- [AC-E10-RR1] Real-model before/on/after invoice lifecycle and exact historical replay remain
  cutoff coherent through the public MIS owner.
- [AC-E10-RR2] The five reminder repayment/source/worker/retry/timeout cases retain at most one
  justified provider effect in two PostgreSQL runs.
- [AC-E10-RR3] Capture-only or malformed composite responses fail visibly after exactly one request;
  the client never invokes SAP-posting or allocation substeps and never supplies allocation policy.
- [AC-E10-RR4] Complete, replay, changed-payload, crash-boundary, and concurrent composite-command
  tests retain one backend transaction and one complete response, with all grouped reproducers green.

## Risk Level
High
