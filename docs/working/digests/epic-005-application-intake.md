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

## Reference Generation And Loan Request Register
- Source trigger confirmed in 005C: the official `LO00000001` sequence is assigned after
  completeness check passes, not at draft creation or submit. Evidence:
  `screen-spec.md` §4.4 says assigned after completeness check, S12 says generate reference when
  all mandatory completeness checks pass, and member portal MP08 says the borrower receives the
  reference number after submitted details/documents are checked.
- 005C implements a narrow backend action:
  `POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`. It represents the
  successful completeness-pass point but does not implement checklist evaluation, nominee gates,
  document verification, deficiencies, eligibility, appraisal, sanction, disbursement, or frontend
  wiring.
- Permission is source-backed `applications.loan_application.complete_check`.
- Generation is limited to submitted applications. Draft or duplicate generation attempts return
  a standard invalid-state error and must not create extra register rows, audit rows, workflow
  events, or sequence-visible application references.
- The sequence table is `system_sequences` with code `loan_application_reference`, prefix `LO`,
  current value, 8-digit padding, and last generated value. References start at `LO00000001`.
- Successful generation sets `application_reference_number`, marks completeness `complete`, moves
  the stage to `credit_assessment`, writes metadata-only audit/action evidence, records a workflow
  event from `submitted` to `reference_generated`, and creates exactly one
  `loan_request_register_entries` row linked one-to-one to the application.
- Register rows are sourced from existing application/member facts and must not copy PAN, Aadhaar,
  full bank account values, protected token values, or hashes.
- A-037 records the source mismatch that S12 names `Reference Generated` as the application status
  while the data-model enum table omits that value.

## Application Documents And Checklist
- Architecture review `2026-07-09_190655_architecture_review` extracted application object-access
  requirements before 005D: `auth-permissions.md` §19.2 scopes Field Officers to created/assigned
  applications, Deputy Manager Finance to credit-assessment queue/assigned applications, and Credit
  Manager to the credit-assessment domain. The endpoint map marks
  `GET /loan-applications/{id}/` as `applications.loan_application.read` plus object access, and
  §37.3 says a Field Officer viewing an unrelated application must be denied. Corrective slice
  005C2 should integrate the existing 002I object-access helper for application detail/actions
  before document/checklist and completeness slices build on those endpoints.
- 005C2 implemented the application object-access boundary for detail, patch, submit, and
  reference generation. Current source-backed owner facts are `LoanApplication.created_by_user` and
  `received_by_user`; Credit Manager role-code access is allowed only when
  `current_stage = credit_assessment`. Same-permission users outside those scopes receive
  `403 OBJECT_ACCESS_DENIED` after the global permission and `404` checks. Denials create no
  update/submit/reference success audit, workflow event, register row, application reference, or
  visible sequence advancement. Future 005D/005E endpoints must reuse
  `applications.services.evaluate_application_object_access(...)` instead of reimplementing scope.
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
- 005D implemented `application_documents` metadata rows with UUID PK, loan application FK,
  document type, party type/ID, linked `documents.DocumentFile`, required flag, submission status,
  verification status, verifier actor/time, remarks, version number, and actor timestamps.
- Implemented endpoints:
  - `GET/POST /api/v1/loan-applications/{loan_application_id}/application-documents/`
  - `POST /api/v1/application-documents/{application_document_id}/verify/`
  - `GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`
  - `POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`
- 005D permission/order facts: list/checklist/refresh require
  `applications.loan_application.read`; upload requires `applications.document.upload`; verify
  requires `applications.document.verify`. Unknown applications/document metadata return
  `404 NOT_FOUND`; missing global permission returns `403 PERMISSION_DENIED`; application scope
  uses `applications.services.evaluate_application_object_access(...)` and out-of-scope
  same-permission actors receive `403 OBJECT_ACCESS_DENIED` with no metadata/audit writes.
- 005D upload is limited to submitted applications and links existing document files by UUID; it
  does not duplicate file bytes or change storage behavior. Duplicate document type/party uploads
  create a new version row, preserving prior audit facts.
- 005D checklist is derived from required application-stage document codes and current latest
  application-document metadata. `cancelled_cheque` is accepted as upload metadata but is not part
  of the required application checklist because the source places it before disbursement.
