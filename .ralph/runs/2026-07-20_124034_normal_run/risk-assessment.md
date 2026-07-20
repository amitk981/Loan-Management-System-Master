# Risk Assessment

Risk level: High (financial configuration and mutable loan projection)

- Scope is bounded to effective-rate admission, activation, explicit-date resolution, loan current-rate
  convergence, reverse consumers, one configurations migration, and permanent tests.
- The principal integrity risk was an ORM bypass creating approved rates without maker/checker,
  timestamp, idempotency, and digest evidence. Standard model/queryset create, update, bulk, and delete
  paths now reject that boundary; the database check constraint independently requires coherent
  proposed/active evidence and distinct maker/checker identities.
- The timing risk was publishing a future rate to `LoanAccount.current_interest_rate` on approval.
  Activation now retains history/notices but updates the mutable projection only when already due.
  Later convergence is an explicit-date, permission-checked, locked, idempotent public operation with
  one audit record.
- The regression risk to invoice/accrual and loan reads is mitigated by public configuration decisions,
  date-bounded projection selectors, 43 focused reverse-consumer tests, and eight prior PostgreSQL owner
  tests. The exact new four-test PostgreSQL class passed twice.
- The migration adds a constraint only; it does not rewrite retained configurations, consumption
  snapshots, histories, notices, invoices, or accruals.
- No frontend, dependency, scheduler policy, benchmark formula, or communication delivery policy changed.

Residual risk: deployment data containing a historically fabricated active row would cause the new
constraint migration to fail closed for investigation. That is preferable to silently blessing
incoherent financial configuration. The orchestrator's full suite and coverage gate remain required.
