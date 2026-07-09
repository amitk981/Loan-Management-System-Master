# Epic 005 Digest: Application Intake, Completeness, and Deficiencies

Sources distilled during slice `005A-loan-application-draft-create-update`:
- `docs/source/implementation-roadmap.md` §11
- `docs/source/api-contracts.md` §19.1-§19.4
- `docs/source/data-model.md` §13.1, §28, §30, §33.1
- `docs/source/auth-permissions.md` §12.4, §20.1, endpoint permission map
- `docs/source/screen-spec.md` S10
- `docs/source/screen-spec-member-portal.md` MP05, MP06, §11, §14.2

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
