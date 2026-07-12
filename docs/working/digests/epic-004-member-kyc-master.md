# Digest — Epic 004: Member, KYC, Nominee, Witness, and Profile Master

## Architecture Review 2026-07-12 - Registry/Witness Residual Closures

- 006Y8 replaces the generic witness `update` action with exact `correct_contact` and
  `correct_identity` six-field actions. Projection and PATCH share permission, application scope,
  maker-checker, and version evaluation; the original verifier retains contact correction but sees
  the identity action disabled with the write's verbatim reason. The routed browser contract uses
  real finance/checker sessions and owns three canonical-reload screenshots.

- 006Y7 makes identity-approval projection/write consume the Registry's one complete permission,
  object-scope, requester-checker, request/member-version, pending-state, and KYC evaluation. The
  serializer only translates the Registry's exact six-field action; it no longer imports back into
  the Registry. PostgreSQL duplicate-create and competing-approval races pass twice with one winner,
  one field-validation loser, and exact member/request/history/audit cardinality.

- 006Y5 completed the §13.2 fields and public Registry facade but did not execute its required
  PostgreSQL duplicate-create/identity-approval races. Identity approval projection also omits the
  member object-scope check performed by the write. 006Y7 owns one full evaluation plus concurrent
  one-winner/standard-duplicate proof.
- 006Y5's form tests mock API wrappers and provide no real-session/screenshots for complete
  individual/institution registration or identity approval. 006Y9 owns mounted and trusted-browser
  canonical readback, masking, and `400`/`403`/`409` proof.
- 006Y6 persisted S09 address/mobile and protected correction history, but its generic Update action
  ignores the identity maker-checker check enforced by the write; the slice also omitted its required
  real browser flow. 006Y8 owns contact/identity-specific authority parity and routed screenshots.

## Architecture Review 2026-07-12 - Member Governance Correctives

- Codebase design §10.1 requires member writes behind `members.modules.member_registry`, including
  duplicate PAN rejection. 006Y placed them in generic services, did not check duplicate PAN/Aadhaar,
  and left malformed nested-profile/integrity edges outside complete standard-envelope tests.
- M02-FR-012 says verified identity changes require an approved change request. A-065's reason-only
  reverification intentionally lacks that approval fact, so 006Y3 adds a persisted request and
  separate permission-based checker approval without hard-coding an approver role.
- 006Y change history omits nested create values and records `null` for address old values. 006Y3
  owns complete masked field diffs, duplicate races, deep-module authority, full §13.2 forms, and
  routed/browser mutation proof.

## 006Y5 Member Registry Closure

- `MemberRegistry` is the public create/update/detail/request/approve seam. It evaluates exact
  permissions and the existing global member-object fallback internally; HTTP views only translate
  module results to standard envelopes.
- Proposed PAN/Aadhaar values are duplicate-checked at request and approval time. Database
  uniqueness failures are translated to field validation inside the atomic workflow, so member,
  request status, history, and audit evidence roll back together.
- Identity approval actions and writes share the requester/checker, pending-state, member-version,
  KYC-state, and permission evaluation. A requester with checker permission sees the same disabled
  maker-checker reason returned by the write.
- The staff registration modal now sends every API §13.2 individual and institution profile field;
  successful mutations retain canonical server refetch behavior and protected identifiers remain
  masked outside immediate write payloads.
- 006Y2 requires witness edit but delivered GET/POST only under A-066. 006Y4 owns versioned audited
  correction, immutable 004E2 evidence, resource actions, canonical refetch, and mounted/browser
  `400`/`403`/`409` proof.

## 006Y Member Identity Governance

- §13.2 member create persists individual or institution profiles and protects PAN/Aadhaar and
  institutional signatory identifiers with the existing token/hash boundary. Every create writes
  masked change history and metadata-only audit evidence.
- Ordinary member PATCH is optimistic (`version` required). Verified PAN/Aadhaar is locked; a
  reasoned reverification action is the only correction route and atomically resets KYC to pending.
- Member detail projects six-field update/reverification actions from the same permission and KYC
  predicates used by writes. Stale/denied writes preserve member/history/KYC/audit counts, except
  the required metadata-only locked-identity rejection audit.
- Member creators/editors cannot verify that member's KYC documents; verifier separation is
  enforced at the backend verification action.

