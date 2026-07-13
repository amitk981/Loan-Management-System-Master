# Migrated Endpoint Families

Production global-permission callers were migrated in these families:

- Identity: admin users, audit logs, and portal-account authority.
- Members: directory, profile, nominees, shareholdings, land/crop, KYC, bank accounts, masking,
  and portal member views.
- Applications: drafts, submit/reference, documents, completeness, deficiencies, rejection notes,
  witnesses, eligibility/loan-limit/appraisal routes, and sanction handoff/read.
- Credit-facing application adapters, including appraisal review and submit-to-sanction authority.
- Documents and secure downloads.
- Communications, templates, and notifications.
- Configuration collections/actions.
- Dashboard summaries.
- Workflow-event reads.
- Tracer lifecycle endpoints.

No frontend production branch referenced the retired code; only test fixtures did, and the shared
backend contract preserves the normal generic 403 UI behavior without a frontend production edit.
