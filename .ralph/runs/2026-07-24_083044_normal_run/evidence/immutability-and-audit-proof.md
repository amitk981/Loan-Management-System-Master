# Immutability and Audit Proof

- `AuditObservation` freezes creator ID/name/role/team, `audit_readonly` scope, bounded sanitised
  observation text, resolved source snapshots, and creation time.
- Instance save/delete and queryset update/delete/bulk-update reject retained rows. HTTP PUT/PATCH/
  DELETE return 405 and write central denial evidence.
- Source resolution reads only existing `AuditLog`, `WorkflowEvent`, `VersionHistory`, or
  `ComplianceEvidence` rows. Creation never calls an owning-domain mutation.
- Successful creation writes `audit.observation.created` without observation text or evidence
  content. Successful evidence bytes write `audit.observation.evidence_accessed`; denied authority,
  UUID, method, or capability paths write `audit.observation.access_denied`.
- Signed evidence access is bound to the current user, audit scope, observation, compliance evidence,
  and document. Permission is rechecked after issuance; revoked, tampered, and cross-observation
  attempts remain nondisclosing.

Behavior evidence:

- Creator/source durability: `evidence/terminal-logs/audit-observation-creator-snapshot-green.log`
- Model/API immutability: `evidence/terminal-logs/audit-observation-immutability-green.log`
- Source-family and guessed-ID denial: `evidence/terminal-logs/audit-observation-references-green.log`
- Permission and denial recorder: `evidence/terminal-logs/audit-observation-permissions-green.log`
- Restricted signed download: `evidence/terminal-logs/audit-observation-evidence-green.log`
- 011O/012D/audit/document/catalogue reverse consumers:
  `evidence/terminal-logs/reverse-consumer-suite-final.log`
