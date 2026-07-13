# Independent Spec Review

1. High: post-action collection/detail/action parity is false. Collection uses the raw immutable
   required-approver snapshot, while detail/action overlay `decision` and `acted_at`. 007D2 owns one
   history-aware projection and immediate read/write parity tests.
2. High: 007D's required simultaneous/final-action PostgreSQL acceptance is absent. No threaded
   transaction test, runtime capability, twice-run evidence, or exact loser ledger exists. 007D2
   owns distinct-approver and duplicate-final races.
3. Medium: terminal actions create `Notification` directly instead of crossing the required 003I
   communication boundary. 007D2 owns one transactional Communication/linked-notification/audit
   adapter path and rollback test.
4. Medium: application/appraisal statuses are assigned directly and the promised closed, excluded,
   contradictory, blank-return, and per-action denial matrix is incomplete. 007D2 owns shared guard
   semantics and independently named public denial rows.

M02-FR-004..006 remain substantive with the new real-boundary authority/substitution proof.
M05-FR-001..006 remain substantive; M05-FR-007/008 are partial on the listed action gaps,
M05-FR-009 remains explicitly deferred to 007H, and M05-FR-010 is partial until 007D2. No material
scope creep was found.

