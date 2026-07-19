# Risk Assessment

Risk level: Medium

- Selected slice: 010A-loan-account-schedule-and-ledger
- Mode: normal_run
- Manual review required: no; independent Ralph validation remains required.

## Risk Factors

- Financial read truth is introduced, including running opening balances and a new repayment-
  schedule table. Incorrect constraints or owner reconciliation could misstate a loan ledger.
- The coordinator spans loan, SAP, and disbursement owners. Dependency placement and historical
  evidence semantics must remain explicit so later servicing movements do not erase the opening
  disbursement or weaken immutable transfer proof.
- One schema migration adds a financial table and database constraints. Runtime capability is
  `none`; this slice does not claim a PostgreSQL race or mutation contract.

## Controls Applied

- Database constraints enforce positive installment numbers, unique account/installment identity,
  non-negative decimal amounts, exact total/component equality, and the source-defined status set.
- Both endpoints reuse active effective role, `finance.loan_account.read`, canonical object scope,
  immutable loan-creation truth, and current SAP-account identity.
- Historical transfer reconciliation always checks funded amount, activation date, owner relations,
  amounts, action/digest, audit/workflow, and transfer evidence. Only later-owned outstanding/status
  and SAP-posting lifecycle fields are allowed to advance.
- Public tests cover authentication, role/permission, cross-scope nondisclosure, missing objects,
  pagination, empty states, query ceilings, full source-row no-write snapshots, servicing-safe
  history, immutable-fact drift, and database rejection.
- Two independent review axes found and drove closure of the initial dependency-direction,
  unsupported-status, servicing-read, no-write, immutable-fact, and SAP-lifecycle issues.

## Residual Risk

- Schedule population/mutation is intentionally absent; later approved-term ingestion must not
  bypass these constraints or invent amortisation policy.
- `partially_paid` remains a future allocation-owner decision under A-137.
- Initial SAP posting is currently representable only as `pending` under A-135; future governance
  must own any posted/failed transition and evidence while the ledger consumes that owner state.
