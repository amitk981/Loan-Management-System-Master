# Slice 012A3: Default, Compliance, and Audit Report Catalogue

## Status
Not Started

## Runtime Capabilities
- `none`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 found the remaining R8 report catalogue had no
executable owner after the six 012A foundation endpoints.

## Goal
Complete the source-required report catalogue for default, recovery, closure, statutory compliance,
grievances, and restricted audit-log export handoff.

## User Value
Compliance, CS, CFO, and Internal Auditor can review every mandatory release report through scoped,
reconciled report definitions before UAT signoff.

## Depends On
- 012A2

## Source References
- `docs/source/implementation-roadmap.md` section 17.3 and R8-AC-001
- `docs/source/functional-spec.md` M14-FR-013
- `docs/source/screen-spec.md` S62-S69 and S74
- `docs/source/api-contracts.md` sections 37, 38, 40, and 42
- `docs/source/auth-permissions.md` compliance/report/audit permissions
- `docs/source/security-privacy.md` restricted audit and sensitive export controls
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md`

## Prototype Reference
- `sfpcl-lms/src/pages/reports/ReportsMIS.tsx`
- `sfpcl-lms/src/pages/registers/RegistersHub.tsx`

## Screens Involved
None in this slice; 012DA owns frontend wiring.

## Frontend Scope
None.

## Backend/API Scope
- Register source-backed selectors/codes for Default, Recovery, Closure/NOC, Section 186, NBFC Test,
  KYC/Re-KYC, Stamp Duty, Money-Lending Review, and Grievance reports.
- Register Audit Log Export only as a restricted handoff to the 012C policy and 012D selector; do not
  create a bypassing query or download route.
- Reuse owning Epic 008/011/012 selectors, preserve as-of/filter semantics, and provide deterministic
  pagination/totals where source-backed.
- Keep export files/jobs in 012B/012C and frontend wiring in 012DA.

## Database/Model Impact
None expected. Index only from measured query-plan evidence through a non-destructive migration.

## API Contracts
Complete the section-40 registry in `docs/working/API_CONTRACTS.md` and document the restricted audit
export handoff, exact permissions, fields, filters, totals, and source-owner reconciliation.

## Permissions
Require each owning compliance/register permission plus object scope. Audit-log export additionally
requires the restricted audit read and sensitive export policy; no broad management fallback.

## Audit Requirements
Routine reads avoid recursive row-level events. Restricted export request/download remains audited by
012C without copying report rows or sensitive filters into audit payloads.

## Validation Rules
- Every report reconciles with canonical source-owner records for identical filters and as-of time.
- Restricted recovery/audit/KYC fields are omitted or masked by default.
- Unsupported filters, unauthorised scope, and unresolved permission mappings fail closed.

## Test Cases
- RED then GREEN for each code: seeded reconciliation, filters, stable order, pagination, totals,
  empty, invalid, 401/403, masking, and cross-scope denial.
- Audit export cannot bypass 012C policy or expose unsanitised 012D values.
- Reverse-consumer tests keep compliance/default/recovery/closure/grievance owners unchanged.

## Visual Acceptance Criteria
Not applicable (backend only).

## Evidence Required
Saved RED/GREEN output; complete matrix for all 23 product-requirement reports plus the two fixed
additional section-40 APIs; code-to-permission/source mapping;
reconciliation, masking and denial examples; audit-export handoff proof; full gates.

## Risk Level
High

## Acceptance Criteria
- The complete 23-report section-17.3/product-requirements catalogue has one registered,
  permission-correct, reconciled owner without aliases hiding a missing report.
- Audit-log export remains restricted and cannot bypass export or sanitisation policy.
- R8-AC-001 is technically satisfiable before 012B/012DA and final UAT review.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Remaining report codes/selectors/contracts implemented
- [ ] Reconciliation, scope, masking, and audit handoff tested
- [ ] Full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
