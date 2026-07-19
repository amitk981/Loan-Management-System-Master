# Risk Assessment

Risk level: High

- Financial/data-integrity risk: duplicate receipts could later double-allocate. Mitigation:
  canonical bank-reference and idempotency uniqueness, locked account serialization, conflict rules,
  and twice-run PostgreSQL races.
- Premature-balance risk: capture could alter principal, schedule, or ledger before 010C. Mitigation:
  only receipt/audit/task/obligation records are written; tests compare unchanged loan truth and run
  focused 009/010A regressions.
- Authority risk: permission alone could reach an unrelated role/object. Mitigation: active user,
  effective source role, exact permission, serviceable state, and source object scope are all required.
- SAP-truth risk: local action could imply provider automation. Mitigation: it records a manual source
  reference, actor, aware timestamp, and audit only; no provider success is claimed.
- Sensitive-evidence risk: audit could leak bank/SAP references or remarks. Mitigation: audit manifests
  omit evidence UUID, references, and remarks; permanent tests assert absence.
- SLA assumption: A-138 documents weekday-only next-working-day calculation until an approved holiday
  calendar exists.
- Residual risk: independent validation must run complete coverage, frontend gates, migrations, and
  the PostgreSQL class twice before commit/merge.