- 005D audit actions are `applications.application_document.attached` and
  `applications.application_document.verified`. Audit payloads are metadata-only and omit raw file
  bytes, storage keys, checksums, full PAN/Aadhaar/bank values, encrypted tokens, and hashes.
- A-039 records that checklist refresh is read-derived until a future source-backed completeness
  slice defines persisted checklist side effects and a narrower mutation permission.

## Completeness Workbench And Pass
- 005E implements backend/API-only completeness workbench endpoints:
  - `GET /api/v1/loan-applications/{loan_application_id}/completeness-check/`
  - `POST /api/v1/loan-applications/{loan_application_id}/completeness-check/pass/`
- Workbench read requires `applications.loan_application.read`; pass requires
  `applications.loan_application.complete_check`. Both endpoints preserve the 005C2 object-access
  boundary after global permission and `404` checks. Same-permission actors outside object scope
  receive `403 OBJECT_ACCESS_DENIED` with no sequence/register/audit/workflow writes.
- The workbench is derived from the 005D checklist/application-document metadata. It returns
  application summary facts, required checklist item statuses, `blocking_document_types`, and
  `can_generate_reference`.
- Completeness pass first enforces source-backed state: only submitted, non-reference-generated
  applications without a loan request register entry can pass. Draft and duplicate/reference
  attempts return `409 INVALID_STATE_TRANSITION`.
- Completeness pass then evaluates the latest 005D metadata row for each mandatory document code:
  `loan_application_form`, `borrower_pan`, `borrower_aadhaar_ovd`, `nominee_pan`,
  `nominee_aadhaar_ovd`, `share_certificate_copy`, `land_document_7_12`, `crop_plan`, and
  `six_month_bank_statement`. Only `submission_status = submitted` and
  `verification_status = verified` is complete. Missing latest metadata is reported as
  `missing_metadata`; pending or rejected latest metadata is reported as `not_verified`.
- Failed completeness validation returns `400 VALIDATION_ERROR` with item-level document codes and
  creates no sequence, register, reference, audit, or workflow side effects.
- Successful completeness pass delegates to the existing 005C
  `generate_reference_after_completeness_pass(...)` service, which generates the `LO...` reference,
  creates the one-to-one loan request register entry, sets completeness complete, moves the
  application to credit assessment, and writes the existing metadata-only audit/workflow evidence.
- 005E deliberately does not persist deficiency rows, create rejection notes, run eligibility,
  calculate loan limits, create appraisal notes, or build frontend/member-portal deficiency
  response screens.

## Deficiency Creation And Resolution
- 005F implements backend/API-only deficiency endpoints:
  - `POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/`
  - `GET /api/v1/loan-applications/{loan_application_id}/deficiencies/`
  - `POST /api/v1/deficiencies/{deficiency_id}/resolve/`
- The return action requires `applications.loan_application.complete_check`; list requires
  `applications.loan_application.read`; resolve requires
  `applications.loan_application.complete_check`. All preserve the 005C2 application object-access
  boundary after global permission and `404` checks.
- Return-with-deficiencies is limited to submitted, non-reference-generated applications without a
  loan request register row. Draft/reference-generated attempts return
  `409 INVALID_STATE_TRANSITION`.
- 005F creates structured `deficiencies` rows only from current 005E blocking checklist facts.
  Request `items[].item_code` must match a blocking required document code; arbitrary codes, empty
  selections, duplicate items, unknown fields, or missing communication mode/message return
  `400 VALIDATION_ERROR`. A-040 records the request-shape decision because the source §19.7 example
  assumes deficiency IDs already exist.
- Source reason mapping: `missing_metadata` becomes `deficiency_type = missing_document`;
  `not_verified` becomes `deficiency_type = not_verified`.
- Successful return originally kept `application_status = submitted`; corrective slice 005F2
  hardens this to the source-backed returned state. It now sets `application_status =
  incomplete_returned`, keeps `current_stage = initial_loan_request`, sets `completeness_status =
  incomplete`, creates open deficiency rows with raised actor/time and communication metadata,
  writes `applications.loan_application.returned_with_deficiencies` audit metadata, and records a
  `loan_application` workflow event from `submitted` to `incomplete_returned`. It does not generate
  a reference, create a loan request register row, move to credit assessment, or advance the visible
  sequence.
