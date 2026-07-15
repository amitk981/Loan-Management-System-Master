# Validation Failure Summary

The trusted outside-sandbox Playwright run reached the successful MP11
resubmission response and canonical application refetch, but the final status
assertion is still stale:

`getByText('Submitted', { exact: true })` timed out at
`sfpcl-lms/e2e/member-portal-deficiency-response.e2e.spec.ts:50`.

The shared `StatusBadge` maps the canonical `submitted` status to the rendered
label `Submitted - Pending Completeness Check`, not `Submitted`. Repair only
this acceptance assertion using the exact rendered label, preferably scoped to
the application header, while preserving the subsequent exact absence check for
the `Deficiency Response` heading and all earlier selector repairs.

The documentation-actions spec passed in the same trusted run. The isolated
SQLite readonly error seen once was caused by two Playwright processes racing
over the same E2E database and is not a product defect; do not change database
or application code for it.
