# Execution Plan

Selected slice: 011NA-member-portal-notices-grievances-and-notifications

## Permission and scope check

- Product edits are limited to `sfpcl_credit/**` and `sfpcl-lms/src/**`; focused E2E work may use
  the repository's existing frontend E2E location.
- Run evidence is limited to `.ralph/runs/2026-07-23_192235_normal_run/**`.
- `docs/source/**`, protected workflow/configuration files, orchestrator-owned state/progress/status
  facts, and Git metadata will not be edited.
- No package installation, migration, or unstated business policy is planned.

## Public behavior plan

1. Establish the existing portal routes, member-auth seam, communication/document download
   interfaces, grievance interface, notification interface, and closure projections.
2. RED→GREEN one backend behavior at a time through the authenticated HTTP interface:
   - a borrower lists only their own published communications and downloads an attached document
     only through the existing audited signed-download interface;
   - a borrower creates, lists, and retrieves only their own grievances with required-field
     validation and staff resolution status/reason;
   - a borrower lists only their own notifications;
   - a borrower lists only their own loan closure, NOC, security-return, and unpledge status.
3. Keep the backend projection behind one member-scoped portal interface that consumes owner
   modules/facades instead of duplicating workflow, document, or financial rules.
4. Wire MP19, MP20, MP21/MP22 (the consolidated prototype support page), MP23, and MP24 static help
   content through the existing portal transport, cards, badges, tables, alerts, and layout. Cover
   loading, empty, error, validation, success, and mobile rendering without new visual patterns.
5. Add/update focused frontend tests and the exact trusted-browser spec
   `e2e/member-portal-communications.e2e.spec.ts`; produce
   `member-portal-communications-mobile.png` from two passing runs if the local browser launches.
6. Run focused backend tests with the mandated Ralph Python, impacted frontend tests, typecheck,
   lint, build, Django check, and migration consistency. The orchestrator retains the authoritative
   impacted/full backend lane.
7. Save RED/GREEN terminal logs, browser evidence, risk assessment, traceable review packet, and
   final summary. Finish with review packet Result exactly `Ready for independent validation`.