- Deficiency resolve uses the source §21.2 `resolution_notes` request, closes only open rows with
  resolver actor/time, writes `applications.deficiency.resolved` audit metadata, and records an
  `application_deficiency` workflow event from `open` to `resolved`.
- Borrower portal response drafting, document re-upload UI, application resubmission back to
  completeness check, rejection notes, and real communication delivery remain later slices.

## Architecture Review 2026-07-09 21:38 - Deficiency Return Status Contract
- Reviewed slices 005C2, 005D, 005E, and 005F after commit `1f30ed6`.
- Source status facts opened for this review:
  - `docs/source/data-model.md` `loan_application_status` includes `incomplete_returned`.
  - `docs/source/functional-spec.md` M03 deficiency flow says an incomplete application enters the
    incomplete state and keeps deficiency history.
  - `docs/source/screen-spec.md` S12 says returned applications become
    `Incomplete - Returned to Applicant` or rejected, depending on business decision.
- 005F currently stores returned applications as `application_status = submitted` plus
  `completeness_status = incomplete`. That hides the returned state from downstream portal/status
  slices. Corrective slice 005F2 should set `application_status = incomplete_returned`, keep
  `completeness_status = incomplete`, and preserve the existing no-reference/no-register/no-sequence
  side-effect guarantees.
- 005F2 implemented that correction. Source docs do not define repeat returns from
  `incomplete_returned`, so repeat return attempts remain blocked with `409 INVALID_STATE_TRANSITION`
  and create no duplicate deficiency rows, success audit/workflow events, register rows, references,
  or visible sequence advancement.

## Member Portal Authentication
- 005FA implements MP00/MP01/MP02/MP25 portal authentication foundation:
  activation start/complete, portal login, password-reset start/complete, and portal password
  change.
- Source MP01 requires member identity/contact verification plus OTP before setting a portal
  password. The implementation links one `PortalAccount` to one `Member` and one
  `borrower_portal_user` auth user.
- Borrower access tokens and `/auth/me` responses include `member_id`,
  `portal_account_id`, and `portal_role = borrower_member`. They expose only portal own-data
  permission codes such as `portal.loan_application.read_own`; they do not grant staff
  `applications.loan_application.complete_check`, deficiency return, or register permissions.
- Password reset OTPs are single-use and revoke all active sessions on success. MP25 password
  change keeps the current session active and revokes other sessions.
- OTP delivery remains behind the 003I communication-shell boundary with no real provider call.
  A-042 records the delivery-channel and last-four verification assumptions.

## Member Portal Dashboard, Profile, And Supply View
- 005FB implements MP03/MP04 and prototype `MP22_ProduceSupply.tsx` as authenticated portal
  own-data reads:
  - `GET /api/v1/portal/dashboard/`
  - `GET /api/v1/portal/profile/`
  - `GET /api/v1/portal/produce-supply/`
- Source MP03 requires member summary, pending actions, application/loan summary, repayment shell,
  notices, and quick actions. 005FB returns implemented application counts and open-deficiency
  pending-action counts; loan, signature, repayment, KYC-update, closure, and notices stay zero/empty
  shells until their modules exist.
- Source MP04 requires own-only member/contact/nominee/shareholding/land/crop/bank/KYC profile
  visibility. 005FB reuses existing Epic 004 serializers and forces PAN/Aadhaar/full bank values to
  masked-only portal display with no reveal path.
- `data-model.md` defines `produce_supply_records`, but no Django model exists yet. A-043 records
  the empty read-only produce-supply shell until that persistence slice exists.
- Staff tokens and non-portal users receive `403 PERMISSION_DENIED` on portal own-data APIs. Query
  `member_id` values are ignored as authority; the linked active `PortalAccount.member_id` is the
  only scope.

## Member Portal Application Start And Status
- 005G implements MP05/MP09/MP10 application start, own list, and own status detail:
  - `GET/POST /api/v1/portal/applications/`
  - `GET/PATCH /api/v1/portal/applications/{loan_application_id}/`
  - `POST /api/v1/portal/applications/{loan_application_id}/submit/`
