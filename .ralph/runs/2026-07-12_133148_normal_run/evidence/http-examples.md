# Member Governance HTTP Examples

## Requester-checker denial

`GET /api/v1/members/{member_id}/` projects:

```json
{
  "action_code": "members.member.identity_change.approve",
  "label": "Approve identity change",
  "enabled": false,
  "disabled_reason": "Requester cannot approve their own change.",
  "required_permission": "members.member.identity_change.approve",
  "required_role": null
}
```

The matching approval POST returns `403 FORBIDDEN` with the same reason and leaves member, request,
history, and audit evidence unchanged.

## Duplicate proposed identity

`POST /api/v1/members/{member_id}/identity-change-requests/` and approval-time uniqueness races
return `400 VALIDATION_ERROR` with `pan` and/or `aadhaar` field errors. `IntegrityError` is absorbed
inside Member Registry and the surrounding transaction rolls back.

## Masked evidence

History stores PAN/Aadhaar masks only (for example `******6789U` and `********1234`). Audit evidence
contains request ID and changed field names; it excludes plaintext values, protected tokens, and
hashes. The canonical member response retains `{masked, can_view_full}` identity objects.
