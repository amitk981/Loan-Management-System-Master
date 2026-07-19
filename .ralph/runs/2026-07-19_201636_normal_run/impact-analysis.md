# Impact Analysis

Selected slice: `CR-013-epic-009-terminal-owner-boundary-correction`

## Affected backend models, endpoints, and services

- `sfpcl_credit.loans.models.LoanAccount` and the public
  `/api/v1/loan-accounts/` list/detail endpoints. Grep evidence: list and detail flow through
  `processes/loan_account_360.py`, whose `eligible_account_candidates()`, `list_accounts()`, and
  `get_account()` currently compose loan creation, SAP completion, transfer evidence, and role
  scope.
- `sfpcl_credit.disbursements.models.Disbursement` plus current transfer, authorisation, readiness,
  and mutation evidence. Grep evidence: `processes/disbursement_workspace.py` counts candidate
  querysets before `_project_account_rows()` / `_project_disbursement()` can reject them, while
  `disbursements/modules/post_transfer_evidence.py` is the canonical post-transfer resolver.
- `SapCustomerProfileRequest` and its immutable delivery/file facts. Grep evidence:
  `sap_workflow/modules/sap_customer_profile.py` supplies the S36/S37 and account-completion
  selectors; migration `sap_workflow.0002` currently adds
  `delivery_storage_checksum_sha256` with an empty historical default and no reconciliation.
- The public `/api/v1/disbursement-workspaces/` endpoint and S36, S37, combined Senior Finance,
  and CFC branches in `processes/disbursement_workspace.py`.
- Epic 009 browser fixture seeding. Grep evidence:
  `identity/epic009_e2e_fixture.py` imports `sfpcl_credit.tests`, constructs a Django `TestCase`,
  invokes `setUp()`, and calls private helpers; `seed_epic_009_e2e_fixture` consumes that runtime
  builder. Portal/full-suite seeds create governed `DocumentTemplate` identities directly and can
  collide when seed families are combined.

## Frontend screens, components, and routes

- `LoanAccount360`, `DisbursementHub`, and `PaymentAuthorisationHub`, routed by `App.tsx`, consume
  `loanAccountsApi.ts` and `disbursementApi.ts`.
- No frontend source change is planned: the required safe empty/not-found/error and workflow states
  already exist. The retained nine-screenshot Playwright contract will verify that backend owner
  correction does not change the approved presentation.
- `FRONTEND_DESIGN_RULES.md` compliance: no new components, styles, colours, typography, layouts,
  mock data, or browser-owned authority decisions will be introduced.

## Blast radius across other modules

- Loan creation/lifecycle and terms remain the immutable account-creation inputs.
- SAP request send/completion, stored workbook evidence, communication/audit/workflow evidence,
  and assigned-user scope all feed the common account/workspace decision.
- Disbursement readiness, initiation, CFC authorisation, transfer success, advice, and initial SAP
  posting consume the same identities and must reject any identity hidden by the owner decision.
- Member bank accounts, source-bank governance, legal/document/security readiness, communications,
  audit, and workflows are evidence providers; their private models/policies must not be copied into
  view code.
- Staff and portal E2E seed commands share users, governed document-template identities, files, and
  browser database state. The union must be idempotent and order-safe.

## Existing coverage and regressions to add

- Loan accounts: extend `test_loan_account_reads_api.py` / the terminal read-boundary regression
  module with a public list/detail checksum-drift proof and paired mutation rejection.
- Staff workspace: extend `test_disbursement_workspace_api.py` / terminal regression coverage for
  stale initiation, exact Senior Finance assignment, exact CFC task authority, truthful count/page
  parity, and paired action/mutation rejection.
- SAP workflow: add historical-state-to-leaf migration tests proving coherent legacy completion is
  reconciled while absent/mismatched/tampered evidence remains fail-closed.
- Identity/E2E fixtures: add source-boundary tests excluding test/private-helper imports plus actual
  fresh-database staff/portal/Epic-009 seed-family order and idempotency tests.
- Cross-owner acceptance: extend the six-test
  `Epic009ReadBoundaryPostgreSQLAcceptanceTests` label and bounded table-driven 1/21/101,
  adjacent-invalid, first/middle/last/out-of-range, scalar-drift, 400/403/404/409, action/mutation,
  and query-ceiling coverage across the five collection branches, reusing public scenario builders.
- Frontend: run the impacted unit tests and the declared nine-state Playwright spec; no frontend
  regression file should change unless a public response-shape defect is discovered.

## Risk and containment

This is High risk because a selector error can disclose member/financial records or permit a stale
financial mutation. Changes will be kept behind module-owned public decisions, exercised through
HTTP/domain seams, and validated on PostgreSQL twice. No source documents, protected paths, or
quality/risk rules will be changed.
