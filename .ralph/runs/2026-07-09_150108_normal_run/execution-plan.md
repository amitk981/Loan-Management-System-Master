# Execution Plan

Selected slice: 004I-sensitive-masking-and-reveal-audit

## Scope
- Implement only `POST /api/v1/members/{member_id}/reveal-sensitive-field/` for member `pan` and `aadhaar`.
- Preserve the existing masked `GET /api/v1/members/{member_id}/` response and the 004H2 KYC duplicate-create contract.
- Use field-specific permissions only: `members.sensitive.reveal_pan` and `members.sensitive.reveal_aadhaar`, plus the existing `members.member.read` base read gate.
- Audit success and denial attempts with metadata only; never persist or expose sensitive values in audit rows.
- Avoid schema changes unless a short-lived grant table proves necessary. The source contract only needs immediate-response reveal plus expiry metadata, so this plan uses no new model/migration.

## TDD Plan
1. Add a failing backend API test for successful PAN reveal through the public endpoint, asserting:
   - full value appears only in the immediate response;
   - response includes an expiry timestamp;
   - `Cache-Control`/`Pragma` prevent caching;
   - audit metadata contains actor/member/field/reason/outcome/expiry and no full value/hash/token.
2. Implement the minimal route, view, service helper, permission check, response headers, and audit row to pass the tracer test.
3. Add incremental failing tests and green each:
   - Aadhaar success uses `members.sensitive.reveal_aadhaar`;
   - missing auth is rejected without reveal audit;
   - missing base read permission writes a denied metadata audit;
   - missing field-specific permission writes a denied metadata audit;
   - unsupported/missing field, blank reason, unknown/deleted member, and unavailable value are rejected with standard envelopes and denial audit where an actor exists;
   - masked profile remains masked and reveal creates no workflow event.
4. Add frontend wiring only if the existing Member Profile patterns can support it without new styling; use reason-required local state only and do not cache full values beyond temporary component state.

## Documentation and Evidence
- Update `docs/working/API_CONTRACTS.md` with request/response, permissions, expiry/no-cache, and audit metadata.
- Save red/green backend output and final gates under `.ralph/runs/2026-07-09_150108_normal_run/evidence/terminal-logs/`.
- Save API response examples in the run evidence folder.
- Before finishing, sharpen the next 1-2 Not Started slices using only already-opened source/digest context.
- Complete Ralph artifacts: `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, handoff, progress/state, and slice status.
