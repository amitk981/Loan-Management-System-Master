# Impact Analysis

Selected slice: `CR-010-backend-pending-age-parallel-ci-flake`

## Affected backend pieces

- Model: `approvals.ApprovalCase`, specifically the persisted `submitted_at` and
  `current_status` values consumed by the live pending-age projection. No model or migration change
  is required.
- Service/serializer: `sfpcl_credit/approvals/modules/approval_case_engine.py`.
  `serialize_case_detail()` includes `_workbench_summary()`, and `_workbench_summary()` calls
  `_pending_age()`. `_pending_age()` computes `elapsed_seconds` from `timezone.now()` for every
  pending-case serialization, so this one field is intentionally not frozen.
- Endpoints: `GET /api/v1/approval-cases/{case_id}/` through
  `approvals.views.approval_case_detail`, and `GET /api/v1/approval-cases/` through
  `approvals.views.approval_case_collection`. Both return `serialize_case_detail()` output; the
  assigned queue adds `assigned_to_me=true`.
- Test runtime: Django's `RemoteTestResult` uses optional `tblib` traceback pickling support when
  failures cross worker-process boundaries. `sfpcl_credit/requirements-dev.txt` currently pins
  coverage but not `tblib`, although both GitHub backend workflows install this file before running
  parallel tests.

Grep evidence:

```text
sfpcl_credit/approvals/modules/approval_case_engine.py:213: "workbench_summary": _workbench_summary(case)
sfpcl_credit/approvals/modules/approval_case_engine.py:262: "pending_age": _pending_age(case)
sfpcl_credit/approvals/modules/approval_case_engine.py:295: def _pending_age(case)
sfpcl_credit/approvals/views.py:40: def approval_case_collection(request)
sfpcl_credit/approvals/views.py:208: def approval_case_detail(request, approval_case_id)
sfpcl_credit/config/urls.py:223-224: approval-case collection and detail routes
.github/workflows/ci.yml:52: pip install -r sfpcl_credit/requirements-dev.txt
.github/workflows/backend-serial-canary.yml:43: pip install -r sfpcl_credit/requirements-dev.txt
```

## Affected frontend pieces

- `sfpcl-lms/src/services/sanctionApi.ts` declares `workbench_summary.pending_age` with live
  `elapsed_seconds` and display fields.
- `sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx`, routed from `src/App.tsx`, renders only the
  server-provided pending-age label/display in the sanction queue.
- No frontend contract, rendering, route, style, or component changes are required. Existing
  frontend fixtures already provide the same payload shape, so no frontend regression test is
  added.
- `FRONTEND_DESIGN_RULES.md` compliance: no UI file will be edited and the approved visual system
  remains unchanged.

## Blast radius and other consumers

- Approval action success responses also reuse `serialize_case_detail()`, but this slice does not
  alter production serialization or action behavior.
- The assigned queue and direct detail response share the same live age calculation. Complete
  payload equality across separate requests is unsafe anywhere in the approvals test module unless
  pending age is isolated first.
- Repository-wide `pending_age` grep found no other backend module consumer. The only production
  consumer outside approvals is the sanction frontend listed above.
- The complete parallel backend lane is affected because any real assertion failure must be
  serialized from a worker to the parent process. Pinning traceback support affects test tooling
  only, not production dependencies or runtime behavior.

## Existing coverage and regression additions

- Existing approvals coverage:
  `ApprovalCaseRoutingApiTests.test_live_appraisal_policy_change_preserves_pending_case_reads_and_action`
  covers detail, assigned queue, stable frozen routing/provenance/appraisal facts, queue membership,
  and the approve action across a live appraisal-policy edit.
- Existing approvals coverage:
  `ApprovalCaseRoutingApiTests.test_detail_is_unchanged_when_live_configuration_rows_change`
  covers detail stability across live rule and committee edits.
- Existing live-age coverage:
  `test_collection_projects_complete_frozen_s21_workbench_facts` validates the pending-age label,
  elapsed range, and display; the historical-routing test already isolates pending age and checks
  monotonicity.
- Approvals regression change: drive both known before/after tests with an explicit advancing clock;
  deep-copy and remove only `workbench_summary.pending_age`; compare every remaining detail/queue
  field and pagination exactly; then validate both live age values separately for canonical label,
  non-empty display, and non-decreasing elapsed seconds.
- Backend-infrastructure regression addition: verify the development requirements explicitly pin
  `tblib`, then pass a captured assertion failure through Django's `RemoteTestResult` and Python
  pickle round-trip to prove the original exception and traceback survive worker transport.

## Risk boundaries

- No production code, model, API contract, migration, frontend, source document, workflow script,
  or protected configuration change is planned.
- Tests will run serially in the coding sandbox as required by the slice. The orchestrator remains
  the sole authority for the complete configured parallel coverage proof.
