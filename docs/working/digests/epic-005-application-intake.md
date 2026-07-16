# Epic 005 Digest: Application Intake, Completeness, and Deficiencies

## Architecture Review 2026-07-15 18:15 - Real Resubmission Evidence

008L3 correctly delegates the application change to the guarded application owner and keeps the
staff deficiency open. Its Playwright MP11 flow intercepts every API call, so it does not prove a
real session, upload, guard, resubmission, or queue return. In addition, workflow history advances
the immutable response to `submitted_for_review` while the borrower projection always reports
`responded`. Corrective 008L4 makes the real backend drive the browser proof twice and keeps the
response projection/history truthful without taking staff resolution authority.

## 008L3 Borrower Resubmission Closure (2026-07-15)

The portal process now resolves active portal-account/member/application scope once, locks the
returned application and every open response, requires a current immutable response for each item,
then delegates `incomplete_returned -> submitted` to the application-owned `resubmit` transition.
That owner invokes the 002H guard and writes the canonical
`applications.loan_application.resubmitted` audit plus loan-application workflow event while
resetting completeness to `not_started`. Invalid or repeated resubmission retains one success only.

The staff-owned deficiency remains `open` until 005F authority resolves it. Borrower upload,
re-upload, and resubmit workflow events instead target the immutable deficiency-response aggregate
and truthfully state `absent/responded -> responded -> submitted_for_review`; no shadow deficiency
state is claimed and no Stage-4 evidence changes.

## Architecture Review 2026-07-15 09:11 - Borrower Resubmission Lifecycle Closure

- 008L2 correctly self-scopes deficiency reads and replacement uploads, but its final resubmission
  directly assigns the application status rather than invoking the application-owned transition
  guard. The response also advances through `responded` and `submitted_for_review` while the
  authoritative deficiency row remains `open`, creating a second lifecycle vocabulary.
- Corrective `008L3` must cross the canonical returned-to-submitted application transition under
  lock, preserve the source completeness queue semantics, and expose one truthful response/
  deficiency state model. The regression contract patches the application transition evaluator
  and proves it is invoked, then verifies audit/workflow and zero-write denial behavior.
- Existing 005E4 staff completeness permissions and M03 coverage remain unchanged; portal
  resubmission must re-enter that existing completeness boundary without acquiring Stage-4 legal
  completion or approval authority.

## Architecture Review 2026-07-11 23:02 - 005E4 Verified Closure

- 005E4 uses the four source-defined completeness permissions for pass, return, resolve, and
  rejection-note creation in both projection and write boundaries. Permission-only, object/state,
  and zero-write denial assertions are substantive rather than coverage-only.
- The trusted routed-browser contract passed twice and produced all nine declared screenshots from
  the current run directory. M03-FR-010 through M03-FR-012 retain implemented confidence; this
  review found no new Epic 005 corrective work.

## 005E4 Completeness Action Authority and Browser Proof

- Completeness actions now use distinct source permissions end to end: pass uses
  `applications.loan_application.complete_check`, return uses
  `applications.loan_application.return_deficiency`, resolution uses
  `applications.deficiency.resolve`, and rejection-note creation uses
  `applications.rejection_note.create`. Each six-field projection evaluates object scope and the
  same state/resource functions as its public write boundary.
- Permission-only matrix coverage proves each action independently and proves all three ungranted
  mutations return the standard permission denial without state, reference, audit, workflow,
  register, deficiency, or rejection-note writes. Deputy Manager – Finance now receives the
  source-backed return permission in the canonical seed.
- The focused routed-container Playwright contract requires `RALPH_EVIDENCE_DIR`, asserts exact
  pass/return/resolve/reject bodies and one-call behavior plus canonical checklist/completeness/
  deficiency reloads, and captures queue-detail, pass, deficiency, returned, resolved, rejected,
  denied, stale, and API-error states. Local collection passes; trusted execution is an independent
  orchestrator gate because Chromium cannot acquire macOS services inside the agent sandbox.

## Architecture Review 2026-07-11 21:34 - Completeness Authority and Browser Closure

