# Digest — Epic 004: Member, KYC, Nominee, Witness, and Profile Master

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
