# Exact HTTP examples

- `GET /api/v1/loan-applications/{id}/appraisal-note/` now returns the standard §44
  `available_actions` projection, including disabled reasons and required authority.
- Legacy remediation is advertised as `revalidate_appraisal_prerequisites` only for a
  `legacy_unverified` appraisal in a remediable state with update plus risk authority.
- `POST /api/v1/appraisal-notes/{id}/revalidate-prerequisites/` sends exactly `{}`.
- `PATCH /api/v1/loan-applications/{id}/appraisal-note/` continues to use the strict writable
  projection; response-only IDs, snapshots, status, TAT, review history, and actions are excluded.
- `GET /api/v1/loan-applications/{id}/sanction-case/` preserves the stored approval-case and exact
  workflow-event identities; this slice did not alter the 006G3 serialization.

