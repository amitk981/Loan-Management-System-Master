# Review Packet: 2026-07-12_232553_normal_run

## Result
Complete; all configured gates pass.

## Slice
006Z5-active-member-evidence-and-verification-governance-closure

## Review Focus

- Confirm the migration matches data-model §11.5 and keeps one current effective record.
- Confirm `Member.active_member_status_id` stores the persisted record PK, while `result_id` remains
  deterministic calculation provenance.
- Confirm internal supply snapshots retain evidence/verifier/entity/route facts and portal rows
  strip them.
- Confirm missing/existing out-of-scope IDs share the same 403 category/message and create no record.

## Traceability

- Functional spec BR-006 says three continuous service years to an eligible SFPCL entity with
  evidence; `MemberServiceEvidence` proves dates/recipient/reference and
  `test_service_scalar_cannot_grant_br006_without_dated_evidence` verifies fail-closed behavior.
- Data model §11.5 says active status is an effective-dated persisted record;
  `ActiveMemberStatus` implements those fields and
  `test_verify_persists_effective_record_and_member_points_to_its_primary_key` verifies the pointer.
- Data model §11.6 names supply entity, route, institution, evidence and verifier facts;
  `SupplyRowProjection` retains them and `test_supply_snapshot_contains_every_review_input` verifies
  the exact snapshot. Portal redaction is verified in `test_portal_supply_is_read_only_and_scoped_from_portal_account`.
- Auth §25.1/§34.2 requires permission and member object access;
  `test_active_status_verify_non_discloses_existing_and_missing_out_of_scope_members` verifies the
  identical standard denial before verification evidence lookup.

## Validation

- Backend: 467 tests, 8 expected SQLite skips, 93% coverage; check and migrations sync pass.
- Frontend: build, typecheck, lint, and 202 tests pass.
- PostgreSQL: active-member verification plus five existing credit races pass twice (6/6 each).

## Recommended Next Action

Run the due architecture review, then 006Z2.