- 005E3 correctly joins authoritative document/completeness projections and restores S12's
  approved composition, but it assigns `applications.loan_application.complete_check` to pass,
  return, resolve, and rejection-note actions and endpoints. Source auth §§12.4/25.2/34.3 instead
  requires distinct `complete_check`, `return_deficiency`, `deficiency.resolve`, and
  `rejection_note.create` authority. Corrective 005E4 aligns projection and write gates and restores
  the full six-field action shape.
- 005E3's focused Playwright controller hard-codes its prior run path, never produced screenshots,
  and lacks promised denied/API-error states. 005E4 declares the trusted contract and all nine
  portable `RALPH_EVIDENCE_DIR` captures.
- 005FA4 is verified closed: the real App boundary covers unset/false/true flags, the staff demo
  selector no longer exposes borrower entry, and trusted login/logout acceptance passed twice.
- M03-FR-010 through M03-FR-012 remain backend-present, but completeness UI/authority confidence
  stays High risk until 005E4. Member deficiency resubmission remains owned by 008L2.

## 005FA4 Portal Auth Real-Boundary Flag Proof

- Unset, explicit-false, and true demo flags are now proven through module-isolated renders of the
  actual `App`/`RoleProvider` boundary, not a manually reconstructed `LoginScreen` projection.
- The true-flag red case found that the staff demo selector still offered a synthetic borrower and
  routed it into the portal. The selector now contains staff roles only; portal entry always uses
  the real credential/session path.
- The trusted Playwright contract derives both screenshot paths from `RALPH_EVIDENCE_DIR`, covers
  empty/populated login with one exact request, and captures the fail-closed post-logout state.

## 005E3 Completeness Authority and Fidelity Closure

- Completeness and deficiency reads now expose four §44-shaped resource actions: pass, return,
  resolve, and rejection-note creation. Their enabled states reuse the write services' permission,
  object-access, application-state, blocker, open-deficiency, duplicate-note, reference, and
  register gates; the React screen never builds a second action matrix.
- The workbench joins the document-checklist projection (submission/verification metadata) to the
  completeness projection (application/nominee/blocker/reference/workflow facts) by document type
  and fails closed on any ID, row-set, status, verification, or latest-document disagreement.
- Successful actions reload both status-filtered queues plus canonical checklist, completeness,
  and complete deficiency history. A 409 remains a one-shot mutation and refreshes only after the
  operator chooses Refresh.
- S12's category cards, progress bar, item rows, document chips, density, and action placement were
  restored with the existing visual vocabulary and real API facts only.

## Architecture Review 2026-07-11 19:23 - Completeness and Portal Proof Corrections

- 005E2 removed mock/reference/state authority and its API wrappers assert exact existing request
  contracts. However, the screen discards the `document-checklist` result, uses one global
  completeness permission plus local status facts for every mutation, and replaced the approved
  S12 category/item/document composition. 005E3 owns explicit two-projection authority, backend
  resource actions/service parity, restored prototype composition, and real-container proof for
  pass/return/resolve/reject/denial/validation/stale paths.
- 005FA3's default browser controller proves real empty/populated portal login and fail-closed
  network-error logout, but its unset/false/true flag unit test manually projects the flag into
  `LoginScreen`. 005FA4 must mount the real App/RoleProvider boundary in isolated flag states and
  successfully run/capture the browser acceptance evidence.
- Epic 005 is not complete. No M03 functional ID is newly closed by this review; completeness UI
  confidence awaits 005E3 and member deficiency resubmission remains 008L2.

## Architecture Review 2026-07-11 - Corrective UI/Auth Anchors

- 005E2 must consume the implemented 005D/005E/005F/005F2 APIs: the nine-document blocker list,
  backend-only reference generation, `incomplete_returned` status, no register/sequence advancement
  on deficiency return, and append-only deficiency history. M03-FR-010/S12 assign the review to
  Deputy Manager – Finance; the UI must not infer assignment from creator/receiver fields.
- The owner-applied 005FA2 code removes the portal demo fallback and defaults RoleContext to an
  unauthenticated user, but its static tests do not execute empty submission, demo-flag variants,
  or logout clearing. Corrective 005FA3 owns real DOM/session-boundary proof without visual changes.

