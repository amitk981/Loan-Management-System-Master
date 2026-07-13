# Slice 007H: Credit Sanction Register

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Generate the Credit Sanction Register entry on every sanction decision and expose the sanction-decision and register read APIs (M05-FR-009).

## User Value
The committee, CS, and auditors read a complete, generated register of every sanction outcome with the authority, approvers, exception, and general-meeting references the source requires.

## Depends On
- 007G

## Source References
- docs/source/data-model.md §15.6 `credit_sanction_register_entries`
- docs/source/api-contracts.md §25.8 (sanction decision read), §25.9 (`GET /api/v1/credit-sanction-register/?financial_year=&decision=`)
- docs/source/functional-spec.md M05-FR-009 and the 15 Credit Sanction Register fields (application number, borrower name/type, requested/eligible/recommended/sanctioned amounts, authority, approver names, date, decision, reasons, exception reference, conflict/abstention details, general-meeting reference)
- docs/source/auth-permissions.md §12.6 (`approvals.sanction_register.read`, `approvals.sanction.read`)
- docs/working/maps/Appraisal and Sanction Map.md (Annexure K open decision — register template code)

## Prototype Reference
- sfpcl-lms/src/pages/registers/RegistersHub.tsx (S23 view; wiring is 007J)

## Concrete Requirements
1. Create the §15.6 register entry inside the 007D/007G completion transaction for both sanctioned and rejected decisions; entries are immutable generated rows — no create/update API.
2. The register read response projects all 15 functional-spec fields; amounts come from the application/eligibility/appraisal/decision records, authority and approver names from the case snapshot and actions, exception reference from 007F, conflict/abstention details from 007E data, and general-meeting reference from 007G. List every projection source in API_CONTRACTS.md.
3. `GET /api/v1/credit-sanction-register/` per §25.9 with financial_year and decision filters, standard pagination, `approvals.sanction_register.read`; financial-year derivation is April-March — record as an assumption if the source is silent.
4. `GET /api/v1/loan-applications/{id}/sanction-decision/` per §25.8 with `approvals.sanction.read`; 404 while no decision exists.
5. Annexure K: the register template code remains unresolved in the Open Decisions Index — implement fields per functional-spec, record the Annexure K linkage as a blocked/deferred decision, and do not invent a template code.
6. Audit event for register-entry creation; workflow event references preserved.

## Test Cases
- Sanctioned and rejected completions both generate exactly one immutable entry; no duplicate on retried completion.
- Register projection matches the 15 fields against a seeded exception + related-party + abstention case.
- Filters/pagination/permission negatives on both read APIs; mutation attempts have no route.

## Run-Ahead Sharpening Review (007G delivered contract, 2026-07-13)

- The register's general-meeting reference comes only from the terminal case's frozen nullable
  `general_meeting_approval`; never select the latest record by application, because evidence may
  be superseded after a returned or completed cycle.
- Project the meeting id, outcome, meeting date, related-party type/user, and the three document
  metadata ids from that frozen row. Do not grant document access through register read permission;
  downloads keep the document module's own permission/sensitivity boundary.
- A missing/pending/rejected gate produces no final approve action and no sanction decision, so it
  cannot generate a sanctioned register row. Conflict-blocked and returned cycles remain outside
  terminal register generation; their case-frozen meeting references stay historical only.

## Run-Ahead Sharpening Review (007F delivered contract, 2026-07-13)

- Resolve an exception reference only through the final case's one-to-one
  `ExceptionRegisterEntry`; never select by application alone because returned/re-enriched cycles
  may retain multiple immutable historical rows.
- Project exception id, type, business reason, status, and cycle from 007F. Authority still comes
  from that same case's canonical route/effective/action history, never from register summary text
  or live committee membership.
- A rejected exception case has a rejected exception row but no `SanctionDecision`; use terminal
  case/action facts without inventing a sanction id. Pending returned/conflict-blocked exception
  rows are not terminal sanction-register decisions.

## Out of Scope
Register UI (007J), file exports (012B/012C), exception register (007F owns), disbursement handoff (Epic 009).

## Risk Level
Medium

## Acceptance Criteria
- Every decision is registered, immutable, complete across the 15 fields, and readable only by permitted roles.
- All gates pass; API examples saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
