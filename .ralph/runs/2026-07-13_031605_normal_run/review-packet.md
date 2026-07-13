# Review Packet: 2026-07-13_031605_normal_run

## Result
Ready for independent validation

## Slice
006Z9-active-member-authority-and-decision-contract-closure

## Outcome

- Replaced `Role.is_system_role` and unowned-row inference with one explicit action-scope projection.
- Enforced `pass -> active`, `relaxation -> relaxation`, and non-qualifying -> `inactive` decisions.
- Extended maker-checker separation across qualifying supply capture/verification and service or
  relaxation evidence ownership.
- Updated the stable API contract and recorded source-silent assignment governance as A-072.

## Traceability

The source says member access must be permission plus object scope and critical decisions must be
atomic and maker-checker safe (`auth-permissions.md` §§3/18/19/25.1; `data-model.md` §34). The code
now projects explicit action scope in `member_authority.py` and rejects contradictory/self-authored
verification in `active_member_status.py`. Tests
`test_role_provenance_does_not_change_explicit_global_verification_scope`,
`test_decision_must_match_calculated_route_with_zero_persisted_evidence`, and
`test_service_or_relaxation_evidence_maker_cannot_verify_derived_result` verify those contracts.

## Validation

- Frontend: build, typecheck, ESLint, 205 Vitest tests pass.
- Backend: Django check and migration sync pass; 498 tests pass with 12 expected PostgreSQL-only
  skips; coverage is 93% against the 85% floor.
- `git diff --check` passes and the dependency scan finds no production member-authority role
  provenance bypass.

## Recommended Next Action

Run independent Ralph validation and commit on success, then execute 006Z10.
