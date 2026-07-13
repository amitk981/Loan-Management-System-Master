# Approval Contract Examples

## Distinct authority after lower-route replacement

```json
{
  "route_approvers": [
    {"role_code": "cfo", "user_id": "cfo-id", "full_name": "CFO"},
    {"role_code": "director", "user_id": "director-1-id", "full_name": "Director 1"}
  ],
  "required_approvers": [
    {"role_code": "cfo", "user_id": "cfo-id", "full_name": "CFO", "decision": "approved", "acted_at": "timestamp"},
    {"role_code": "director", "user_id": "director-2-id", "full_name": "Director 2", "decision": "approved", "acted_at": "timestamp", "replacement_for_user_id": "director-1-id"}
  ],
  "approval_actions": [
    {"approval_action_id": "action-1", "role_code": "cfo", "user_id": "cfo-id", "full_name": "CFO", "decision": "approved", "comments": null, "acted_at": "timestamp"},
    {"approval_action_id": "action-2", "role_code": "director", "user_id": "director-2-id", "full_name": "Director 2", "decision": "approved", "comments": null, "acted_at": "timestamp", "replacement_for_user_id": "director-1-id"}
  ]
}
```

Collection, detail, and the case portion of the action response returned identical facts in
`test_alternate_action_is_canonical_without_rewriting_route_provenance`.

## Unsatisfied two-Director authority

Excluding either routed Director left exactly CFO + one distinct Director, so public enrichment
returned `current_status = blocked_by_conflict` and:

```json
{
  "conflict_block_reason": "Required Director approval authority is unavailable after conflict exclusion."
}
```

Both directions retained zero ApprovalAction and zero SanctionDecision rows.

## Unused alternate nondisclosure

An unused second Director with `approvals.case.read`, both before and after a material-interest
declaration, received an ordinary and assigned collection with `data: []` and `total_count: 0`.
Direct detail and action returned `403 OBJECT_ACCESS_DENIED`; no action row was written.
