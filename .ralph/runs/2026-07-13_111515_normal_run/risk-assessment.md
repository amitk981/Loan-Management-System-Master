# Risk Assessment

Risk level: High

- Selected slice: 006Z15-member-public-action-authority-matrix-closure
- Mode: normal_run
- Authorization impact: member object-scope denials are now proven at ten real production
  interfaces; HTTP adapters distinguish object denial from missing permission and maker-checker
  denial using typed exceptions.
- Cross-object impact: staff eligibility and portal own-data/borrower-limit routes now reject a
  different caller-supplied member id before calculation or evidence writes.
- Data impact: no schema or migration change. Successful existing writes are unchanged; denied
  requests preserve member, identity, supply, service-maker, status, eligibility, history, audit,
  and workflow ledgers.
- Compatibility risk: callers that previously sent a foreign `member_id` query/body and relied on
  it being ignored now receive canonical `403 OBJECT_ACCESS_DENIED`. This is intentional security
  hardening and is documented in `API_CONTRACTS.md`.
- Controls: standing owner approval; RED/GREEN TDD; independently selectable action rows;
  action-specific phase omission guards; exact ledger deltas; focused regression suites; full
  backend/frontend configured gates; two-axis review.
- Residual risk: PostgreSQL concurrency is not touched and this slice declares no PostgreSQL runtime
  capability. The source-required empty filtered member list remains `200` rather than collection-
  level `403`, recorded in A-078.

Manual review required: no; standing approval and all gates apply.
