# Review Packet — 006Y8

## Outcome

Witness correction now exposes separate contact and identity controls. Both projection and PATCH
consume the application-owned correction evaluation for update permission, application scope,
maker-checker separation, and current version. The verifier can correct address/mobile but cannot
mutate protected identity; a distinct authorised checker can.

## Traceability

- Source says witness identity is protected, witness evidence belongs to the application and must
  remain reviewable (`data-model.md` §10.5, §29-§30); code preserves immutable verification facts
  and masked correction history; verified by
  `test_witness_correction_is_versioned_masked_audited_and_preserves_evidence`.
- Source says action facts use exactly six fields and backend workflow gates remain authoritative
  (`api-contracts.md` §44); code projects `read`, `correct_contact`, and `correct_identity`; verified
  by `test_witness_correction_actions_distinguish_verifier_from_checker_authority`.
- Slice requires routed real-session contact reload, verifier denial, and checker identity reload;
  `witness-correction-authority.e2e.spec.ts` uses the production login and Application Detail route,
  collects exactly one test, and writes the three required screenshot names during trusted runs.

## Observable HTTP examples

- Verifier GET: `correct_contact.enabled=true`; `correct_identity.enabled=false` with
  `A different authorised user must correct verified witness identity.`
- Verifier identity PATCH: `403 MAKER_CHECKER_REQUIRED`, same message, zero correction history/audit.
- Checker identity PATCH with current version: `200`, version increments, PAN/Aadhaar remain masked.
- Stale PATCH: `409 VERSION_CONFLICT`; immutable/unknown or malformed PATCH: `400 VALIDATION_ERROR`.

## Verification

- Frontend: build, typecheck, lint, 176/176 tests.
- Backend: check, migration sync, 451/451 tests with 7 expected SQLite skips, 93% coverage.
- Browser: named spec collection succeeds; trusted screenshots are intentionally delegated to the
  orchestrator's two declared outside-sandbox runs.
