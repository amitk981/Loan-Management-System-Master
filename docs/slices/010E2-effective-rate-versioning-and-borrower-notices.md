# Slice 010E2: Effective Rate Versioning and Borrower Notices

## Status
Not Started

## Runtime Capabilities
- `postgresql-five-race-acceptance`

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 identified M10-FR-001 and M10-FR-002 as unowned by
the executable queue before invoice and accrual calculations consume rate history.

## Goal
Create governed, effective-dated floating-interest configuration and an honest borrower-notice
obligation so every later calculation resolves one immutable rate version for its period.

## User Value
Accounts can prove which approved rate applied on a date, and borrowers receive traceable rate-change
notice truth without the system pretending an external message was delivered.

## Depends On
- 010E

## Source References
- `docs/source/functional-spec.md` M10-FR-001 and M10-FR-002
- `docs/source/api-contracts.md` section 41.4 Interest Rate Config
- `docs/source/data-model.md` sections 18.5 and 25.3
- `docs/source/domain-model.md` sections 13 and 19.2
- `docs/source/auth-permissions.md` `config.interest_rate.manage`
- `docs/source/user-flows.md` rate-change communication requirements
- `docs/source/screen-spec.md` S47 and common floating-rate rules
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md`

## Prototype Reference
- `sfpcl-lms/src/pages/interest/InterestManagement.tsx`

## Screens Involved
None in this slice; 010M owns staff configuration/status wiring.

## Frontend Scope
None.

## Backend/API Scope
- Implement the section-41.4 list/create/activate contract through the existing versioned-config
  owner, including rate type/value, effective date, approved benchmark/spread/reset fields when
  configured, communication-required truth, creator/approver, and immutable history.
- Resolve exactly one active version for a calculation date. Reject overlaps, gaps that would permit
  a fabricated rate, retroactive mutation of consumed periods, changed replay, or caller-supplied
  "current" truth.
- Activation creates borrower-notice obligations for affected active loans when communication is
  required. Use existing email/SMS adapters and delivery receipts; pending/failed delivery remains
  visible and never becomes success from queueing alone.
- Do not invent benchmark, spread, reset, or penal-interest policy when the source leaves it open.

## Database/Model Impact
At most one non-destructive migration for effective-dated rate configuration/history and its durable
notice-obligation linkage, reusing existing configuration and communications owners where possible.

## API Contracts
Implement section 41.4 in `docs/working/API_CONTRACTS.md` and document deterministic period
resolution, activation conflicts, and notice status without provider fabrication.

## Permissions
Require `config.interest_rate.manage`, object/configuration scope, maker-checker separation, and the
existing communication authority. Read access does not imply create or activate.

## Audit Requirements
Audit proposal, approval/activation, effective dates, old/new rate metadata, notice creation and
delivery outcome without logging borrower contact details or message bodies.

## Validation Rules
- Effective periods cannot overlap; one date resolves zero or one version, and zero fails closed.
- A version already consumed by an invoice/accrual cannot be mutated or backdated over that period.
- Activation and notice fan-out are atomic at the local system-of-record boundary and replay-safe.

## Trusted PostgreSQL Acceptance
- Test: `sfpcl_credit.tests.test_interest_rate_config_api.InterestRateActivationPostgreSQLAcceptanceTests`
- Expected tests: 3

## Test Cases
- RED then GREEN: create/approve/activate two non-overlapping versions and resolve the correct rate at
  before/at/after boundaries; overlap, gap, and backdated consumed-period changes fail closed.
- Concurrent activation retains one effective winner and one notice obligation per affected loan.
- Exact replay, changed replay, maker-checker, permissions, communication failure/retry, immutable
  history, and sanitised audit coverage.
- Reverse-consumer tests prove 010F/010G can consume historical rates without rewriting old results.

## Visual Acceptance Criteria
Not applicable (backend only).

## Evidence Required
Saved RED/GREEN output; section-41.4 examples; effective-period boundary matrix; maker-checker and
notice-delivery truth; twice-run PostgreSQL acceptance; reverse-consumer and full gates.

## Risk Level
High

## Acceptance Criteria
- Floating rates are versioned, effective-dated, immutable after use, and permission-correct.
- Required borrower notices have durable, honest delivery truth.
- Invoice/accrual consumers can resolve a deterministic historical rate.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Code, migration, and contracts implemented
- [ ] Permissions, maker-checker, audit, and notice truth tested
- [ ] PostgreSQL acceptance passed twice
- [ ] Reverse consumers and full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