## 006Y2 Member and Witness UI Closure

- Staff member registration supports individual and institution variants through the 006Y create
  endpoint. Profile update and reasoned identity reverification send the current member version and
  refetch canonical detail instead of locally merging mutation responses.
- Verified identity values render masked and read-only. Only the resource's
  `members.member.update` and `members.member.reverify_identity` actions expose profile controls;
  backend validation, permission, identity-lock, and stale-write results remain authoritative.
- Application Detail reads/captures witnesses through the 004E2 application-scoped GET/POST seam,
  then refetches immutable verification-time shareholding and folio evidence. The delivered contract
  has no update endpoint; A-066 records why edit is not invented client-side.

## Architecture Review 2026-07-11 - 004E Witness Hardening

- 004E's successful shareholder/KYC/name/masking/audit behavior is substantive, but malformed or
  non-object JSON can escape because the adapter does not translate `parse_json_body`'s Django
  `ValidationError`.
- The qualifying folio is written only to the creation audit. `Witness` stores no shareholding FK
  or folio snapshot, and GET reselects current shareholdings, so later mutations can rewrite the
  displayed verification basis. Automatic FK/`db_index` indexes are also duplicated by explicit
  `Meta.indexes`.
- Corrective 004E2 owns standard malformed-body envelopes, immutable shareholding/folio evidence,
  conservative legacy backfill, stable-read tests, a thin application-owned query seam, and
  redundant-index cleanup. M02-FR-009/BR-010 is not fully closed until it lands.

## 004E2 Witness Evidence Hardening

- New witness creation snapshots the exact qualifying shareholding UUID and folio; list/create
  responses use only that verification-time evidence and do not reselect current holdings.
- Legacy backfill requires one creation-audit folio and exactly one matching shareholding for the
  witness member. Missing, conflicting, or ambiguous evidence stays nullable rather than guessed.
- Malformed JSON and non-object bodies return `400 VALIDATION_ERROR` without witness/audit/workflow
  writes. Witness list query plus serialization composition now lives behind the application
  service seam.
- The named application, PAN-hash, and Aadhaar-hash indexes remain exactly once; their redundant
  automatic FK/`db_index` companions are removed.

Source extracts opened incidentally during 003K queue sharpening. `docs/source/` remains
authoritative; the 004A run must still read the full Epic 004 file and named source references
before implementation.

## Member Directory Initial Extracts
- `docs/source/api-contracts.md` §13.1 defines
  `GET /api/v1/members/?search=&member_type=&membership_status=&kyc_status=&default_status=&page=1&page_size=20`.
- The §13.1 response item includes `member_id`, `member_number`, `member_type`, `legal_name`,
  `display_name`, `folio_number`, `membership_status`, `kyc_status`, `rekyc_due_date`,
  `default_status`, `mobile_number`, `email`, `share_summary{number_of_shares, holding_mode,
  available_share_count}`, and `active_member_status{status, verified_at}`.
- The same excerpt shows `mobile_number` masked in the example. 004A should preserve masking and
  avoid exposing sensitive identifiers through the directory response unless the full source pass
  confirms role-specific reveal rules.
- 004A source pass confirmed `auth-permissions.md` §12.2 and §25.1 use `members.member.read` for
  listing members; `/members` route guard also maps to `members.member.read`. Directory reads are
  scope-limited in source language, but no exact object-scope rule exists yet, so 004A blocks users
  without the permission and does not expose all records to unauthenticated/unauthorised users.
- `api-contracts.md` §6.2 and §7 require standard list pagination and `VALIDATION_ERROR` envelopes.
  004A validates only §13.1 query parameters: `search`, `member_type`, `membership_status`,
  `kyc_status`, `default_status`, `page`, and `page_size`; unknown parameters return 400.
- Sharpened 004A as a read-only, paginated member-directory endpoint/UI wiring slice. It should not
  implement member create/update, KYC verification, nominee, witness, share certificate, demat,
  landholding, crop plan, loan application, or borrower 360 behavior.

## Member Profile and KYC Extracts Opened During 003L
- `docs/source/implementation-roadmap.md` §11.2 scopes R2 member master, nominee/witness,
  shareholding, land/crop, KYC, loan application, completeness, eligibility, loan limit, appraisal,
  and credit queues. 004A/004B should stay in the member directory/profile foundation and not pull in
  loan application, eligibility, loan-limit, or appraisal behavior.
