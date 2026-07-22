# Risk Assessment

Risk level: Medium (slice-declared)

- Selected slice: 011H-noc-issuance
- Mode: normal_run
- Schema impact: one additive `closure.0002_noc_issuance` migration creates `nocs` and extends the
  existing NOC requirement status vocabulary from pending to completed.
- Financial/compliance risk: a NOC is authoritative no-dues evidence. Controls lock the retained
  closure, require zero-balance full repayment, validate the approved/current-renderer NOC document
  against canonical merge facts, and freeze generation audit/template/renderer/checksum provenance.
- Permission risk: issue requires Critical `closure.noc.issue`, Company Secretary/Compliance role,
  and active Compliance Team object scope. Credit reads are limited to the manager who retained the
  close; Company Secretary/Compliance reads require that same team relationship; borrower access is
  active-portal self-only and Auditor access requires the governed read grant.
- Concurrency/idempotency risk: the closure row is the serialization point; exact replay returns the
  retained chain and changed replay is denied. The declared five-thread PostgreSQL acceptance passed.
- Delivery risk: the existing dispatcher retains the queued job; provider sent/failed truth is read
  from that owner and synchronized to the NOC with an append-only correlated audit. Handoff failure
  rolls back communication/NOC success and remains retryable.
- Document-content risk: only an approved effective NOC template containing every required canonical
  placeholder is accepted; the generation audit's merge digest must match current closure facts and
  the active Company Secretary signatory on the day of issue.
- Compatibility risk: closure snapshot facts remain immutable; only the NOC checklist requirement
  makes its owner-controlled pending-to-completed transition. Existing document and communication
  regression packs are green.
- Deferred decision: A-160 records email-only delivery and explicit Company Secretary signatory until
  governed hard-copy dispatch/configured-signatory infrastructure exists.
- Manual review required: independent Ralph validation remains required before commit/merge.
