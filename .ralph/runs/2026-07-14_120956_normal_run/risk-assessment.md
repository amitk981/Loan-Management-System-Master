# Risk Assessment

Risk level: Medium as declared by the slice, with critical transaction/permission paths reviewed.

- Selected slice: `008C-documentation-checklist-applicability`; mode: `normal_run`.
- Data impact: one additive migration creates `document_checklists` and `checklist_items`. Protected
  application/loan-document links, unique application/item identities, bounded states, and database
  consistency constraints prevent invalid or duplicate ledgers. Loan/signature transitions remain
  explicitly null-only until their real owners exist.
- Transaction impact: the public final-approval path supplies a checklist callback inside the
  existing approval transaction. Forced checklist failure proves approval action, sanction,
  register/communication evidence, application status, and checklist all roll back. Conflict-denial
  audits still commit through their intentionally separate failure path.
- Access impact: legal GET requires `documents.checklist.read` plus source-authorised application or
  approval-cycle scope. Tests cover missing permission, permission-only, unrelated committee,
  attributable committee, Compliance, Company Secretary, and audit-read scope.
- Concurrency impact: application row locking plus unique constraints passed two independent
  five-worker PostgreSQL runs with one checklist, eleven items, and one creation audit.
- Residual risk: A-104 documents the shared pre/post-sanction GET compatibility seam; A-105 records
  conservative missing/mixed/conflicting applicability blockers pending governance. 008K/009C must
  install real protected signature/loan links before those ids can become non-null.
- No destructive migration, real personal/financial fixture, network call, external communication,
  deployment, Git add/commit/merge/push, or protected-file change occurred.