- `implementation-roadmap.md` §11.4 names Member Directory and Member Profile as R2 frontend stories;
  §11.6 says QA must cover member validation, KYC upload/masking, nominee minor rejection, witness
  shareholder validation, and related flows in their owning slices.
- `docs/source/api-contracts.md` §13.3 defines `GET /api/v1/members/{member_id}/` with masked PAN
  and Aadhaar objects shaped as `{masked, can_view_full}`, registered address, KYC/default status,
  profile shell fields, and object-level `available_actions[]`.
- `api-contracts.md` §13.5 defines `POST /api/v1/members/{member_id}/reveal-sensitive-field/` with
  a required `field_name` and `reason`, full value expiry, sensitive-data permission, mandatory audit
  logging, and no frontend caching of full values.
- `api-contracts.md` §14-§18 define nominee, shareholding, active-member, land/crop, and KYC
  endpoints. 004B should not implement those mutation/calculation/upload/verify endpoints unless its
  slice is explicitly widened; it may show profile placeholders only if backed by implemented data.
- `docs/source/data-model.md` §10.1 defines `members` fields including encrypted/hash PAN and
  Aadhaar, contact fields, KYC/default status, `active_member_status_id`, primary bank account, and
  standard audit columns. Member number is nullable/unique when available; folio number is required.
- `data-model.md` §10.2-§10.3 separate individual farmer profiles from FPC/producer institution
  profiles. 004B should keep profile serialization explicit by member type and not force both
  profile shapes for every member.
- `data-model.md` §11-§12 define shareholding, active-member, land/crop, KYC, bank-account, cancelled
  cheque, and bank-verification-letter tables. These are future target areas after 004A/004B unless a
  slice explicitly owns each table/API.
- `data-model.md` §28-§29 require referential integrity, PAN/Aadhaar/bank masking, encrypted
  sensitive columns, hash columns for duplicate/search, and last-4 masking rules.
- `docs/source/screen-spec.md` S05 lists Member Directory columns and filters, including member
  ID/folio/name/type, active status, shares, holding mode, produce supply, services availed, default,
  KYC, open loans, last updated, and filters for member type, active, shareholding mode, KYC, default,
  crop, land range, producer institution, and subsidiary-linked borrower. 004A should implement only
  the filters in §13.1 unless it also implements source-backed fields for the additional filters.
- `screen-spec.md` S06 defines Member Profile tabs for overview, shareholding, produce supply,
  services, KYC, land/crop, loans, nominee, communications, and audit trail. 004B should use the
  existing prototype layout but must not keep mock-only data on backend-wired paths.
- `screen-spec.md` S17 says KYC verification covers borrower, nominee, witness, CKYC consent,
  re-KYC, and risk rating. PAN and Aadhaar are required before appraisal completion, but 004B must
  not invent appraisal blockers or CKYC policy behavior.

## 004B Repair Extracts
- 004B implements only `GET /api/v1/members/{member_id}/` from `api-contracts.md` §13.3 with
  masked `pan`/`aadhaar` objects, registered address, nullable type-specific profile shell objects,
  and `available_actions[]`.
- §13.5 sensitive reveal remains deferred: no full values, no reveal controls, and
  `can_view_full: false` in the 004B response.
- `auth-permissions.md` maps member detail to `members.member.read` plus object access; exact
  object-scope facts are still unmodeled, so 004B gates by `members.member.read` and records A-030.
- Future slices should add object-scope enforcement only when source-backed member/team ownership
  facts exist.

## 004C Profile Detail Extracts
- `data-model.md` §10.2 requires individual-profile first/last name and permits nullable middle
  name, gender, date of birth, occupation, and employment/service years. One row belongs only to
  an `individual_farmer`.
- §10.3 requires producer/FPC institution type and authorised-signatory name; registration number,
  produce-supply years, and sensitive signatory identifiers are nullable. One row belongs only to
  an `fpc` or `producer_institution`.
- 004C returns the remaining individual fields and the existing non-sensitive producer fields from
  `GET /api/v1/members/{member_id}/`. Missing type-specific rows remain `null`.
- Signatory PAN/Aadhaar remain deferred because §13.5 requires reason capture, expiry, audit, and
  no frontend caching. They are neither stored nor serialized by 004C.