- Source MP05/MP06/MP08 require borrowers to create/save/resume a draft and submit it to SFPCL.
  Source MP09/MP10 require own application list/status with pending owner, lifecycle stage,
  deficiencies, next steps, and no edit after submit unless returned.
- Portal application scope is only the active `PortalAccount.member_id`. Payload/query/path
  `member_id` cannot broaden authority. Staff/non-portal tokens receive `403 PERMISSION_DENIED`;
  cross-member existing application attempts receive `403 OBJECT_ACCESS_DENIED` with no create,
  audit, workflow, register, reference, or sequence side effects.
- The portal endpoints reuse the 005A/005B draft/update/submit services. Submit still requires
  own member, positive requested amount, declared purpose, and purpose category. Draft save may
  remain incomplete.
- Submitted applications can appear without an `LO...` reference; reference generation remains
  staff completeness-pass behavior from 005C/005E.
- Returned applications serialize borrower rectification state as
  `application_status = incomplete_returned`, `completeness_status = incomplete`,
  `current_stage = initial_loan_request`, `pending_with = Borrower`, open deficiency count, and
  open deficiency metadata. Deficiency response/re-upload/resubmission remains out of scope.
- Portal responses intentionally omit staff completeness/reference/return/resolve actions, PAN,
  Aadhaar, full bank-account values, encrypted values, token hashes, raw document contents, and
  staff-only document internals.

## Architecture Review 2026-07-10 01:01 - Portal Session And Audit Contract
- Reviewed slices 005F2, 005FA, 005FB, and 005G after prior architecture-review commit `49da479`.
- Source portal login/access facts opened for this review:
  - MP00 says inactive/suspended portal users are blocked.
  - §14.1 says inactive or unauthorised portal accounts are blocked.
  - §11 names portal-specific audit events including `portal.login.success`,
    `portal.login.failed`, `portal.account.activated`, `portal.application.draft_created`,
    `portal.application.saved`, `portal.application.submitted`, and `portal.password.changed`.
- 005FA blocks suspended portal accounts at fresh login, and 005FB/005G portal data routes require
  an active `PortalAccount` for their own-data scope. However, `/auth/me` and token/current-user
  payload construction still add portal member claims for any linked portal account regardless of
  `PortalAccount.status`; password-change also checks only that a portal account relation exists.
  Corrective slice 005G2 should add a shared portal-session validity boundary and revoke/block old
  sessions once the portal account is no longer active.
- 005FA/005G audit rows currently use implementation names such as
  `portal.auth.login.succeeded`, `portal.auth.activation.completed`,
  `portal.auth.password_changed`, and reused internal `applications.loan_application.*` actions for
  borrower portal draft/create/submit. Corrective slice 005G2 should align borrower portal audit
  actions with the source portal event names while preserving existing internal staff audit action
  names for staff routes.

## Member Portal Session And Audit Contract Hardening
- 005G2 implemented the architecture-review correction. A shared session-bound portal authority
  check now rejects already-issued access/refresh sessions when the linked `PortalAccount` is no
  longer active or the linked member is deleted. It revokes the `UserSession` with
  `revoked_reason = portal_account_status_changed` and returns `401 INVALID_TOKEN` through the
  existing auth helper semantics. A-044 records this route-level status decision.
- `/api/v1/auth/me/`, portal password change, portal dashboard/profile/produce-supply, and portal
  application routes no longer expose portal `member_id`, `portal_account_id`, `portal_role`, or
  portal own-data permissions after account suspension. Denied suspended-session portal application
  attempts create no application, portal application audit row, workflow event, register row,
  reference, or visible sequence side effect.
- Portal auth/action audit names now match the source member-portal audit table:
  `portal.account.activated`, `portal.login.success`, `portal.login.failed`,
  `portal.password.changed`, `portal.application.draft_created`,
  `portal.application.saved`, and `portal.application.submitted`.
- Staff application routes keep the internal audit action names
  `applications.loan_application.created`, `applications.loan_application.updated`, and
  `applications.loan_application.submitted`; the portal-specific names are passed only by borrower
  portal route services.
- New tests prove portal audit payloads remain metadata-only and do not include PAN, Aadhaar, full
  bank account values, OTP values, token hashes, passwords, encrypted values, or raw document data.
