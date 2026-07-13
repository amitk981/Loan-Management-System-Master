# Focused Approval Action Contract Evidence

Verified through `ApprovalCaseRoutingApiTests` public HTTP requests:

- Partial `POST .../approve/` returns HTTP 200 with version 3/pending status; immediate collection,
  detail, and action data agree on immutable route provenance, the CFO `approved` decision and
  non-null `acted_at`, and disabled actor actions.
- Stale positive-integer version returns `409 STALE_VERSION`; acted/excluded/closed return
  `409 TRANSITION_CONFLICT`; unassigned object scope returns `403 OBJECT_ACCESS_DENIED`;
  contradictory routing returns `404 NOT_FOUND`; missing approve/reject/return permission returns
  `403 FORBIDDEN`. Every ordinary denial preserves exact business ledgers.
- Blank reject and return comments return `400 VALIDATION_ERROR`; approve permits omitted comments.
- Final approval returns HTTP 200 with approved/version 4 and `sanction_decision_created: true`.
  The same transaction persists one pending email Communication addressed to team
  `credit_assessment`, one linked Notification, and one metadata-only communication audit.

Runtime proof is retained in the focused RED/GREEN logs, both PostgreSQL race logs, and the full
backend gate log in the sibling `terminal-logs/` directory.