- `api-contracts.md` §14.1-§14.3 define nominee list/create plus minor, required PAN/Aadhaar, and
  identity-format errors. `data-model.md` §10.4 requires encrypted/hash identity storage,
  `minor_flag = false`, and nominee signatures; `auth-permissions.md` maps reads to
  `members.nominee.read` and creates to `members.nominee.create`.
- `data-model.md` §10.5 says a witness belongs to a loan application, must be an existing SFPCL
  shareholder, needs KYC, and signs the Loan Agreement/SH-4 where applicable. Because 004E follows
  nominee work but precedes application/shareholding persistence, it must not invent a standalone
  witness endpoint or fake shareholder verification.

## 004D Nominee Extracts
- 004D implements `GET`/`POST /api/v1/members/{member_id}/nominees/` from `api-contracts.md`
  §14.1-§14.3 as member-level nominee list/create only. Application-specific snapshot behavior
  remains deferred; `loan_application_id` is nullable storage and is not accepted by the API.
- `data-model.md` §10.4 fields now exist in `nominees`: member FK, nullable application UUID,
  nominee name, DOB, age snapshot, gender, relationship, protected PAN/Aadhaar token storage plus
  keyed hashes, `kyc_status`, `minor_flag`, signature-required flag, and timestamps.
- `auth-permissions.md` §12.2 and endpoint map split read/create permissions:
  `members.nominee.read` for `GET` and `members.nominee.create` for `POST`. 004D does not reuse
  `members.member.read` for nominee creation.
- Validation: PAN and Aadhaar are required; missing values return `MISSING_REQUIRED_FIELD`, invalid
  source formats return `INVALID_PAN_FORMAT` / `INVALID_AADHAAR_FORMAT`, and nominees under legal
  majority return `NOMINEE_MINOR_NOT_ALLOWED`. A-031 records the age-18 majority default pending
  source confirmation.
- Responses and audit metadata expose masked PAN/Aadhaar only and never full plaintext identity
  values. Nominee create writes `members.nominee.created`; masked list/read writes no workflow event.
- Member Profile's Nominee tab is API-backed with existing card/empty/alert/form styles. It must not
  restore `mockData` nominee rows such as the old synthetic `Sudha Patil` example.
- `data-model.md` §10.5 and `screen-spec.md` S09 require witnesses to belong to a loan application,
  resolve to an existing SFPCL shareholder/member or folio, carry protected PAN/Aadhaar, and remain
  incomplete until shareholder/KYC verification is complete. 004E should not create a member-level
  witness endpoint if loan applications/shareholdings are still absent.
- `api-contracts.md` §15.1-§15.2 define member shareholding list/create/update:
  `GET`/`POST /api/v1/members/{member_id}/shareholdings/` and
  `PATCH /api/v1/shareholdings/{shareholding_id}/`. Response fields include `shareholding_id`,
  `folio_number`, `number_of_shares`, `holding_mode`, valuation snapshot fields,
  `pledged_share_count`, `available_share_count`, and `future_shares_pledge_flag`.
- `data-model.md` §11.1 requires `shareholdings` with member FK, folio, non-negative share counts,
  holding mode (`physical`/`demat`/`mixed`), optional demat/valuation references, pledged and
  available counts, future-pledge flag, status, and timestamps. Constraints: shares cannot be
  negative, pledged shares cannot exceed total shares, and available shares equal total minus
  pledged when maintained.
- `data-model.md` §11.2 defines `share_certificates` under a shareholding: certificate number,
  optional distinctive-number range, share count, optional document FK, and status
  (`active`/`pledged`/`transferred`). 004F should only implement certificate behavior if it can stay
  within one slice alongside the shareholding API; otherwise split certificates into a follow-up.
- `auth-permissions.md` maps shareholding endpoints to `members.shareholding.read`,
  `members.shareholding.create`, and `members.shareholding.update`.

## 004D2 Contract-Hardening Extracts
- `auth-permissions.md` §30.2 requires actor/action/entity/old/new values/request/IP/user-agent
  audit contents, and §30.3 AUD-005/AUD-006 allows only masked values or metadata, not sensitive
  data values, in audit logs.
