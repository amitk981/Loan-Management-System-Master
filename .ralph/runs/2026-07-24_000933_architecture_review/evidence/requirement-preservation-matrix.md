# 011P Requirement Preservation Matrix

| Original 011P contract | Successor preservation |
|---|---|
| S53 default detail, S54 grace/extension, S55 non-payment note | 011PA requirements 1-3 |
| S56 recovery decision with frozen note, authority/conflict evidence, permitted decision, reason, terminal outcome, and exact blockers | 011PB requirements 1-4 |
| S57 unavailable without an approved executable decision; browser cannot supply approval/authority truth | 011PA requirement 4 and 011PB requirements 3-4 |
| S58-S61 closure readiness, NOC, security return/unpledge, and archive state | 011PC requirements 1-3 |
| S62-S67 controls, Section 186, NBFC, KYC/re-KYC, money-lending, stamp duty, and role-correct review | 011PD requirements 1-5 |
| S68 grievance list/resolve with status and reason | 011PE requirement 1 |
| Audit Archive Hub read-only with audited downloads | 011PE requirement 2 |
| Loading, empty, error, unauthorized, blocked/validation, and success states; existing patterns only | 011PA requirement 5; 011PB requirement 5; 011PC requirement 4; 011PD requirement 6; 011PE requirement 3 |
| Shared frontend request/action/render coverage | Scoped shared API seam and focused tests in every successor |
| Remove mocks and inline business fixtures from all five original page owners | 011PA partial Default owner; 011PB final Default owner; 011PC Closure owner; 011PD Compliance owner; 011PE Grievance and Audit Archive owners plus terminal five-owner check |
| Closure blocker/NOC test | 011PC Test Cases |
| Recovery execution and S56 approval-evidence tests | 011PB Test Cases |
| Compliance seeded values and auditor read-only test | 011PD Test Cases |
| Grievance missing-reason rejection test | 011PE Test Cases |
| RED/GREEN output for every owner | Scoped Evidence Required section in 011PA-011PE |
| Role/action/blocker and mock-removal matrices | Scoped rows in 011PA-011PD; completed matrices in terminal 011PE |
| Five named screenshots from two passing contract runs | Individual ownership in 011PA-011PE; all five repeated in 011PE terminal combined acceptance |
| Focused Epic 011 reverse-consumer and configured full gates | Required by every successor |
| Medium risk | `## Risk Level` is Medium in every successor |
| Original prerequisite 011O | Inherited by first successor 011PA |
| Every downstream dependency on 011P | Sole baseline edge in 012G redirected to terminal 011PE |

## Source and Prototype Coverage

- Screen specification coverage remains S53-S68 across 011PA-011PE, including sections 9.9 and
  9.10 in the owning successors.
- API sections 35-38 remain covered across the five successors.
- Default, recovery, closure, compliance, and grievance functional rules remain cited by their
  owning successors; default and closure user flows remain cited.
- The shared Epic 011 digest §011P remains cited by every successor.
- All five original prototype owners remain cited: `DefaultRecoveryHub.tsx`,
  `LoanClosureHub.tsx`, `ComplianceDashboard.tsx`, `GrievancesHub.tsx`, and
  `AuditArchiveHub.tsx`.

## Scope Guard

The rewrite changes queue documents and current-run evidence only. It does not implement product
code, inspect unrelated slice specifications, modify the Epic 011 digest, or alter source material.
