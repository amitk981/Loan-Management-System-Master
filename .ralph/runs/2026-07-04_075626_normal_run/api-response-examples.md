# API Response Examples

No API contract or backend endpoint changed in slice 002F.

This slice consumes the existing 002D3 `/api/v1/auth/me/` contract:

- `roles[{role_code, role_name}]`
- `teams[{team_code, team_name}]`
- `permissions[]`
- `available_actions[]`

Frontend behavior added in this run maps `permissions[]` through `CANONICAL_TO_PROTOTYPE_PERMISSIONS` and uses the shared `PAGE_PERMISSIONS`/`resolveNavigationAttempt()` contract to hide or block staff shell navigation. Unknown canonical permissions and unknown role codes continue to grant no prototype UI access unless explicitly mapped and tested.
