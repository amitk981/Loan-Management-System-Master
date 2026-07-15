# Epic 009 Digest — SAP, Loan Account, and Disbursement

Sources distilled while sharpening 009A on 2026-07-15: `implementation-roadmap.md` §14,
`integrations.md` §8/§33.1, `data-model.md` §19.1-19.2, `api-contracts.md` §29.1, and
`functional-spec.md` BR-047-BR-050/M07-FR-001-M07-FR-010.

## 009A SAP Customer Profile Request

- MVP is manual/file-first. After terminal sanction, a Credit Manager creates the request and a
  genuine Excel/Annexure-I artifact for an active Senior Manager Finance assignee; direct SAP API
  integration is future scope.
- `POST /api/v1/loan-applications/{id}/sap-customer-profile-request/` returns the request id,
  `draft` status, Excel file id, and assignee. Canonical borrower/application/sanction facts should
  be server-owned even though the illustrative API body lists them, so a caller cannot forge the
  source evidence.
- Required frozen facts are application number, legal name/type, PAN, registered address, folio,
  sanctioned amount/date, individual-only Aadhaar, and optional email/mobile/current verified-bank
  last-four plus IFSC. Full sensitive values are encrypted at rest and excluded from ordinary
  projections/log/audit evidence.
- The table stores application/member, status (`draft/sent/completed`), requester, assignee, frozen
  fields, linked Excel file, and sent/completed timestamps. Source idempotency identity is
  application plus active request; retries/concurrent creates must not duplicate request, file,
  workflow, or audit facts.
- INT-SAP-001/002/006 and R5-AC-001/002 require post-sanction creation, complete Excel details, and
  audit evidence. Code confirmation, duplicate-code blocking, reuse, and readiness belong to 009B+
  and must not be claimed by 009A.
- Source schema says Aadhaar is non-null while the integration payload says “individual only” and
  the platform supports FPC borrowers. Treat Aadhaar as conditionally required/encrypted for
  individuals and absent for FPCs; do not fabricate an FPC Aadhaar value.
