# Risk Assessment

Risk level: High (owner standing approval; no veto entry found).

- Selected slice: `008A2-template-effective-integrity-and-file-reference-boundary`.
- Database risk: one additive migration creates a lock-identity table with a unique
  document-type/borrower-variant key. It does not rewrite, delete, or relink retained templates or
  files. Django migration drift is clean; PostgreSQL races passed twice.
- Authorization risk: a new Critical `documents.template.file_reference` permission is deliberately
  separate from template read/manage and file download, and is seeded only to the existing
  Compliance document-preparation owner. Nondisclosing denials and zero-write matrices pass.
- Integrity risk: every catalogue write now takes a persistent identity lock. The five-request
  first-version race retains exactly one template/audit/version-history set; successor replay still
  retains one linked successor and evidence set.
- Compatibility risk: routes, request/response envelopes, fields, filters, pagination, and metadata-
  only behavior are unchanged. Existing callers that relied on a bare file row or download
  permission as template-reference authority now fail closed as required by the corrective slice.
- Governance risk: FPO mapping remains unresolved. Only `individual_farmer` resolves; other member
  variants return configuration-required validation per A-097. A-099 records the narrow provenance
  labels/permission default pending confirmation.
- Operational risk: no dependency, frontend, generated document, external call, communication,
  deployment, commit, merge, or push was performed. No protected or source file was modified.

Residual risk is limited to governance confirming the FPO mapping and template-source provenance/
role labels; both are centralized behind one resolver/reference boundary for safe later revision.
