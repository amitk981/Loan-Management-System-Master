# Approval Case API Examples

Representative contract examples verified by
`sfpcl_credit.tests.test_approval_case_routing_api.ApprovalCaseRoutingApiTests`.
UUIDs are illustrative test values.

## Assigned queue

`GET /api/v1/approval-cases/?current_status=pending&approval_type=sanction&assigned_to_me=true`

```json
{
  "success": true,
  "data": [
    {
      "approval_case_id": "11111111-1111-1111-1111-111111111111",
      "approval_type": "sanction",
      "related_entity_type": "loan_application",
      "related_entity_id": "22222222-2222-2222-2222-222222222222",
      "loan_application_id": "22222222-2222-2222-2222-222222222222",
      "application_reference_number": "LO00000701",
      "amount": "500000.00",
      "current_status": "pending",
      "decision_date": "2026-07-13",
      "version": 2
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-13T00:00:00Z",
    "api_version": "v1"
  }
}
```

## Routed detail action projection

The full response additionally contains immutable matrix/committee/loan-limit provenance and
dynamic `review_facts`. The action fragment for the pending snapshotted CFO is:

```json
{
  "required_approvers": [
    {
      "role_code": "cfo",
      "user_id": "33333333-3333-3333-3333-333333333333",
      "full_name": "Snapshot CFO",
      "decision": null,
      "acted_at": null
    }
  ],
  "available_actions": [
    {
      "action_code": "approve",
      "label": "Approve",
      "enabled": true,
      "disabled_reason": null,
      "required_permission": "approvals.case.approve"
    },
    {
      "action_code": "reject",
      "label": "Reject",
      "enabled": true,
      "disabled_reason": null,
      "required_permission": "approvals.case.reject"
    },
    {
      "action_code": "return",
      "label": "Return for Clarification",
      "enabled": true,
      "disabled_reason": null,
      "required_permission": "approvals.case.return"
    }
  ]
}
```

## Assignment-scope denial

An authenticated user without `approvals.case.read` receives:

```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have approval case read permission.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-13T00:00:00Z",
    "api_version": "v1"
  }
}
```
