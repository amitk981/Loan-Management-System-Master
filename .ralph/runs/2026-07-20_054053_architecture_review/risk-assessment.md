# Risk Assessment

Risk level: High findings; Low candidate-mutation risk.

- Selected slice: `architecture-review`.
- Mode: `architecture_review`.
- Production code modified: no.
- Candidate scope: active findings ledger, one numeric corrective slice, one downstream dependency,
  and current-run evidence/artifacts.
- Financial/data-integrity risk: High. Consumed effective-rate periods can be backdated, active rate
  truth is mutable/incoherent with loan histories, and exact allocation replay changes after reversal.
- Matching risk: High. A subsidiary narration with the correct borrower/application plus a competing
  borrower can be automatically admitted.
- Performance/testability risk: Medium. Ledger pagination remains full-history materialisation and
  acceptance suites retain private cross-`TestCase` fixture chains.
- Mitigation: one grouped High-risk corrective (`010E3`) is dependency-ordered before invoice work,
  carries exact stable finding/root/acceptance IDs, requires five twice-run PostgreSQL tests, and
  preserves the existing full independent gate.
- Rollback: documentation-only candidate changes can be reverted by the orchestrator before merge;
  no schema, product behavior, external service, or user data was changed during review.
- Manual review required: independent Ralph validation only; owner approval is already governed by
  the standing approval/veto model.
