# Risk Assessment

Risk level: High

- Selected slice: 009B2-sap-delivery-replay-audit-and-owner-seam-closure
- Mode: repair
- Standing approval: confirmed; no owner veto exists.

## Material risks

- Restricted Annexure-I identity/bank content now crosses a new authenticated download boundary.
- SAP completion is a Critical finance fact; replay, code uniqueness, actor ownership, and audit
  vocabulary errors could create duplicate or misleading customer-master truth.
- One compatibility migration adds delivery/capability/digest state to the applied Finance-owned SAP
  request table. A bad migration or partial lifecycle update could strand sent requests.
- Concurrent first request/code completion remains PostgreSQL-sensitive.

## Controls and evidence

- Physical workbook storage remains authenticated ciphertext. Send first verifies stored ciphertext,
  decrypts the workbook, checks its XLSX signature, computes a plaintext checksum, and requires the
  manual adapter to return that exact checksum before changing status.
- Capability claims bind request, delivery, document, assignee, checksum, and persisted version;
  expiry and consumption are checked under a row lock. Replacement invalidates the prior version,
  and every successful download is checksum-verified again.
- Only the frozen active Senior Manager Finance assignee with the persisted completion permission can
  issue/read. Cross-user/request/application/file, expired, consumed, replaced, and tampered cases
  are regression-tested and nondisclosing.
- Completion stores a supplied/omitted-aware canonical digest. Global normalized code uniqueness,
  one active member code, exact terminal sanction, confirmation provenance, and assignee locks remain.
- Mandatory new/reuse events and every sensitive SAP audit freeze role/team/request/network context;
  recursive scans exclude identity, bank, workbook, token, and raw SAP-code plaintext.
- All three PostgreSQL request/code/member race classes passed twice. Full backend/frontend gates and
  migration drift are green.

## Residual risk

- Applied SAP tables and the existing Finance implementation kernel remain a deliberate compatibility
  seam so this corrective slice does not duplicate or rewrite retained data. All HTTP/downstream
  callers are guarded through the installed public SAP owner; a future physical app-state transfer
  must be a separately gated state-only migration if source ownership requires it.
- Manual delivery proves governed in-platform receipt; it intentionally does not prove delivery by a
  real email or SAP provider. Future API/email adapters must preserve the same idempotent contract.

Manual review required: the orchestrator must independently rerun all configured gates and the
declared PostgreSQL capability before commit/merge/push.
