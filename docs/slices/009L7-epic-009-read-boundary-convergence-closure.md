# Slice 009L7: Epic 009 Read-Boundary Convergence Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Converge Epic 009 on one executable read boundary: restore the binding Loan Account permission and
object scope, eliminate every remaining count/projector disagreement, and make the retained browser
fixture consume public owner interfaces without breaking the advertised full Playwright suite.

## Depends On
- 009L6
- CR-012

## Runtime Capabilities

- `postgresql-five-race-acceptance`
- `localhost-e2e-server`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_epic009_read_boundary_postgresql.Epic009ReadBoundaryPostgreSQLAcceptanceTests`
- Expected tests: 6

## Trusted Browser Acceptance

- Spec: `e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`
- Screenshot: `loan-account-list.png`
- Screenshot: `loan-account-sanctioned-summary.png`
- Screenshot: `loan-account-active-summary.png`
- Screenshot: `sap-request-and-confirmation.png`
- Screenshot: `disbursement-readiness-blockers.png`
- Screenshot: `payment-initiation.png`
- Screenshot: `cfc-authorisation.png`
- Screenshot: `transfer-and-advice-success.png`
- Screenshot: `loan-account-safe-error.png`

## Source / Review References

- `docs/source/functional-spec.md` M07-FR-001 through M07-FR-010 and M08-FR-001 through M08-FR-011
- `docs/source/screen-spec.md` S36 through S42
- `docs/source/api-contracts.md` §§29-31 and 45
- `docs/source/auth-permissions.md` §§19.3 and 34.7
- `docs/source/codebase-design.md` §§16, 26, and 42
- `docs/working/API_CONTRACTS.md` Loan Account 360 and staff-disbursement-workspace contracts
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-19_180917_architecture_review`
- `.ralph/runs/2026-07-19_180917_architecture_review/evidence/review-probes/test_009l6_closure_probes.py`

## Concrete Requirements

1. Restore the public Loan Account list/detail contract: every caller requires the active source
   role, `finance.loan_account.read`, and its exact object scope. Disbursement-initiation permission
   is not a substitute and must not grant portfolio scope. Give the staff workspace a distinct
   owner interface for its initiation candidates so internal composition cannot weaken public
   authorization or list/detail parity.
2. Replace the remaining SQL-subset-plus-scalar-drop pattern with one public owner decision for
   each Loan Account, S36, S37, combined Senior Finance, and CFC collection. Count, page boundaries,
   rows, actions, detail reads, and mutations must consume that same decision; a selected identity
   may never disappear during projection.
3. Make the owner decision cover every scalar fact, including SAP send and completion audit actors,
   exact action bodies and relations, communication/task/action URL, Annexure-I bytes and digest,
   assignment and code identity, readiness, bank/source/account owners, initiation, workflow,
   aggregate, transfer, and file integrity. If a fact cannot be queried directly, materialize an
   immutable owner-maintained eligibility fact rather than copying a partial predicate or scanning
   the portfolio.
4. Complete the retained executable matrix for all five collection branches: 1/21/101 mixed rows,
   more than four adjacent invalid rows, first/middle/last/out-of-range pages, every scalar evidence
   component, all consumers, stable ordering/query ceilings, paired action/mutation allow and deny,
   and independent 400/403/404/409 behavior. Convert all three review probes into permanent public-
   seam regressions and retain the prior 009L4/009L5 probes.
5. Refactor the guarded Epic 009 E2E seed onto reusable public fixture/domain builders. Runtime
   management code must not import `TestCase` classes, call their `setUp`, or depend on private test
   helpers. Preserve both E2E guards, idempotency, isolated storage/database behavior, and the real
   owner evidence used by the browser contract.
6. Make Playwright seeding correct for both the targeted Epic 009 command and ordinary
   `npm run e2e`: selection of multiple/all specs must provision the union of required deterministic
   fixtures without destructive reseeding or missing Epic 009 actors. Add a non-browser config/
   collection regression for the full-suite command.
7. Retain CR-012's real form logins, real owned Django APIs, state-specific assertions, nine fresh
   screenshots, nine distinct per-run SHA-256 values, and two independent trusted runs. Do not add
   route fulfilment, token injection, production styling, business rules, or unsupported SAP-posting
   success.

## Scope Boundaries

- No Epic 010 schedule, ledger, repayment, interest, DPD, default, or closure behavior.
- No new SAP-posting confirmation actor, permission, adapter, or success evidence under A-135.
- No frontend design-system or production-screen styling change.
- This is the final admitted grouped repair for the current Epic 009 corrective cycle; another
  recurrence of the same selector/owner boundary must fail closed instead of spawning a leaf slice.

## Acceptance and Reverse-Consumer Tests

- The three retained review probes return exact zero/403 outcomes through public HTTP seams on
  SQLite and PostgreSQL; actor, file-byte, completion, CFC-owner, and aggregate variants behave the
  same before count and offset.
- Public Loan Account list/detail stay 403 without `finance.loan_account.read`; assigned Senior
  Finance sees only its permitted account after the permission is granted, while the workspace can
  still initiate through its separate candidate interface.
- Table-driven 1/21/101 tests cover all five branches, every scalar field group, >4 adjacent drift,
  deterministic pages, stable query ceilings, and paired mutation/error outcomes.
- The declared six-test PostgreSQL label runs twice and exercises the production JSON/digest/file-
  eligibility and permission/scope boundary.
- `npm run e2e` collection/config proof provisions all required fixture families; the declared Epic
  009 browser spec still runs twice with nine valid, distinct screenshots and matching manifests.
- Complete configured backend/frontend gates and the prior Epic 009 reverse consumers remain green.

## Risk Level
High

## Acceptance Criteria

- Public reads cannot be widened by a mutation permission or an internal workspace composition need.
- No owner-validity drift can inflate a count, shift a page, advertise a rejected action, or expose
  a row that its scalar/public owner rejects.
- The five-branch matrix is executable rather than inferred from one-row examples.
- Targeted and full Playwright workflows both provision deterministic public-owner fixtures.

## Done Checklist

- [ ] Execution plan and impact boundary written
- [ ] Backend/business RED-GREEN evidence saved
- [ ] Public Loan Account permission and exact scope restored
- [ ] One owner decision consumed by selectors, projectors, details, actions, and mutations
- [ ] Five-branch matrix and six-test PostgreSQL contract green twice
- [ ] Public E2E fixture builder and full-suite seeding regression green
- [ ] Nine-state browser contract green twice with fresh distinct hashes
- [ ] Risk/review evidence completed; commit delegated to Ralph
