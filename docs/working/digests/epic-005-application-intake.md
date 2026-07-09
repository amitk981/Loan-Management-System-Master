# Epic 005 Digest: Application Intake, Completeness, and Deficiencies

Sources distilled during slice `005A-loan-application-draft-create-update`:
- `docs/source/implementation-roadmap.md` §11
- `docs/source/api-contracts.md` §19.1-§19.4
- `docs/source/data-model.md` §13.1, §28, §30, §33.1
- `docs/source/auth-permissions.md` §12.4, §20.1, endpoint permission map
- `docs/source/screen-spec.md` S10
- `docs/source/screen-spec-member-portal.md` MP05, MP06, §11, §14.2

Additional sources distilled during slice `005B-application-submit-and-status-transition`:
- `docs/source/api-contracts.md` §19.5 plus audit/workflow examples in §42.
- `docs/source/api-contracts.md` §20.1-§20.3 and §27.1-§27.2 for application documents and
  checklist endpoints.
- `docs/source/data-model.md` `loan_application_status`, `loan_applications.submitted_at`,
  `application_documents` fields, and domain event table.
- `docs/source/auth-permissions.md` §12.4, §20.1, §36 endpoint map.
- `docs/source/screen-spec.md` S10 required documents/submission validations.
- `docs/source/screen-spec-member-portal.md` MP07/MP08 submission confirmation and MP10 status
  language.

## Draft Application Foundation
- Loan application creation must require an existing member. Data model stores
  `member_id`, borrower type snapshot, channel/date, requested amount, declared
  purpose, purpose category, status/stage, completeness status, terms flag, and
  actor timestamps.
- Slice 005A narrows the broader source contract to draft persistence only. It
  deliberately does not generate `LO...` reference numbers, submit, run
  completeness, verify documents, raise deficiencies, run eligibility, calculate
  limits, appraise, sanction, or disburse.
- S10 and MP05/MP06 require draft save/resume for member, requested loan facts,
  land/crop, bank metadata, and declarations. Required-field completeness
  blockers belong to submit/completeness slices.

## API Surface
- Source §19 defines:
  - `POST /api/v1/loan-applications/`
  - `GET /api/v1/loan-applications/{loan_application_id}/`
  - `PATCH /api/v1/loan-applications/{loan_application_id}/`
  - submit/check/deficiency endpoints for later slices.
- 005A implements create/read/update of draft facts only using the standard API
  success/error envelope.
- Draft responses include member identity and masked Epic 004 bank summaries.
  They must not serialize PAN, Aadhaar, full bank account numbers, encrypted
  token values, or hash columns.

## Validation And Permissions
- Permissions are source-backed:
  - Create: `applications.loan_application.create`
  - Read: `applications.loan_application.read`
  - Update draft: `applications.loan_application.update`
- Draft state can be edited by Field Officer, Deputy Manager, and Credit Manager
  once those role grants are applied through the catalogue.
- Validation for 005A:
  - Reject missing, malformed, unknown, or deleted borrower `member_id`.
  - Reject malformed land/crop/bank/cancelled-cheque UUIDs.
  - Reject land/crop/bank/cancelled-cheque references that do not belong to the
    selected member.
  - Reject non-positive requested amount when supplied.
  - Allow incomplete KYC/documents at draft save time.

## Audit And Workflow
- Critical application create/update actions require audit rows.
- Audit metadata must be metadata-only and must not include full sensitive
  identifiers, token values, or hashes.
- Existing workflow-event foundation can record the draft-created state without
  inventing submit/completeness transitions. Draft updates should not create
  extra workflow transitions unless a source-backed state change occurs.

## Submit Transition Foundation
- Canonical first submitted status is `submitted`.
- Source permission is `applications.loan_application.submit`; state permission table allows draft
  edit/upload/submit for Field Officer, Deputy Manager, and Credit Manager. The endpoint map lists
  `POST /loan-applications/{id}/submit/` with this permission.
- 005B owns only `draft -> submitted`. It preserves `current_stage =
  initial_loan_request`, keeps `completeness_status = not_started`, and does not generate
  `LO...` references. The portal copy says the reference number is received after submitted
  details/documents are checked.
- 005B submit requires the persisted S10/MP06 loan request facts: member, positive requested amount,
  declared purpose, and purpose category. Nominee, document placeholders, completeness check,
  deficiencies, eligibility, appraisal, sanction, disbursement, and payment initiation remain later
  slices.
- Successful submit should stamp submitted actor/time, lock direct draft edits, write
  metadata-only `applications.loan_application.submitted` audit, and write a `loan_application`
  workflow event from `draft` to `submitted`.

## Application Documents And Checklist
- Source application-document endpoints:
  - `GET /api/v1/loan-applications/{loan_application_id}/application-documents/`
  - `POST /api/v1/loan-applications/{loan_application_id}/application-documents/`
  - `POST /api/v1/application-documents/{application_document_id}/verify/`
  - `GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`
  - `POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`
- Upload fields: `document_type`, `party_type`, optional `party_id`, `file`, and optional
  `remarks`. Party types are borrower/nominee/witness. Verification request carries
  `verification_status` and `remarks`.
- Data model fields for application documents include loan application FK, document type, party
  type/ID, document file FK, required flag, submission status, verification status, verifier
  actor/time, and remarks.
- Required application-stage documents from source: loan application form, borrower PAN, borrower
  Aadhaar/OVD for individual borrowers, nominee PAN, nominee Aadhaar/OVD, share certificate copy,
  land document / 7/12 extract, crop plan, and six-month bank statement. Cancelled cheque may be
  collected at application stage but is explicitly required before disbursement, so it should not
  block the 005D application checklist unless the source pass finds stronger language.
- Document statuses in the portal are `Not Uploaded -> Uploaded -> Under Review -> Accepted /
  Rejected / Re-upload Required`; backend verification vocabulary can map these to pending /
  submitted / verified / rejected metadata without exposing sensitive values.
- Duplicate document types should create a new version/history row or a standard duplicate-state
  error, but must not overwrite audit history.
