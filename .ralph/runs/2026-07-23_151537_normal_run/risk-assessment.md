# Risk Assessment

Risk level: High

- Selected slice: `011M3-global-search-compliance-results`
- Privacy/data exposure: mitigated by safe-field allowlists, canonical selectors, whole-group
  omission on provider/contract failure, action validation, and negative assertions for evidence,
  legal, KYC, snapshot, note, guessed-ID, and cross-scope content.
- Permission risk: mitigated by exact provider permission admission, source-owner object scopes,
  a Compliance/CFO/Company Secretary/Internal Auditor matrix, and route actions that additionally
  require `compliance.task.read`.
- Provenance risk: mitigated by canonical audit actor/time for control/task changes and retained
  preparer/reviewer/assignee facts for other record types.
- Pagination/order risk: mitigated by deterministic owner ordering, the inherited 100-row cap, and
  explicit 21-row continuation coverage.
- Regression risk: 61 focused backend tests, six focused frontend tests, Django check, migration
  sync, typecheck, lint, and build pass. The orchestrator retains the authoritative full backend
  coverage lane for this High-risk candidate.
- Browser infrastructure: two local declared runs reached healthy servers but Chrome exited before
  test execution. No screenshot was fabricated; independent trusted validation remains required.
- Schema/dependency impact: none.
- Protected/source paths: none modified.

Residual risk: the independent validator must complete the two browser runs and create
`global-search-compliance-results.png`; otherwise the candidate must remain uncommitted.