- `api-contracts.md` §13.3 shows member-detail `available_actions[]`, and §44 says detail endpoints
  may return action availability for frontend usability, but the backend remains the source of
  workflow gates. 004D2 keeps member profile detail neutral by returning `available_actions: []`
  until 005A and later eligibility slices own loan-start actions and blockers.
- `api-contracts.md` §14.1-§14.3 plus local API contracts keep nominee PAN/Aadhaar required,
  validated, stored as protected tokens plus keyed hashes, and returned masked. 004D2 removes
  nominee PAN/Aadhaar plaintext, encrypted token keys, hash keys, and submitted identity-derived hash
  values from `members.nominee.created` audit metadata only; stored hash columns stay unchanged for
  duplicate/search support.
- Queue sharpening on 2026-07-09: 004E witness validation is blocked until persisted
  shareholding/shareholder facts and a real loan-application boundary exist. 004F shareholding now
  follows 004D2 directly so witness verification can later resolve against real facts instead of a
  member-level or boolean-only stub.

## 004F Shareholding Extracts
- `api-contracts.md` §15.1-§15.2 define member shareholding list/create/update. 004F implements
  only `GET`/`POST /api/v1/members/{member_id}/shareholdings/`; `PATCH
  /api/v1/shareholdings/{shareholding_id}/` is deferred to a follow-up slice.
- `data-model.md` §11.1 requires member FK, folio number, non-negative share count, holding mode
  (`physical`/`demat`/`mixed`), nullable demat/valuation references, valuation snapshot fields,
  pledged and available share counts, future-shares pledge flag, status, and timestamps.
  004F maintains `available_share_count = number_of_shares - pledged_share_count` and rejects
  pledged shares above total shares.
- `auth-permissions.md` §12.2/endpoint map uses `members.shareholding.read` for list and
  `members.shareholding.create` for create. 004F does not use `members.member.read` as a substitute
  for shareholding access.
- 004F writes `members.shareholding.created` audit metadata for successful creates and no workflow
  event. Read-only list access writes no audit/workflow row.
- Member Profile's Shareholding tab is API-backed and must not render `mockData` shareholding rows
  or a certificate placeholder as the primary backend-backed state. It uses existing card, empty
  panel, alert, and form patterns.
- `data-model.md` §11.2 share certificates remain deferred: certificate number, optional
  distinctive range, share count, optional document FK, and active/pledged/transferred status should
  be implemented in a small follow-up slice, not folded into unrelated land/KYC work.

## 004E Witness Validation Extracts
- `data-model.md` §10.5 makes a witness application-scoped and requires protected PAN/Aadhaar,
  persisted shareholder verification, verification metadata, and KYC. `screen-spec.md` S09 requires
  a real SFPCL shareholder/member or folio and says documentation cannot complete before witness
  verification.
- `auth-permissions.md` §15.4 and §26.4 allow Compliance and Company Secretary to record witness
  KYC, Credit Manager to read, and audit access to remain read-only. The §12.2 catalogue and §34
  endpoint map omit exact witness permission codes; 004E records this gap and uses narrow
  `members.witness.read/create` permissions following the source naming convention instead of
  borrowing nominee/shareholding/KYC permissions.
- 004E uses nested `GET/POST /api/v1/loan-applications/{id}/witnesses/`, validates application object
  access, and qualifies only a member with matching name, verified KYC, and at least one active
  positive shareholding. Caller verification metadata is forbidden; successful creation sets it
  from persisted facts and writes a metadata-only audit row.

## 004G/004H Queue-Sharpening Extracts
- `api-contracts.md` §17.1 defines land-holding endpoints:
  `GET`/`POST /api/v1/members/{member_id}/land-holdings/` and detail/update
  `/api/v1/land-holdings/{land_holding_id}/`. Create request fields: `document_type`,
  `survey_number`, `village`, `taluka`, `district`, `state`, `area_acres`, `document_id`.
- `api-contracts.md` §17.2 defines crop-plan endpoints:
  `GET`/`POST /api/v1/members/{member_id}/crop-plans/` and detail/update
  `/api/v1/crop-plans/{crop_plan_id}/`. Create request fields: nullable
  `loan_application_id`, `crop_type`, `season`, `planned_area_acres`,
  `estimated_cost_amount`, `loan_purpose_alignment`, and nullable `document_id`.
- `data-model.md` §11.7 requires land-holding verification fields and says 7/12 extract is
  required for loan application, while `area_acres` feeds land-based loan limit. 004G must not
  invent loan-limit calculations or application blockers.
