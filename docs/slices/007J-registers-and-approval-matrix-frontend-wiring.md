# Slice 007J: Sanction/Exception Registers and Approval Matrix Settings UI Wiring

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Wire the register and configuration surfaces of Epic 007: Credit Sanction Register (S23), Exception Register (S25) in RegistersHub, and the Approval Matrix settings panel (S71) in SettingsHub, so sanction outcomes and approval rules are visible from real data.

## User Value
The Sanction Committee, CS, and auditors read real registers generated from approval events, and admins see the actual approval matrix (up to ₹5,00,000: CFO + one Director; above: CFO + two Directors) that routing uses.

## Depends On
- 007I

## Source References
- docs/source/screen-spec.md screens S23 (Credit Sanction Register), S25 (Exception Register), S71 (Approval Matrix Settings); section 4.3 (registers are generated views)
- docs/source/api-contracts.md section 25 (approval and sanction APIs)
- docs/source/functional-spec.md BR-026/BR-027 (thresholds), exception rules
- docs/source/auth-permissions.md section 16 (approval authority)

## Prototype Reference
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/settings/SettingsHub.tsx (approval matrix panel)
- sfpcl-lms/src/pages/borrower/portal/applications/MP12_SanctionOutcome.tsx

## Concrete Requirements
1. Wire the sanction and exception register views in `RegistersHub.tsx` to the 007H register APIs with pagination/filtering per api-contracts §8; registers stay read-only generated views — no manual row editing.
2. Wire the approval matrix panel in `SettingsHub.tsx` to the 007A configuration API: display current versioned rules; edits only for permitted admin roles, creating a new config version (003E pattern), never overwriting silently.
3. Export actions appear only for roles with register-export permission; actual export jobs arrive in 012B — show the permitted action state, keep the button wired to whatever exists, and record the interim behaviour in API_CONTRACTS.md.
4. Wire the member portal Sanction Outcome view (spec MP12, `MP12_SanctionOutcome.tsx`) to the sanction decision API: borrower sees own outcome, sanctioned amount, and borrower-facing terms only — no internal approval history.
5. Loading, empty, error, unauthorized states throughout; reuse existing table/queue patterns only.

## Owned Mock Removals
- `src/pages/registers/RegistersHub.tsx` — the S23 (Credit Sanction Register) and S25 (Exception Register) views must run with no mock reads after this slice; the file's remaining register views and final `mockData` import removal are owned by 012DA.
- `src/pages/settings/SettingsHub.tsx` — approval matrix panel only; the remaining panels are owned by 007J2.

## Test Cases
- Register rows match seeded approval/sanction fixtures (generated, not hand-entered).
- Non-permitted role sees no matrix edit action and receives 403 on direct API call.
- Matrix edit creates a new version with audit event.

## Run-Ahead Sharpening Review (007H delivered contract, 2026-07-13)

- S23 consumes only `GET /api/v1/credit-sanction-register/` with canonical
  `FYyyyy-yy`, `sanctioned|rejected`, `page`, and `page_size` query values. Render the server's 15
  frozen fields and pagination unchanged; do not derive money, authority, names, or references
  from live application/case/configuration data.
- Render `exception_reference`, `conflict_abstention_details`, and
  `general_meeting_approval_reference` as nullable/nested frozen register facts. Meeting document
  ids are metadata only: register visibility must not create a download affordance unless the
  existing document resource separately grants it. Annexure K/template code stays absent under
  OC-002/A-087.
- S25 continues to consume the 007F `/exception-register/` contract; do not conflate its
  status/type filters or case-object scope with the global 007H sanction-register filter contract.
- The §25.8 internal sanction-decision endpoint requires `approvals.sanction.read` and returns 404
  for rejected outcomes. Before wiring borrower MP12, inspect its cited portal ownership contract;
  do not grant borrowers the internal approval permission or widen the 007H endpoint merely to
  satisfy the screen. Preserve rejected outcome copy from the borrower-authorised source the MP12
  contract names.

## Run-Ahead Sharpening Review (Architecture Review 2026-07-13_200023, 2026-07-13)

- Consume 007H2's already scoped register pages exactly. Never infer global register visibility
  from the presence of `approvals.sanction_register.read`, merge pages from another case endpoint,
  or display a client-computed total; the server count is object-scoped before pagination.
- A Director's register can contain only attributable original/effective/acted cycles, while
  persisted legal/audit/management readers retain their backend-defined read-only scope. Empty and
  filtered states must not reveal that out-of-scope rows exist.

## Run-Ahead Sharpening Review (007H2 delivered contract, 2026-07-13)

- Render the server pagination object verbatim after every filter change. `total_count`,
  `total_pages`, normalized `page`, empty results, and next/previous state are already computed
  inside the caller's canonical case scope; never preserve or merge a total from an earlier actor,
  filter, or page.
- Director rows include only original/effective/conflicted/acted attributable cycles. A persisted
  legal/audit/management scope is usable only with the separate register permission, and neither
  kind of visibility enables case actions, sanction-decision reads, document references, or
  downloads.
- Keep `reasons` and `exception_reference.business_reason` as distinct frozen values. Do not
  substitute one for the other or derive either from live application, case, or exception data.

## Out of Scope
Register file exports (012B/012C), sanction case actions (007D/007I), stamp duty register (008D/011 compliance views).

## Risk Level
Medium

## Acceptance Criteria
- S23/S25/S71 run on backend data with role-correct actions.
- All gates pass; screenshots of registers and matrix settings saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
