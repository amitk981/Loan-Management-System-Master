# Risk Assessment

## Classification

- Risk level: High
- Selected slice: `010N2-epic-010-terminal-servicing-recurrence-repair`
- Mode: `normal_run`
- Standing approval: active; no owner veto exists for this slice.

## Material risks and controls

- Historical MIS could admit an invoice generated after the cutoff or serialize a later issuance.
  The selector now excludes post-cutoff `generated_at` rows, and the lifecycle projector uses
  `generated_at` plus `issued_at`; before/on/after and original-probe tests are GREEN.
- Test-only coupling could conceal broken public repayment setup. The terminal direct-repayment test
  now builds an active account, authority, login, schedule, and command payload through the public
  servicing builder rather than invoking another `TestCase.setUp()`.
- A partially deployed/malformed CR-015 composite response could strand capture before SAP/allocation.
  The frontend retains the canonical single-command path and resumes only when that endpoint returns
  the legacy capture shape; replay uses the same server-owned SAP/allocation seams and idempotency key.
- Reminder provider-effect races must not regress. The exact five-case PostgreSQL class passed twice,
  including repayment, source/scope change, competing worker, retry, and timeout cases.
- Financial and schema regressions remain fail-closed behind independent complete-suite coverage.
  This agent deliberately ran focused tests only, per the run contract; Ralph owns the authoritative
  complete backend suite and coverage floor.

## Residual risk

The legacy capture-shape resume branch is reachable only if the composite endpoint violates its
current response contract. Independent review should confirm this defensive branch remains bounded
to incomplete deployments and is removed when mixed-version operation is no longer supported.