- `data-model.md` §11.8 requires crop-plan verification fields. 004G should persist records and
  validation only; loan-purpose eligibility decisions belong to later application/eligibility
  slices.
- `api-contracts.md` §18.1-§18.5 define KYC profile list/create/update, document upload, document
  verify, and re-KYC review endpoints. `data-model.md` §12.1-§12.2 requires `kyc_profiles` and
  `kyc_documents`; KYC must be complete before disbursement, and re-KYC recurs every two years.
- Screen spec S06 Land and Crop Evidence tab fields are 7/12 extract document, land area under
  cultivation, crop plan, crop type, season, per-acre scale of finance, and land-based eligible
  amount. 004G should not add frontend UI unless it wires to real backend data using existing
  Member Profile patterns.

## 004G Landholding and Crop Plan Extracts
- 004G implements only `GET`/`POST /api/v1/members/{member_id}/land-holdings/` and
  `GET`/`POST /api/v1/members/{member_id}/crop-plans/`. Detail/update endpoints remain deferred.
- `land_holdings` now stores member FK, document type, survey/location fields, positive
  `area_acres`, required `document_id`, verification status, nullable verifier/timestamp, and
  created timestamp.
- `crop_plans` now stores member FK, nullable `loan_application_id`, crop type, season, positive
  `planned_area_acres`, optional estimated cost, loan-purpose alignment, optional `document_id`,
  verification status, nullable verifier/timestamp, and created timestamp.
- Because `auth-permissions.md` has no land/crop-specific codes, A-032 records the 004G assumption:
  lists use `members.member.read`, creates use `members.member.update`, and no new permission codes
  are seeded.
- Successful creates write metadata-only audit rows: `members.land_holding.created` and
  `members.crop_plan.created`. Read-only lists write no access audit and no workflow event.
- Validation rejects zero/negative acreage, missing land `document_id`, malformed UUIDs, and missing
  required create fields. Loan-limit calculations, per-acre scale-of-finance, purpose eligibility,
  application blockers, verification actions, and land/crop detail updates are deferred.
- Member Profile's Land & Crop tab is API-backed with loading/empty/error/list/validation/success
  states using existing Member Profile card, empty-panel, alert, and form patterns. It does not show
  per-acre scale of finance or land-based eligible amount because no source-backed calculation
  endpoint exists yet.

## 004H KYC Upload and Verification Extracts
- 004H implements member-party KYC only:
  `GET/POST /api/v1/kyc-profiles/`, `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/`,
  `POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/`, and
  `POST /api/v1/kyc-documents/{kyc_document_id}/verify/`.
- `kyc_profiles` stores party type/id, status, CKYC consent, optional beneficial-ownership flag,
  risk rating, verification user/timestamp, re-KYC due date, and rejection reason. One profile is
  allowed per member party.
- `kyc_documents` stores profile FK, allowed document type (`pan`, `aadhaar`, `photo`,
  `ckyc_consent`), restricted `document_files` FK, self-attestation flag, verification status,
  verifier/timestamp, remarks, and created timestamp.
- Permissions are source KYC codes only: profile read/create/update, document upload, and document
  verify. No `kyc.document.download`, `kyc.sensitive.reveal`, or `kyc.rekyc.manage` behavior is
  implemented.
- PAN and Aadhaar uploads require self-attestation. KYC upload/verify audits are metadata-only and
  exclude identity plaintext, identity hashes, encrypted CKYC identifiers, and file bytes.
- A-033 records the temporary status rollup: document verification updates profile/member KYC status
  and sets re-KYC due two years after verified results until source-backed completeness rules exist.
- Member Profile's KYC tab is API-backed with loading/empty/error/list/validation/success states
  using existing profile card, empty-panel, alert, field, and status-badge patterns. Sensitive reveal
  remains deferred to 004I.

## 004H2/004J Architecture-Review Extracts
- Architecture review 2026-07-09 found that `kyc_profiles` has a one-profile-per-party database
  constraint, and this digest says one profile is allowed per member party. 004H2 should add a
  failing-first duplicate-create regression and return a standard validation envelope before the
  database raises an unhandled uniqueness error.
