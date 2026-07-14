# Risk Assessment

Slice: 008G-tri-party-agreement-workflow
Overall risk: Medium

The change adds one legal verification mutation and one nullable, non-destructive
`loan_documents.verification_remarks` migration. It does not alter existing renderer provenance,
generation, signature, checklist-completion, security, repayment, or disbursement states. Existing
rows migrate safely with null remarks.

Controls:

- Permission plus active Company Secretary role is checked before parsing or object lookup.
- The existing sanctioned Stage-4/current-renderer authority seam locks the loan document.
- Approval-owned frozen subsidiary truth must be complete and true; false/missing/conflicting truth
  fails closed.
- The single legal exact-document selector supplies two canonical maker-attributed signed rows; a
  mismatch, resolution, wrong party/document, absent signed time, null maker, or self-check fails.
- The applicable checklist target is locked and must link the exact document before mutation.
- Document update and audit/version/workflow evidence share one transaction; projection conflicts
  roll everything back.
- Exact replay is zero-write; a changed remark retains immutable old/new history.
- Metadata reads do not expose files, downloads, or plaintext sensitive data.

External effects: none. No network, communication, deployment, file download, repayment deduction,
security invocation, or frontend action was added.

Residual risk: the authoritative five-worker row-lock test is PostgreSQL-only and skipped by the
routine SQLite gate, matching repository convention. The test is present for the PostgreSQL harness;
this slice did not declare the orchestrator runtime capability, so no local PostgreSQL result is
claimed. A-111 records the source-silent current remarks column.

Rollback: revert the route/module/read projections and migration before deployment, or apply a
forward migration after confirming retained remarks are archived. Never drop a migrated column after
production use without preserving its legal audit meaning.
