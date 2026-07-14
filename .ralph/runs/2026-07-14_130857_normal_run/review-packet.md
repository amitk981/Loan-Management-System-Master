# Review Packet: 2026-07-14_130857_normal_run

## Result
Ready for independent orchestrator validation

## Slice
008B4-renderer-provenance-and-replay-contract-closure

## Recommended Next Action
Validate, commit, merge to `staging`, and push through the Ralph orchestrator. Then run 008C2.

## Change Summary

- Added one additive migration with an all-null/all-populated renderer provenance group.
- New output freezes `legal-renderer-v1`, generated-file UUID, and stored SHA-256 after genuine
  renderer validation; instance and normal bulk ORM paths reject provenance mutation.
- Legacy/mismatched output lists as `legacy_unverified`, conflicts on replay with zero writes, and is
  excluded from checklist linkage. No remediation/overwrite endpoint was invented.
- Moved authorised-unknown disclosure into application-owned authority: Compliance Team + route
  permission receives 404; missing/unrelated authority remains 403 before validation/queries.

## Traceability

- Source says generated documents retain template/file history and genuine Word/PDF output
  (`functional-spec.md` §15.1; `data-model.md` §§16.1-16.3). Code binds renderer contract, exact file,
  and checksum in `LoanDocument`; verified by
  `test_new_outputs_bind_current_provenance_to_reopened_stored_checksum` for both formats.
- Slice says legacy rows must not masquerade as current or overwrite legal history. Code returns
  `409 CONFLICT`, labels list metadata, and filters the checklist selector; verified with actual
  stored plain-text DOCX/minimal PDF plus executed/verified/stamped/notarised/checklist-linked facts
  in `test_legacy_unverified_row_conflicts_on_replay_and_is_labelled_in_list` and migration tests.
- API §7.5 says absent resources use 404 while denied actors remain nondisclosing. The application
  authority seam owns that ordering; verified by
  `test_unknown_application_is_404_only_after_role_and_permission_authority`.

## Independent Review

- Standards axis: no remaining findings after centralising disclosure authority and guarding bulk
  provenance mutation.
- Spec axis: no remaining findings after strengthening DOCX/PDF replay/selector and legacy lifecycle
  matrices.

## Validation

- Django check and migration sync: pass.
- Backend: 752 tests pass, 23 expected PostgreSQL-only skips, 93% coverage (85% floor).
- Frontend: build/typecheck/lint pass; 293 tests pass.
- Slice queue lint passes; state JSON parses; `git diff --check` passes; no protected path changed.
- No frontend or browser-acceptance scope; no network/dependency changes.