- `data-model.md` §12.3 defines `bank_accounts` with owner party type/id, holder name, protected
  account number storage/hash/last4, IFSC, bank and branch names, verification status, nullable
  cancelled-cheque link, signature-verified flag, and active/inactive status.
- `data-model.md` §12.4 defines `cancelled_cheques` with loan-application/member/document IDs,
  protected account-number storage, IFSC, branch, verification status, signature-mismatch flag, and
  created timestamp. Because loan applications do not exist yet, 004J should either keep the
  cancelled-cheque boundary member-profile-only with an explicit assumption or defer
  loan-application-specific cheque behavior.
- `data-model.md` §12.5 defines `bank_verification_letters` for signature mismatch/detail
  confirmation with bank signed/stamped flags and verification result. This belongs to a
  signature-mismatch/documentation workflow unless 004J is split.
- `data-model.md` §28 includes `bank_accounts.account_number_encrypted` and
  `cancelled_cheques.account_number_encrypted` in the encrypted sensitive-field set. API responses
  and audit metadata must expose only masked/last-four account values, never full numbers, encrypted
  token contents, hashes, cheque images, or file bytes.
- `screen-spec.md` S11 says duplicate checks include the same bank account in other active borrower
  records, S15 covers bank verification letters for signature mismatch, and disbursement screens use
  cheque-derived holder name, masked account number, IFSC, and branch. 004J should persist the
  foundation facts but not invent duplicate-active-borrower decisions, mismatch resolution,
  disbursement blockers, or payment initiation.

## 004I Sensitive Reveal Extracts
- 004I implements only member PAN/Aadhaar reveal:
  `POST /api/v1/members/{member_id}/reveal-sensitive-field/` with request
  `field_name` (`pan` or `aadhaar`) and non-empty `reason`.
- Base member read remains `members.member.read`; field permissions are exact:
  `members.sensitive.reveal_pan` for `pan` and `members.sensitive.reveal_aadhaar` for `aadhaar`.
  Broad member read, KYC, document, admin, export, or bank permissions do not grant reveal.
- `GET /api/v1/members/{member_id}/` stays masked. Its `pan.can_view_full` and
  `aadhaar.can_view_full` flags reflect only the matching field-specific permission and never
  include full source values.
- Successful reveal returns the full value only in the immediate response with a five-minute
  `expires_at`, `Cache-Control: no-store`, and `Pragma: no-cache`. Frontend code keeps full values
  only in temporary component state, requires a reason before calling the endpoint, and clears the
  reason after success.
- Success audit action: `members.sensitive_field.revealed`. Authenticated denial audit action:
  `members.sensitive_field.reveal_denied`. Audit metadata includes member ID, field name, reason,
  outcome, denial reason when applicable, request ID, IP/user-agent, and expiry on success; it
  excludes full PAN/Aadhaar, encrypted token contents, hash values, and identifier-derived values.
- Missing auth returns `401 AUTH_REQUIRED` without reveal audit. Missing base read returns
  `403 PERMISSION_DENIED`; missing field permission returns `403 SENSITIVE_FIELD_ACCESS_DENIED`;
  invalid field/reason or unavailable source value returns `400 VALIDATION_ERROR`; unknown or
  soft-deleted member returns `404 NOT_FOUND`. Sensitive reveal writes no workflow event.

## 004J Bank Account and Cancelled Cheque Extracts
- 004J implements member-profile bank metadata only:
  `GET/POST /api/v1/members/{member_id}/bank-accounts/` and
  `GET/POST /api/v1/members/{member_id}/cancelled-cheques/`.
- `bank_accounts` stores member ownership as `owner_party_type = member` plus `owner_party_id`,
  holder name, protected account-number token, keyed hash, last four, IFSC, bank/branch names,
  verification status (`pending`/`verified`/`rejected`), nullable cancelled-cheque FK, nullable
  signature-verified flag, status (`active`/`inactive`), and created timestamp.
- `cancelled_cheques` stores member FK, nullable `loan_application_id` placeholder, document ID,
  protected account-number token, keyed hash, last four, IFSC, branch, verification status,
  signature-mismatch flag, and created timestamp. Loan-application-specific cheque behavior remains
  deferred until application persistence exists.
- Responses expose only masked account-number metadata shaped as
  `{masked, last4, can_view_full: false}`. Full account numbers, protected token contents, and
  account-number hashes are never serialized or included in audit metadata.
