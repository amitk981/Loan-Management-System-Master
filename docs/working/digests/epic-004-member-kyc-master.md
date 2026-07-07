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