## 005E2 Real-Data Workbench Closure

- The staff completeness queue requests only `submitted` and `incomplete_returned` rows from the
  staff list API. Selection loads the backend completeness projection and the complete deficiency
  history; no application/member/document mock or seeded deficiency remains.
- Completeness pass, return, resolution, and rejection-note creation use the exact existing 005E,
  005F/005F2, and 005H payloads, then re-read server state. The UI never generates a reference or
  advances a state locally.
- Until a future backend projection adds completeness resource `available_actions`, the UI uses
  the canonical `/auth/me` `applications.loan_application.complete_check` code only for action
  visibility. Object access and all business/state decisions remain backend-enforced.

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

## Member Portal Deficiency Response And Resubmission
- 008L2 closes MP11 through active-portal-account scoped deficiency list, strict replacement upload,
  authenticated current-content download, and atomic resubmission routes. Borrowers see only
  correction descriptions and current response metadata; staff remarks and identities remain hidden.
- Replacement PDF/JPEG/PNG evidence is limited to 5 MiB and the server-advertised KYC/legal/finance
  category plus confidential sensitivity. Central file storage and the next pending
  `ApplicationDocument` version make evidence visible to staff verification, while immutable response
  successor rows belong to `ApplicationDeficiency`; `PortalDocumentationSubmission` is never reused.
- Every open deficiency needs a current response before resubmission. Canonical storage returns
  `incomplete_returned` to source-defined `submitted` (A-095), resets completeness to `not_started`,
  and thereby reopens the existing Deputy Manager completeness queue. Portal audit/workflow facts and
  timeline presentation identify the action as resubmission.
- Cross-member attempts are nondisclosing and audited; suspended sessions, invalid type/size/category,
  partial response, and wrong-state attempts create no success evidence. A Stage-4 regression proves
  checklist status/actions/history, approvals, verifier/signature/remarks, legal/security evidence,
  readiness, loan-account, and disbursement truth remain untouched.

## Architecture Review 2026-07-10 01:01 - Portal Session And Audit Contract
- Reviewed slices 005F2, 005FA, 005FB, and 005G after prior architecture-review commit `49da479`.

## Rejection Note Shell
- 005H implements backend/API-only staff rejection-note metadata:
  - `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/`
  - `POST /api/v1/rejection-notes/{rejection_note_id}/send/`
- Source fields from `api-contracts.md` §21.3-§21.4 and `data-model.md` §13.6 are represented by
  `rejection_stage`, `rejection_reason_category`, `detailed_reason`, `reapply_allowed_flag`,
  `communication_mode`, `prepared_by_user`, optional approval/communication facts, and send actor
  timestamps. 005H adds `note_status = draft/sent` as the metadata-shell state.
- 005H uses the existing staff permission `applications.loan_application.complete_check` because no
  narrower source-backed rejection-note permission exists yet. Staff object access reuses
  `applications.services.evaluate_application_object_access(...)` after global permission and
  `404` checks. Same-permission actors outside scope receive `403 OBJECT_ACCESS_DENIED`.
- Borrower portal tokens cannot create or send staff rejection notes. Active portal tokens receive
  `403 PERMISSION_DENIED`; stale sessions for suspended portal accounts receive
  `401 INVALID_TOKEN` through the shared session validator before any rejection-note side effect.
- Create is limited to submitted applications with no `LO...` reference, no loan request register
  row, and no existing rejection note. Draft, `incomplete_returned`, reference-generated, and
  duplicate-create attempts return `409 INVALID_STATE_TRANSITION` and create no rejection note,
  success audit row, workflow event, register row, reference, or sequence advancement.
- Successful create writes `applications.rejection_note.created` metadata-only audit and a
  `rejection_note` workflow event into `draft`. Successful send writes
  `applications.rejection_note.sent`, stamps `sent_by_user`/`sent_at`, and records a workflow event
  from `draft` to `sent`.
- Send is a metadata/status transition only in 005H. It validates `recipient_email` but does not
  call a provider and does not create a `communications` row.
