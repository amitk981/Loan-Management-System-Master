# Risk Assessment

Risk level: Medium (slice-declared); independent validation may classify the model/routing change
for a complete backend lane under Ralph policy.

- Selected slice: 011G-closure-readiness
- Mode: normal_run
- Schema: one new `closure` migration creates immutable financial-close and explicit downstream
  requirement records with one-close-per-loan and bounded-state database constraints.
- Financial integrity: close locks the loan row, derives balances and blockers on the server, and
  rechecks them in the same transaction. PostgreSQL close/repayment, close/recovery, and duplicate
  races passed twice.
- Mutation integrity: closed loan instance save, queryset update/delete, and bulk update paths lock
  the same row and fail closed. This shared guard was covered by focused reverse-consumer tests.
- Authorization: readiness requires the read permission plus Credit/CS/Auditor scope; close requires
  critical permission and Credit/CS scope at a repayment/recovery closure stage. Auditor is read only.
- Source conflict: account status becomes `closed` for API §36.2, while the retained stage is only
  `financially_closed`; NOC/security/archive remain explicit pending/not-applicable requirements.
- Policy boundary: only `full_repayment` is supported. No settlement, write-off, waiver, or interest
  adjustment business rule was invented; non-zero interest remains a blocker.
- Data exposure: denial evidence uses bounded reason codes and named checks; caller notes pass the
  shared safe-audit-text guard; no personal or financial fixture data was added.
- Scope/diff: backend plus working API contract only, one migration, no dependency or frontend change,
  approximately 1,605 product/contract added lines (below the 2,000-line cap).
- Residual risk: downstream 011H-J must consume and advance only their owned requirement records;
  this slice intentionally does not implement those controlled actions.
- Manual review required: yes, through Ralph's independent validation and PostgreSQL capability gate.
