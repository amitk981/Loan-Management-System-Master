# Epic 004-member-kyc-master: 004: Member, KYC, Nominee, Witness, and Profile Master

This parent epic preserves the broad planning context from the earlier Ralph slice. Actual implementation work is broken into smaller child slices under `docs/slices/`.

## Source Broad Slice

# Slice 004: Member, KYC, Nominee, Witness, and Profile Master

## Status
Not Started

## Goal
Implement member master data, individual/FPC profiles, nominee and witness validation, shareholding, land/crop records, KYC profiles, sensitive masking, and matching frontend screens.

## User Value
Credit users can manage the member record that all loan applications depend on, while sensitive identity and KYC data remains protected.

## Depends On
- Slice 002
- Slice 003

## Source References
- `docs/source/implementation-roadmap.md` sections 11, 20.1, 20.2, 20.3, 21.2, 22.1
- `docs/source/data-model.md` sections for parties, members, shareholding, KYC, bank, masking
- `docs/source/api-contracts.md` sections 13, 14, 15, 16, 17, 18
- `docs/source/screen-spec.md` member and borrower screens
- `docs/source/auth-permissions.md`

## Screens Involved
- Member Directory
- Member Profile
- Borrower 360
- KYC/document panels
- Sensitive reveal workflow

## Prototype Reference
- `MemberDirectory.tsx`
- `MemberProfile.tsx`
- `Borrower360.tsx`
- `mockData.ts`

## Frontend Scope
- Wire member directory/profile to real APIs.
- Add create/update flows if missing from the prototype.
- Add loading, empty, validation, error, unauthorized, and masked/reveal states.
- Preserve borrower/member profile layout while removing mock-only assumptions.

## Backend/API Scope
- Member list/create/detail/update APIs.
- Individual farmer and FPC/producer institution profile APIs.
- Nominee APIs with adult validation.
- Witness APIs with existing-shareholder validation.
- Shareholding, share certificate, demat, landholding, crop plan APIs.
- KYC profile/document upload/verify/re-KYC APIs.
- Sensitive reveal endpoint with reason and audit.

## Database/Model Impact
- Members, profiles, nominees, witnesses, shareholdings, share certificates, demat accounts, produce supply records, land holdings, crop plans, KYC profiles/documents, bank accounts where needed.

## API Contracts
- Member APIs
- Nominee APIs
- Shareholding APIs
- Active member status APIs
- Land/crop APIs
- KYC APIs

## Permissions
- Credit/Finance/Compliance can view/update according to source rules.
- Sensitive reveal requires explicit permission, reason, and audit.

## Validation Rules
- Member number uniqueness.
- Nominee cannot be minor.
- Witness must be existing shareholder where required.
- KYC documents use allowed document types.
- Masked fields remain masked unless reveal is authorized.

## Test Cases
- Member create/update/list/detail.
- Nominee minor rejection.
- Witness shareholder validation.
- KYC upload/verify and masking.
- Sensitive reveal audit.
- Frontend directory/profile states.

## Visual Acceptance Criteria
- Directory and profile remain scan-friendly.
- Masked sensitive fields are visually clear without leaking data.

## Evidence Required
- API tests and sample responses.
- Screenshots of directory, profile, masked field, and validation error.

## Risk Level
Medium

## Acceptance Criteria
- Member and KYC master records are persisted through APIs.
- Frontend member screens use backend data.
- Sensitive masking and reveal audit controls work.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

