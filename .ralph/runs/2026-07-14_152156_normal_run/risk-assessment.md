# Risk Assessment

Risk level: Medium

- Selected slice: 008E-signature-mismatch-workflow
- Mode: normal_run
- Data risk: one additive `signature_records` migration with protected foreign keys, bounded
  vocabularies, unique current signer identities, and database consistency checks. No destructive
  migration or backfill.
- Authorization risk: action-specific Compliance capture and Company Secretary resolution are
  enforced inside the legal-documents module before target/evidence mutation; non-Stage-4 and wrong
  roles are nondisclosing and zero-write.
- Workflow risk: signature mutation, application-owned mismatch fact, checklist applicability, and
  audit/version/workflow ledgers share one transaction. Completed evidence raises an atomic conflict.
- Evidence risk: High assumption A-107 interprets §26.8's document id through the existing current-
  renderer legal-document/file relationship and adequate declaration stamp because no signed-copy
  or bank-attestation aggregate exists. This never grants download or completion.
- Concurrency mitigation: loan-document row locking plus database uniqueness retains one current
  signature identity; exact replay is zero-write and real changes retain history.
- External impact: no frontend, network, deployment, communication, or external-service action.
- Manual review required: normal independent Ralph validation and architecture review; no owner
  approval pause is required under standing approval.
