# Risk Assessment — 011L

## Classification

Medium product risk with database uniqueness and authoritative PostgreSQL race acceptance, as
declared by the prepared slice.

## Controlled Risks

- Financial/statutory math uses only finite `Decimal` inputs. Money is retained at two decimal
  places; displayed ratios at four. NBFC statutory `>50%` decisions use unrounded ratios so display
  rounding cannot suppress a trigger.
- Unique database constraints plus exact input snapshots retain one result per type/FY/quarter.
  Exact replay returns retained truth; changed task/evidence/input replay conflicts.
- Calculations require the matching 011K quarterly task, assigned preparer, current accepted
  evidence, and a distinct snapshotted reviewer. They do not import or mutate finance records.
- Draft submission and final review are separate audited transitions. Accepted breach/trigger
  reviews require reviewer-owned restricted Board evidence. Final review and calculation facts
  reject direct model rewrites.
- Critical create permissions are limited to CFO and Accounts Head delegate roles. Exact reads are
  granted to those roles and Internal Auditor; denied tracker access is audited without changing
  unrelated 011K endpoint side effects.
- One migration adds both period-unique models. Migration sync is clean.

## Residual / Independent Validation

- Local SQLite truth skips the PostgreSQL-only concurrency classes. Ralph must execute
  `StatutoryTrackerPostgreSQLAcceptanceTests` against PostgreSQL with expected count 1, twice, as
  declared by the slice capability.
- A-162 records the source-silent FY/calendar-quarter bridge, rounding convention, and required
  early-warning configuration. A-163 records the bounded Board-evidence ownership rule.
- The orchestrator owns the authoritative impacted/full backend lane and coverage decision; no
  complete suite or local coverage run was performed by the implementation agent.