- A-045 records the status deferral: rejection-note creation leaves
  `LoanApplication.application_status = submitted` because the current source-backed intake status
  vocabulary has no generic rejected state yet. Future appraisal/sanction rejection slices must
  define when and how the application status changes.
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

## Architecture Review 2026-07-10 04:18 - Application Detail API State Hardening
- Reviewed slices 005G2, 005H, 005I, and 006A after prior architecture-review commit `353c6df`.
- 005I successfully moved Application List, New Application, and most Application Detail loading to
  staff APIs, but `ApplicationDetail.tsx` still contains a frontend-only `LO00000035` special case
  that can override real backend stage/document/owner/status display, plus hardcoded witness rows
  and hardcoded nominee sensitive placeholder values.
- 005I's own slice file requires Application Detail to show API-backed detail state, document
  checklist state, deficiency state, and 005H rejection-note state where an existing detail slot can
  support it. The current staff application detail serializer does not expose rejection-note metadata
  for the UI to render.
- Corrective slice `005I2-application-detail-api-state-hardening` must remove the hardcoded
  Application Detail state, render unavailable/empty states instead of synthetic person data, expose
  optional staff rejection-note summary on the detail response, and add backend/frontend regression
  tests proving a real `LO00000035` reference does not trigger mock status/document overrides.

## Application Detail API State Hardening
- 005I2 implemented the architecture-review correction. Staff application detail now serializes
  `rejection_note` as either `null` or a metadata-only summary with IDs, status/stage/category,
  reapply flag, actor IDs, timestamps, communication mode, and nullable communication ID.
- Staff detail omits rejection-note `detailed_reason`, leaves `application_status` backend-owned,
  and read-only detail access writes no success audit/workflow event.
- Borrower portal application detail continues to omit staff rejection-note metadata.
- `ApplicationDetail.tsx` no longer special-cases `LO00000035`, no longer forces
  `Sanctioned · Documentation Pending`, fixed document blocker counts, or Compliance/CS ownership,
  and no longer renders hardcoded witness rows or hardcoded nominee PAN/Aadhaar reveal values.
- Missing API-backed nominee/witness facts render neutral unavailable states using existing visual
  patterns.

## Architecture Review 2026-07-10 09:32 - Nominee And Detail Contract Gaps
- Source `api-contracts.md` §19.2 requires `nominee_id` on application create and §19.3 returns one
  selected nominee summary. The implemented member nominee API deliberately creates only reusable
  member-level nominees, `LoanApplication` stores no selected nominee, and no staff/portal request
  can populate `Nominee.loan_application_id`. Consequently, 006B's green eligible path currently
  depends on direct ORM fixture writes and silently chooses `.first()` if several reverse-linked
  rows exist. Corrective slice `005I3-application-nominee-selection-contract` must establish one
  explicit same-member application nominee through the public draft flows and make 006B use it.
- 005I2 removed the `LO00000035` branch and fake people, but Application Detail still inherits
  synthetic documentation/disbursement defaults, fixed stage dates/completion claims, hardcoded
  later-stage owner roles, and a frontend payment-readiness rule. Corrective slice
  `005I4-application-detail-backend-state-hardening` must render backend fields/actions or neutral
  absence and must test through the HTTP service seam rather than a production `initialData` prop.
- Epic 005 requirement-ID spot check: no parent epic transitioned to `Complete` in this review
  window. M03-FR-008/M03-FR-011/M03-FR-012 remain implemented; 005I3 explicitly owns the missing
  M03-FR-003 nominee selection and submit gate. Existing assumptions A-036/A-039-A-045 continue to
  own the documented partial/deferred intake behavior.

## Application Nominee Selection Contract
- 005I3 adds nullable, protected `LoanApplication.nominee` persistence so legacy drafts migrate
  safely while staff and portal create/update flows store source §19.2 `nominee_id`.
- A supplied nominee must belong to the application member, must not have `minor_flag = true`, must
  meet A-031's age-18 threshold, and must carry date-of-birth or age-snapshot evidence. Invalid
  selection paths write no application/audit/workflow success evidence.
