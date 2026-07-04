# API Response Examples

Slice: `002H-state-machine-and-transition-guard-foundation`

No public endpoint was added. The examples below show that the migrated tracer path preserves existing response shapes while routing state/permission checks through the shared workflow guard.

## Successful Tracer Transition

`POST /api/v1/tracer/loan-applications/{loan_application_id}/sanction/`

```json
{
  "success": true,
  "data": {
    "entity_type": "loan_application",
    "entity_id": "00000000-0000-0000-0000-000000000000",
    "previous_status": "draft",
    "new_status": "sanctioned",
    "workflow_event_id": "00000000-0000-0000-0000-000000000001",
    "available_actions": []
  },
  "meta": {
    "request_id": "generated-or-forwarded-request-id",
    "timestamp": "2026-07-04T00:00:00Z",
    "api_version": "v1"
  }
}
```

Verified by `sfpcl_credit.tests.test_tracer_api.TracerApiTests.test_full_tracer_lifecycle_persists_and_audits_every_transition`.

## Missing Permission

`POST /api/v1/tracer/members/` as an authenticated user without `tracer.lifecycle.run`

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "Tracer lifecycle permission is required."
  },
  "meta": {
    "request_id": "generated-or-forwarded-request-id",
    "timestamp": "2026-07-04T00:00:00Z",
    "api_version": "v1"
  }
}
```

Verified by `sfpcl_credit.tests.test_tracer_api.TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows`.

## Invalid State Transition

`POST /api/v1/tracer/loan-applications/{loan_application_id}/loan-account/` while the application is still `draft`

```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Expected status sanctioned, found draft."
  },
  "meta": {
    "request_id": "generated-or-forwarded-request-id",
    "timestamp": "2026-07-04T00:00:00Z",
    "api_version": "v1"
  }
}
```

Verified by `sfpcl_credit.tests.test_tracer_api.TracerApiTests.test_transition_guard_rejects_creating_account_before_sanction`, including assertions that no extra success audit/workflow events are written.
