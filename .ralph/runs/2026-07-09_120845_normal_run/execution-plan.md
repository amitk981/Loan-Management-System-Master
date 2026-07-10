# Execution Plan

Selected slice: 004D2-member-profile-and-nominee-contract-hardening

## Required context read

- Read `AGENTS.md`, token/context/runbook/config/permissions/state/handoff/policy/design-rule files in the requested order.
- Read selected slice `docs/slices/004D2-member-profile-and-nominee-contract-hardening.md`.
- Read parent epic `docs/epics/004-member-kyc-master.md`, digest `docs/working/digests/epic-004-member-kyc-master.md`, review finding entry, source references in `auth-permissions.md` and `api-contracts.md`, and current `docs/working/API_CONTRACTS.md`.

## Permission check

Planned edits are within allowed paths from `.ralph/permissions.json`:

- `sfpcl_credit/tests/test_member_nominees_api.py`
- `sfpcl_credit/tests/test_member_profile_api.py`
- `sfpcl_credit/members/services.py`
- `docs/working/API_CONTRACTS.md`
- `docs/working/HANDOFF.md`
- `docs/working/digests/epic-004-member-kyc-master.md` if queue sharpening needs distilled extracts
- `docs/slices/004D2-member-profile-and-nominee-contract-hardening.md`
- one or two next `docs/slices/*.md` files for required sharpening
- `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/2026-07-09_120845_normal_run/**`

Protected and forbidden paths will not be modified.

## TDD plan

1. Add a nominee-create API regression proving `members.nominee.created` audit `new_value_json` contains metadata but no PAN/Aadhaar plaintext, encrypted token keys, hash keys, or submitted identity-derived hash values. Run only `test_member_nominees_api` and save the failing log.
2. Implement the minimal service change: keep nominee stored hashes unchanged, keep masked responses unchanged, remove identity hash fields from audit metadata.
3. Run `test_member_nominees_api` and save the green log.
4. Add member-profile API regressions proving `available_actions[]` is neutral/deferred and no longer derived from `membership_status`, `kyc_status`, or `default_status`, even when the caller has `applications.loan_application.create`. Run only `test_member_profile_api` and save the failing log.
5. Implement the minimal service change: return an empty `available_actions[]` from member profile until 005A and later eligibility slices own the workflow.
6. Run `test_member_profile_api` and save the green log.

## Contract and docs plan

- Update `docs/working/API_CONTRACTS.md` to document empty member profile `available_actions[]` during this deferment and explicit nominee audit identity exclusions.
- Complete the selected slice checklist/status.
- Sharpen the next one or two `Not Started` slices using only source/digest context already opened.
- Update handoff, progress, state, risk assessment, review packet, changed-files, and final summary.

## Gates

Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command:

- targeted red/green backend tests as above
- `manage.py check`
- full backend test suite
- `makemigrations --check`
- backend coverage at or above 85%
- frontend `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`
- `git diff --check`
- protected/forbidden path review
