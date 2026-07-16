# Risk Assessment

Risk level: High

- Selected slice: `009A-sap-customer-code-request`
- Mode: repair
- Standing approval: applies; no `[revoked]` entry was found for this slice.
- Sensitive data: PAN and individual Aadhaar are decrypted only from the shared field-encryption
  source, immediately re-encrypted for the request snapshot, and written to physical document
  storage only as authenticated ciphertext. Plaintext exists transiently only while rendering the
  restricted outbound workbook in memory and is absent from responses, errors, audit, workflow,
  integration, and application logs.
- Financial/workflow integrity: creation depends on the exact current terminal sanction, locks the
  persisted actor/application/member/decision/request/code/assignee authorities, and writes request,
  document metadata, audit, and workflow evidence atomically. PostgreSQL five-caller acceptance ran
  twice after the final review changes.
- Database impact: one initial Finance migration creates the request table, SAP-code shell, active
  uniqueness constraints, status/amount checks, and queue/read indexes. No completion, SAP code,
  loan-account, readiness, disbursement, or integration send behavior is implemented.
- Availability/compatibility: historical one-way identity tokens are rejected rather than exported
  as fabricated full values (A-120). The single-sheet OOXML renderer is dependency-free and isolated
  behind a tuple-to-bytes seam (A-123); the encrypted-storage reader is required to recover workbook
  bytes from physical storage.
- Residual risk: 009B must use `EncryptedAnnexureStorage.read_verified` for send/download and must
  preserve the active-code conflict and exact terminal-cycle checks. Production key management and
  historical identity remediation remain governed by the shared encryption owner.

Manual review required: yes, because this is a high-risk sensitive-data and financial workflow
boundary. Independent Standards/Spec review completed and all findings were resolved or recorded.
