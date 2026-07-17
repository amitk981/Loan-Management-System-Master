# Risk Assessment

Risk level: High

- Selected slice: 009H-disbursement-advice-and-communication.
- Money/state risk: advice reads and reconciles exact 009G success but changes no transfer, CFC,
  account balance/status/terms, Loan Register, checklist, repayment, schedule, or interest fact.
- External-side-effect risk: the MVP Manual adapter performs no network call and returns a
  deterministic accepted identity. The shared adapter interface validates payload/result facts;
  adapter rejection rolls back before any sent communication or disbursement link is retained.
- Duplicate/race risk: the disbursement row and source relations are locked before delivery. Exact
  replay validates the singular communication/audit/workflow ledger and does not invoke the adapter;
  changed/stale replay conflicts. Two five-caller PostgreSQL tests are declared for twice-run
  orchestrator acceptance; the sandbox itself denied `/tmp/.s.PGSQL.5432`.
- Privacy risk: body/audit facts use canonical borrower identity and masked UTR only. No full source/
  destination bank, evidence checksum/storage key, PAN/Aadhaar, document URL/token, authorisation
  comments, or unrelated owner evidence is emitted.
- Permission risk: active persisted exact Senior Finance maker or CFC checker plus the High send
  grant is required. Missing/cross-object scope is nondisclosing; role/grant/contact alone fails.
- Template risk: exactly one approved effective borrower-email advice template must declare and use
  the exact safe variable set. Missing, ambiguous, extra, or incomplete templates fail closed.
- Schema/dependency risk: no migration, financial table, package, or network dependency was added.
- Diff risk: 17 non-run paths changed and the implementation remains below configured 30-file /
  2,000-line / one-migration limits. Protected and source paths are unchanged.

Residual risk: authoritative PostgreSQL scheduling/locking behavior must pass the orchestrator's
declared twice-run capability gate before commit. A real provider remains future adapter work; A-098
records the source-silent template event code/variable and MVP transport convention.