- Submit and completeness/reference generation require the stored selection. Staff and own-member
  portal detail return only nominee ID/name/age/minor/KYC/relationship/signature metadata and never
  PAN/Aadhaar tokens, hashes, or values.
- 006B eligibility reads only `LoanApplication.nominee`; reverse-linked
  `Nominee.loan_application_id` rows and ordering cannot choose or change the assessed nominee.
  Legacy null selections remain `pending_manual_evidence`.

## Application Detail Backend State Hardening
- 005I4 adds persisted receiver/creator `assigned_owner` and §44-shaped `available_actions` to the
  staff detail response. The only current detail action is authorized, object-scoped draft submit;
  submitted and later-stage responses return an empty list until owning workflow APIs add actions.
- Application Detail now loads detail, checklist, and deficiencies through one production loader;
  its tests mock those HTTP service functions and render loading, success, and error states through
  the same loader/view boundary. The production-only `initialData` / `initialActiveTab` bypass is
  removed.
- The stepper remains wholly neutral because the detail DTO has no stage-history facts; the exact
  backend `current_stage` is shown separately as text. It no longer invents completion dates,
  review/verification claims, owner departments, SAP progress, disbursement progress, or payment
  readiness.
- Overview loan type and tenure render only when returned by the backend. Future eligibility,
  sanction, security, disbursement, and audit panels use the existing neutral unavailable pattern;
  checklist counts/rows remain direct presentations of API checklist items.
- Submitted and later-stage regressions assert two conflicting backend owner names win exactly.
  LO00000035, rejection-note, empty witness, and selected nominee metadata-only regressions now run
  through the HTTP loader/view seam; nominee PAN/Aadhaar labels, token/hash values, and reveal
  controls remain absent.

## Architecture Review 2026-07-10 15:46 - Ownership And Nominee Authority
- Reviewed 005I3/005I4 with the next Epic 006 corrections. Staff detail/list currently project
  `received_by_user or created_by_user` as `assigned_owner`, but neither field is a persisted
  assignment. A portal-created application can therefore display the borrower portal user as the
  internal staff owner. Corrective 005I5 requires neutral `assigned_owner = null` until the future
  assignment/task owner supplies a real fact.
- MP10 portal detail consumes the safe nominee DTO but omits nominee ID and minor/adult status.
  Selector tests do not exercise this page. 005I5 must render all safe 005I3 nominee facts while
  keeping PAN/Aadhaar values, hashes, tokens, and reveal controls absent.
- Staff and portal application forms independently calculate adult/minor status in React. This
  duplicates backend BR-009 authority and can drift. 005I5 removes the client calculations,
  centralizes the existing backend nominee decision for intake/completeness/eligibility, and adds
  invalid staff PATCH plus portal create/PATCH mutation-preservation tests.
- 005I4 loader/view tests contain useful assertions but split the production async controller from
  the rendered success/error/action path. 005I5 must test the actual production component with
  mocked HTTP using the existing E2E harness or a minimal pinned dev-only DOM test dependency.

## Application Ownership And Nominee Authority Hardening
- 005I5 makes `assigned_owner` neutral in staff list/detail. Receiver and creator remain intake/audit
  actors only; staff- and portal-created API regressions prove neither is projected as assignment.
- `applications.modules.nominee_validation.evaluate_nominee_selection` is the public BR-009 seam.
  Staff/portal draft mutation, submit, completeness/reference, and credit eligibility use the same
  unchanged same-member/adult/age-evidence decision and validation messages.
- Invalid staff PATCH and portal create/PATCH tests cover unknown, cross-member, minor, and missing-
  age-evidence nominees and prove serialized detail, selection, status, audit counts, and workflow
  counts are preserved.
- Staff and portal forms now require only the selected nominee ID as input shape and display backend
  `nominee_id` errors. React no longer computes age or minority.
- MP10 renders nominee ID, name, age snapshot, adult/minor state, KYC, relationship, and signature-
  required state while sensitive values and controls remain absent. Browser regressions cover the
  production staff controller and portal detail with mocked HTTP; local Playwright execution was
  blocked by the AFK sandbox's local-port restriction, so the orchestrator must execute them.
