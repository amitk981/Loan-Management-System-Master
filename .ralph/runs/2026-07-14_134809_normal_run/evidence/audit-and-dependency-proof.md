# Audit and Dependency Proof

## Exact audit semantics

`document_checklist.created` records the application, canonical approval case, sanction decision,
source reason, all initial item facts, request id, IP, user agent, actor roles, and actor teams. The
matching workflow event carries the same evidence.

Later actions are deliberately disjoint:

- `document_checklist.applicability_changed` old/new item snapshots contain only required,
  applicable, completion, applicability source, and blocker facts. They never claim a generated-
  document relationship change.
- `document_checklist.linkage_changed` old/new item snapshots contain only `loan_document_id`.
  They never claim applicability or completion changes.
- Exact replay, denied reads, legacy-provenance exclusion, and transactional rollback create no
  success audit/workflow evidence.

Tests assert request id `req-applicability-correction`, IP `203.0.113.44`, user agent `Checklist
Correction Test`, plus actor role/team and canonical approval/sanction ids. Linkage uses the distinct
request `req-current-renderer-link` and asserts an exact one-key linkage projection. The label/order
regression proves presentation drift cannot create an identical-snapshot applicability event.

## Dependency direction

The sanctioned completion dependency is top-down:

```text
processes.sanction_completion
  -> approvals.modules.approval_actions (private completion-bound writer)
  -> legal_documents.modules.document_checklist
```

`approval_actions` contains no `legal_documents` import. `legal_documents.document_checklist`
contains no `members` import or `CancelledCheque` query; it consumes
`applications.modules.document_checklist_facts`. Checklist reads delegate permission, A-104 routing,
parent disclosure, and object scope to `approvals.modules.document_checklist_access` before querying
the legal checklist tables. These directions are asserted by
`test_dependency_direction_keeps_approvals_free_of_legal_imports` and the fact/read-boundary tests.
