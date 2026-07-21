# Review Packet: 2026-07-22_031437_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Review Boundary

- Fixed point: `fff95e9d49f7541a8c74f8677b47de8db966964e`
- Product commits: `d95dfd34` (010N2), `04597c23` (010N3), `71fd80df` (010N4)
- Diff: `git diff fff95e9d...71fd80df`
- Later `fix(ralph)` commits were orchestration-policy changes and were not treated as product
  findings. The review was limited to the new product diff and the five active Epic 010 roots named
  by the run contract.

## Convergence Metrics

- Findings closed: 0
- New Critical: 0
- New High: 0
- New Medium: 0
- New Low: 0
- Corrective slices added: 3

All reproduced issues retain existing stable identities and are therefore Carried, not New. Because
corrective additions exceed closures across the two latest reviews, the recommendation is to stop
symptom-level patching: 010N5, 010N6, and 010N7 each deepen one existing owner boundary, with 010N5
preserving the single grouped terminal episode rather than creating another leaf or generation.

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | High | Carried | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/terminal-mis-carried.log | 010N5 | - |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | High | Carried | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/terminal-reminder-carried.log | 010N5 | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | High | Carried | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/servicing-composite-owner.log | 010N5 | - |
| AR-010-INTEREST-UI-001 | ROOT-010-INTEREST-PORTFOLIO-COMPLETENESS | High | Carried | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/interest-portfolio-identity.log | 010N6 | - |
| AR-010-SEARCH-001 | ROOT-010-GLOBAL-SEARCH-SENSITIVE-AUTHORITY | High | Carried | .ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/global-search-owner-scope.log | 010N7 | - |

## Standards

- High: the new capture-only compatibility path in `servicingApi.ts` performs SAP-posting and
  allocation mutations in React, violating the sole backend composite owner in API_CONTRACTS and
  codebase-design §§17/42.
- High: the security search facade discards actor and bypasses the canonical Stage-4/object-scope
  owner. Prefix-only routing also excludes otherwise valid SAP/CDSL identifiers.
- Medium: permanent tests cover happy composite responses and generic pagination helpers but not
  the new compatibility branch, cross-page identity stability, or out-of-scope security records.
- Low: the aggregate retains a cross-domain model alias only as a historical probe patch target.

## Spec

- High: CR-015 requirement 3 and 010N2 requirements 3/5 require one backend-owned direct-repayment
  command; the new fallback restores the forbidden browser-owned sequence.
- High: 010N3 AC-E10-I1/I2 promise that loan 101 cannot be silently omitted, but two stable-looking
  pages containing 101 rows/100 identities are accepted and accrued as complete.
- High: 010N4 requirements 1/2 require canonical sensitive-input permission and object scope before
  disclosure; a real out-of-Stage-4 cheque record still resolves its member.
- Medium: production `available_actions` remains an alias of permissions rather than a resource
  action projection.
- Medium: the SAP/CDSL test matrix covers only invented prefixes, not arbitrary valid owner values.

Summary: Standards found 4 issues (worst High: financial/security owner bypasses); Spec found 5
issues (worst High: the three binding closure contracts remain partial).

## Terminal Repair Verification

The MIS `generated_at` lifecycle tests and reminder repayment/provider probe are individually green.
The active episode cannot close because the servicing client-side mutation probe fails. Per the
grouped terminal contract, 010N5 retains all three inherited Finding ID/Root ID pairs with the same
`Architecture Review Recurrence Repair` declaration. This is still episode 1/attempt 1, not a new
corrective generation, second finalizer, or quarantine.

## Traceability

- The source contract says the composite endpoint is the staff UI's sole direct-repayment mutation;
  the code accepts a partial capture and calls two substep endpoints, verified by the failing Vitest
  probe in `servicing-composite-owner.log`.
- 010N3 says a 101st loan can never be silently omitted; the code validates counts but not unique
  identities, verified by two failing page/batch probes in `interest-portfolio-identity.log`.
- S02 and the security contracts say sensitive matches require canonical permission and object
  scope; the code queries instrument tables without the canonical Stage-4 owner, verified by the
  real-record Django probe in `global-search-owner-scope.log`.

## Repository Truth and Queue

- `docs/working/CONTEXT.md` remains accurate: Epic 010 is active and now has three root-boundary
  corrections before later work consumes servicing/search truth.
- `.ralph/state.json` lists no Blocked slices, so no stale prerequisite required re-parking.
- M10-FR-003–010 retain implemented owners, but terminal servicing, complete interest membership,
  and sensitive search remain conditional on 010N5–010N7.
- No ADR was added: the corrections enforce existing owner, pagination, and security decisions.
- All three new slice runtime declarations validate; 010N5's exact five-test PostgreSQL contract
  validates; the complete slice queue lint passes.

## Recommended Next Action
Run independent architecture-review validation, then execute 010N5, 010N6, and 010N7 in dependency
order before continuing later product work.
