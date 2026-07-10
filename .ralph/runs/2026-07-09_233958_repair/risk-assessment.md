# Risk Assessment

Risk level: Medium

- Selected slice: 005FB-member-portal-dashboard-profile-and-supply-view
- Mode: repair
- Manual review required: normal Ralph review only.

## Risk Drivers
- Full-stack portal slice touching authenticated borrower/member data.
- Object-level privacy matters: portal users must see only their linked member record.
- Sensitive values appear in the profile surface and must remain masked.
- Produce-supply source table exists in `data-model.md`, but the implemented backend model does not.

## Controls Applied
- Portal endpoints derive scope from an active `PortalAccount.member_id`; client `member_id` query
  values are ignored as authority.
- Staff and non-portal tokens receive `403 PERMISSION_DENIED` on portal own-data endpoints.
- Existing member subresource serializers are reused; PAN/Aadhaar and bank-account values remain
  masked and portal `can_view_full` is forced false.
- Produce supply returns an empty shell and A-043 records the model gap instead of inventing rows.
- Backend and frontend TDD red/green evidence is saved under `evidence/terminal-logs/`.

## Residual Risk
- Loan counts are placeholder zeroes because loan-account models are not implemented yet.
- Notices are empty because borrower-facing notice/letter delivery is out of scope.
- Live screenshot capture failed due sandbox browser permissions; static visual evidence HTML is
  saved and all frontend gates pass.
