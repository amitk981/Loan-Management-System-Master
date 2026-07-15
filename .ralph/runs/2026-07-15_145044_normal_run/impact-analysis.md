# Impact Analysis

## Change boundary

This CR is a frontend-only visibility correction. The server projection deliberately exposes
status and controls independently; MP07 currently makes the status badge conditional on all three
controls being absent. The correction will render the existing badge for a completed action even
when an authorised download is retained.

## Backend models, endpoints, and services

- Model: `legal_documents.PortalDocumentationSubmission` is the retained upload record
  (`sfpcl_credit/legal_documents/models.py:764`). No field or migration changes are required.
- Process owner: `sfpcl_credit/processes/portal_documentation_actions.py` computes the borrower-safe
  action projection and upload/download authority. Grep identifies projection construction near
  lines 107-190 and upload/download guards near lines 201-364. Its contract already keeps `status`,
  `download`, `upload_allowed`, and `reupload_allowed` as separate facts.
- HTTP adapters: `sfpcl_credit/members/portal_views.py:325-383` expose documentation list, upload,
  and download actions; `sfpcl_credit/config/urls.py:243-253` routes them. No endpoint changes are
  required.
- Existing backend regression coverage:
  `sfpcl_credit/tests/test_portal_documentation_actions_api.py` covers the projection and retained
  download boundary. Because the CR neither changes nor reinterprets that backend contract, no new
  backend regression is needed; the full backend suite remains a release gate.

## Frontend screens, components, routes, and services

- Affected renderer:
  `sfpcl-lms/src/pages/borrower/portal/documents/MP07_DocumentChecklist.tsx`. Its action-control row
  currently renders `StatusBadge` only when download, upload, and re-upload are all absent.
- Existing public rendering tests:
  `sfpcl-lms/src/pages/borrower/portal/documents/PortalDocumentationActions.test.tsx` renders MP07
  and MP13 through their public interfaces. Add the CR regression here for MP07.
- Route/consumer: `sfpcl-lms/src/pages/borrower/BorrowerPortal.tsx:140` mounts MP07 for the
  `documents` tab. No route change is required.
- Shared hook/API contract:
  `usePortalDocumentationActions.ts` and `services/portalApi.ts:194-224,297-307` load and act on the
  projection. They already preserve the four independent server fields and need no change.

## Blast radius across other modules

- MP13 (`MP13_DocumentationActions.tsx`) consumes the same projection but has its own action-card
  rendering. It is not affected and will not be changed.
- The borrower portal shell/sidebar only selects MP07 and is not affected.
- Staff documentation, legal-document checklist, document storage/download, application lifecycle,
  permissions, audit, and workflow modules are not affected because this CR changes no state,
  authority, request, or response data.
- The only product module receiving a regression is MP07's existing portal-documentation rendering
  test module. Full frontend tests guard shared consumers.

## Regression behavior

Render MP07 with a server action whose status is `complete`, whose download descriptor is present,
and whose upload/re-upload flags are false. Assert through the rendered interface that:

1. `Complete` is visible.
2. `Download Term Sheet` remains available.
3. `Upload Term Sheet` and `Re-upload Term Sheet` are absent.

This is the only affected module and therefore the only new module-specific regression.

## Frontend design compliance

The change reuses the already-imported `StatusBadge`, the existing action row, current spacing,
colours, typography, and controls. It introduces no component, CSS class, colour, layout, mock
production data, business calculation, or client-side authority decision. It changes visibility
only, as required by `FRONTEND_DESIGN_RULES.md` and the owner-approved CR.
