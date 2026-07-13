# Risk Assessment

Risk level: Medium.

- Selected slice: `007C-cfo-and-director-threshold-routing`.
- Data/schema impact: one additive `approval_actions` read-ledger migration with unique
  case/approver and valid-decision constraints. No action is created by this slice.
- Authority/security impact: `approvals.case.read` gates all endpoints; only pending stored
  approvers with the action-specific permission receive enabled actions. The maker and unrelated
  users without read permission receive 403; global readers receive no assignment actions.
- Financial impact: read-only APIs expose stored amount/provenance but execute no sanction action,
  register write, notification, or money movement.
- Snapshot risk: complete 007B matrix/committee/policy provenance is required, while the ordered
  required list alone controls assignment. Tests prove current-row mutations and a contradictory
  same-amount version-1 shell cannot alter the historical queue.
- Known deferred constraint: optional `digital_signature_id` is a nullable UUID until the source
  `signature_records` owner exists; A-077 forbids treating it as verified evidence.
- Manual review required: normal orchestrator validation only; no owner veto applies to this
  Medium-risk slice.
