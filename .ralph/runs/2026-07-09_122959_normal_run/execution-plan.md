# Execution Plan

Selected slice: 004F-shareholding-and-share-certificate-records

## Scope
- Implement `GET` and `POST /api/v1/members/{member_id}/shareholdings/`.
- Add the `shareholdings` persistence model and one migration.
- Wire Member Profile's Shareholding tab to the real API using existing card, empty panel, alert, and form patterns.
- Update working API contracts, digest/handoff/state/slice status, and run evidence.

## Explicit Deferrals
- `PATCH /api/v1/shareholdings/{shareholding_id}/` is deferred to keep this slice small.
- `share_certificates` are deferred to a follow-up slice; source §11.2 requires them, but adding nested certificate create/update plus UI would broaden 004F beyond list/create shareholding records.
- Demat account table behavior, valuation calculation, CDSL integration, pledge eligibility, and loan-limit rules remain deferred per slice validation rules.

## TDD Plan
1. Backend RED: add a shareholding API test covering list/create success, permission split, invalid counts, overflow, missing member/auth, available-share derivation, and audit metadata.
2. Backend GREEN: add `Shareholding` model/migration, service functions, URL/view, serializer, validation, and audit write.
3. Frontend RED: add API-client and `MemberProfileView` tests for shareholding list/create loading, empty, error, validation, success states, and no mock share rows.
4. Frontend GREEN: extend `memberProfileApi.ts` and the Shareholding tab to fetch/create real rows with existing styles.
5. Refactor only after tests are green.

## Gates and Evidence
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for all backend commands.
- Save red/green test logs and final gate logs under `.ralph/runs/2026-07-09_122959_normal_run/evidence/terminal-logs/`.
- Run backend check, backend tests, migration check, coverage, frontend typecheck, lint, tests, and build.
- Save API response examples and screenshots if frontend can be rendered locally.