- Because `auth-permissions.md` has no exact bank-account metadata codes, A-034 records the 004J
  assumption: lists use `members.member.read`, creates use `members.member.update`, and no new
  permission codes are seeded. PAN/Aadhaar reveal, KYC, document, disbursement, export, and security
  permissions do not grant bank metadata access or reveal.
- Successful creates write metadata-only audit rows: `members.bank_account.created` and
  `members.cancelled_cheque.created`. Read-only lists write no audit/workflow row, and create
  actions write no workflow event.
- Validation rejects missing holder/account/IFSC facts, account numbers shorter than four digits,
  malformed UUID fields, unsupported verification status, and unsupported bank-account status.
  Duplicate-active-borrower warnings, bank verification letters, signature mismatch resolution,
  blank-dated cheque custody, disbursement gates, payment initiation, and bank-account full reveal
  are deferred.

## 004K Borrower 360 and KYC UI Wiring Extracts
- 004K wires `Borrower360` to existing Epic 004 frontend client methods and adds bank/cancelled
  cheque fetch methods for `GET /api/v1/members/{member_id}/bank-accounts/` and
  `GET /api/v1/members/{member_id}/cancelled-cheques/`.
- Borrower 360 now composes member detail, shareholding, land/crop, nominee, KYC profile/document,
  bank-account, and cancelled-cheque metadata in the approved existing card/tab/status patterns.
  It no longer imports `mockData` or renders the former synthetic loan, repayment, communication,
  risk, audit, security, or nominee rows.
- PAN/Aadhaar display remains masked by default. If the backend marks a field revealable, the page
  captures a reason and calls the 004I reveal endpoint; full values remain temporary component state
  only with backend expiry messaging and a hide control.
- Bank-account and cancelled-cheque account numbers are normalized to masked/last-four metadata with
  `can_view_full: false`; the UI has no bank reveal affordance and does not add duplicate-active
  borrower warnings, signature-mismatch resolution, payment initiation, or disbursement-readiness
  controls.
- Later application, loan-account, repayment, communication, risk/exception, and audit API wiring
  remains deferred. Borrower 360 shows explicit empty states for those modules instead of reusing
  prototype mock data.

## 004K2 Architecture-Review Extract
- Architecture review 2026-07-09 found a frontend/backend DTO mismatch in the Borrower 360 bank
  metadata path: the 004J backend/API contract serializes bank-account holder names as
  `account_holder_name`, but the 004K frontend type, normalizer, and tests use `holder_name`.
- Corrective slice 004K2 should preserve the backend field name, update the frontend API type and
  normalizer to consume `account_holder_name`, render that value on Borrower 360, and add a
  regression using the real backend response shape.
- Bank account numbers must remain masked-only with `can_view_full: false`; 004K2 must not add a
  bank-account reveal flow, duplicate-active-borrower warning, signature-mismatch workflow,
  payment initiation, or disbursement-readiness UI.

## Architecture Review 2026-07-12 12:52 - Member and Witness Governance Corrections

- `MemberRegistry` must be the public create/update/read/request/approve seam and enforce exact
  permission plus member object access internally; auth §34.2 requires object access for member
  detail/update, and views or public service helpers cannot be the only guard.
- Proposed PAN/Aadhaar changes must be duplicate-checked again under approval locking and translate
  database uniqueness races to standard field errors with no partial member/history/audit writes.
- Identity approval projection must disable the requester even when that actor also has the checker
  permission, using the same maker-checker evaluation and reason as the write.
- API §13.2 registration still requires the full individual and institution variants listed in
  corrective slice 006Y5; current staff forms submit only a subset.
- S09 names witness address and mobile in addition to name/PAN/Aadhaar. 006Y6 must persist those
  contact fields and expose disabled six-field witness actions rather than omitting denied actions.

## 006Y6 Witness Contact and Action Parity Closure

- S09 address is required free text (500-character storage boundary); mobile is optional and, when
  supplied, contains 7-15 digits after spaces are removed. Both are returned by witness APIs and
  recorded as plain old/new values in versioned correction history because they are not protected
  identity evidence.
- Collection and resource projections retain read/create and read/update actions when disabled,
  with stable permission or application-object reasons. Application Detail consumes these actions,
  shows the disabled update reason, and never infers mutation authority.
