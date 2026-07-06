# Object Access Result Examples

No public API endpoint was added in slice 002I. These are service-level result examples from
`sfpcl_credit.identity.modules.object_permissions.evaluate_object_access(...)`; future API
slices should translate denied results through the standard API envelope.

## Allowed By Owner

```json
{
  "allowed": true,
  "reason": "allowed_owner",
  "error_code": null,
  "required_permission": "loan_application.read",
  "approval_required": false
}
```

## Allowed By Team

```json
{
  "allowed": true,
  "reason": "allowed_team",
  "error_code": null,
  "required_permission": "loan_application.read",
  "approval_required": false
}
```

## Missing Permission

```json
{
  "allowed": false,
  "reason": "missing_permission",
  "error_code": "PERMISSION_DENIED",
  "required_permission": "loan_application.read",
  "approval_required": false
}
```

## Unknown Scope

```json
{
  "allowed": false,
  "reason": "scope_unknown",
  "error_code": "OBJECT_ACCESS_DENIED",
  "required_permission": "loan_application.read",
  "approval_required": true
}
```
