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
