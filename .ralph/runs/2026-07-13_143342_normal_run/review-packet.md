# Review Packet: 2026-07-13_143342_normal_run

## Result
Ready for independent validation

## Slice
007D2-approval-action-boundary-and-postgresql-race-closure

## Recommended Next Action
Validate and commit this slice, then run 007D3.

## Standards Review

- Deep-module seam: HTTP handlers remain thin; approval actions call the approval-case projection
  and communication adapter rather than duplicating serializers or notification persistence.
- Transactions: application -> appraisal -> case locks precede predicates and mutation. Owner and
  case state changes use the shared transition guard. PostgreSQL races prove serial behavior.
- Contracts/security: action-specific permissions and attributable object scope remain backend-
  enforced. Collection/detail/POST share reason decisions; ordinary denials are zero-write.
- Audit/privacy: action and communication audits identify actors/targets/metadata; communication
  body snapshots are not copied into audit metadata.
- Diff safety: no protected/source/frontend/schema/dependency files changed; Ralph size limits are
  respected. No unresolved Standards finding remains.

## Spec Review and Traceability

- API §25.3-25.7/§44 says reads expose action history and authoritative available actions; code now
  uses the history-aware detail projection for collection/detail/action and one availability
  function. Verified by `test_partial_action_collection_detail_and_action_share_history_aware_projection`
  and the independently named denial rows.
- Data model §§15.3-15.5/§34 and codebase-design §§13.1/22.3 require immutable transactional
  approvals with concurrency control. Verified twice on PostgreSQL by both
  `ApprovalActionConcurrencyTests` races and exact ledger assertions.
- M05-FR-007/008 requires approve/reject/return with reasons for reject/return. Verified by omitted
  approve, blank reject, blank return, guarded owner-state, stale, and parity tests.
- Data model §24.2 and M05-FR-010 require Credit Assessment communication. Terminal outcomes now
  create one pending Communication, linked team Notification, and metadata-only audit through the
  communications module. Success and forced-failure rollback tests verify atomicity.
- Deliberate deferrals: immutable returned-case resubmission is 007D3; conflict-specific audited
  denial is 007E; registers remain 007F/007H. No unresolved Spec finding remains.

## Evidence

- RED/GREEN and focused logs: `evidence/terminal-logs/`
- PostgreSQL race runs: `postgresql-approval-action-races-run-1.log` and `run-2.log`
- Full gates: `backend-full-gates.log`, `frontend-full-gates.log`
