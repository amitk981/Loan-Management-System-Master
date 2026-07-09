# Ralph Handoff

## Last Run
2026-07-09_200049_normal_run

## Current Status
Slice `005D-application-document-checklist` completed successfully.

The application-document/checklist backend now includes:
- `application_documents` metadata rows with UUID PK, loan application FK, linked
  `documents.DocumentFile`, document type, party type/ID, required flag, submission status,
  verification status, verifier actor/time, remarks, version number, and actor timestamps.
- `GET/POST /api/v1/loan-applications/{loan_application_id}/application-documents/`
- `POST /api/v1/application-documents/{application_document_id}/verify/`
- `GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`
- `POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`

Permission and access order:
- List/checklist/refresh require `applications.loan_application.read`.
- Upload requires `applications.document.upload`.
- Verify requires `applications.document.verify`.
- Unknown applications/document metadata return `404 NOT_FOUND`.
- Missing global permission returns `403 PERMISSION_DENIED`.
- Application scope uses `applications.services.evaluate_application_object_access(...)`;
  same-permission actors outside scope receive `403 OBJECT_ACCESS_DENIED`.
- Scope denials create no application-document metadata or upload/verify success audit rows.

Implemented checklist facts:
- Required application-stage checklist codes are `loan_application_form`, `borrower_pan`,
  `borrower_aadhaar_ovd`, `nominee_pan`, `nominee_aadhaar_ovd`, `share_certificate_copy`,
  `land_document_7_12`, `crop_plan`, and `six_month_bank_statement`.
- `cancelled_cheque` is accepted as application-document metadata but is not required for the
  application-stage checklist because source extracts place it before disbursement.
- Upload is limited to submitted applications, links an existing `DocumentFile` by UUID, and creates
  a new version row for duplicate document type/party combinations.
- Verification values are `pending`, `verified`, and `rejected`.
- Checklist refresh is read-derived under A-039; it writes no audit/workflow rows and does not
  persist checklist rows.

Sensitive-data boundary:
- Responses and audit metadata omit raw file bytes, storage keys, checksums, full PAN/Aadhaar/bank
  values, encrypted tokens, and hashes.
- Upload audit action: `applications.application_document.attached`.
- Verify audit action: `applications.application_document.verified`.

## Documentation Updates
- `docs/working/API_CONTRACTS.md` documents the 005D endpoints, request/response shape, permission
  checks, object-access order, version behavior, and audit boundaries.
- `docs/working/ASSUMPTIONS.md` has A-039 for read-derived checklist refresh.
- `docs/working/digests/epic-005-application-intake.md` records the implemented 005D facts.
- `005E` was sharpened to evaluate 005D's required checklist codes and call the existing reference
  generation service only after mandatory latest metadata is verified.

## Next Run
Run `005E-completeness-workbench`.

Key instruction for 005E: use the 005D checklist/application-document metadata and
`applications.services.evaluate_application_object_access(...)`. Do not duplicate document facts,
storage behavior, sequence generation, or loan request register writes. Completeness pass should
call `applications.services.generate_reference_after_completeness_pass(...)` only after all
mandatory latest checklist metadata is verified.

## Evidence
See `.ralph/runs/2026-07-09_200049_normal_run/`.

Key artifacts: `execution-plan.md`, `api-response-examples.md`, `review-packet.md`,
`risk-assessment.md`, `changed-files.txt`, `final-summary.md`, and gate logs under
`evidence/terminal-logs/`.
