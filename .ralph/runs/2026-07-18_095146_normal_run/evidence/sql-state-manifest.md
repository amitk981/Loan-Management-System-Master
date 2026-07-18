# 009G4 SQL and State Manifest

## Owner anchor

- Migration: `legal_documents.0015_checklist_constraint_state_owner_anchor`
- Operations: `[]`
- `sqlmigrate`: `No operations found.`
- Database writes on apply/reverse: none
- Data transforms on apply/reverse: none

## Dependencies

- `legal_documents.0014_staff_documentation_durable_actions` — current legal owner leaf
- `disbursements.0005_disbursementadviceintent_loanregisterupdate_and_more` — reviewed historical
  replacement of the two Epic-009 placeholders
- `disbursements.0007_remove_disbursement_disb_success_evidence_complete_and_more` — current 009G3
  disbursement leaf
- `communications.0004_advice_outbox_and_receipt_owner` — current 009H3B communications leaf

## Retained state contract

At the anchor, after reversing only the empty anchor, and after reapplying it:

- `checklist_finance_requires_sanction`: exactly one model-state and physical constraint
- `checklist_ready_evidence_complete`: exactly one model-state and physical constraint
- `checklist_account_requires_epic_009`: absent from model state and physical schema
- `checklist_finance_requires_epic_009`: absent from model state and physical schema
- The complete introspected `document_checklists` physical schema is identical.
- The retained checklist and checklist-action primary keys, foreign keys, statuses, meanings,
  comments, actor snapshot, role, request, workflow, and application values are identical.

Executable proof: `evidence/terminal-logs/tdd-green-refactor.txt` (6/6 tests pass).
Migration sync and zero-SQL proof: `evidence/terminal-logs/backend-static-gates.txt`.
