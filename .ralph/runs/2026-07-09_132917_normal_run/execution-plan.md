# Execution Plan

Selected slice: 004H-kyc-upload-and-verification

## Scope
- Implement KYC profile and KYC document metadata persistence for member parties only.
- Add source-backed endpoints:
  - `GET /api/v1/kyc-profiles/?party_type=member&party_id={member_id}`
  - `POST /api/v1/kyc-profiles/`
  - `PATCH /api/v1/kyc-profiles/{kyc_profile_id}/`
  - `POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/`
  - `POST /api/v1/kyc-documents/{kyc_document_id}/verify/`
- Wire the Member Profile KYC tab to these APIs using existing profile card, alert, empty-panel,
  field, and status-badge patterns only.
- Update `docs/working/API_CONTRACTS.md`, the Epic 004 digest, handoff/progress/state/slice status,
  and required Ralph evidence artifacts.

## Deliberate Deferrals
- Re-KYC review task endpoints from source §18.5 unless the core API/UI work remains trivially small.
- Sensitive reveal behavior and reveal UI; slice 004I owns reason capture, expiry, and audit.
- Disbursement/appraisal blockers, CKYC provider integration, KYC deficiencies, document download,
  and nominee/witness/signatory KYC.

## TDD Plan
1. Add backend tests for profile create/read/update, member-only party validation, missing member,
   authentication and permission separation, document upload metadata, unsupported document types,
   PAN/Aadhaar self-attestation, verification/rejection, and metadata-only audits.
2. Run the targeted backend KYC tests before implementation and save red output under
   `evidence/terminal-logs/`.
3. Implement models, migration, services, views, URL routes, serializers, validation, and audit rows.
4. Add frontend API-client and Member Profile KYC tab tests for loading/empty/error/validation/success.
5. Run targeted backend/frontend tests and save green outputs.

## Quality Gates
- Backend: `manage.py check`, full backend tests, `makemigrations --check`, coverage using
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Frontend: `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.
- Save API examples and a static HTML screenshot artifact when frontend is touched.
