# Ralph Handoff

## Last Run

2026-07-14_000359_normal_run

## Current Status

007J is complete. RegistersHub S23 and S25 now load only their independent actor-scoped 007H/007F
collections through a typed authenticated client. Filter changes reset to page one and every
response replaces rows and pagination. S23 renders all 15 frozen fields—including distinct sanction
reasons, exception business reasons, conflicts/abstentions, and General Meeting metadata—without
case actions or document downloads. S25 keeps description and business reason separate. No owned
tab reads the remaining RegistersHub mock fixtures.

SettingsHub S71 now renders retained 007A matrix versions. A caller with
`approvals.matrix.manage` can submit a complete successor version, which the UI truthfully presents
as a pending maker-checker proposal; it never overwrites the active rule or fabricates activation.
Canonical register/matrix permissions now reach resource-scoped navigation gates without granting
unrelated hub tabs; backend sessions that hold only those permissions see only their owned
register/matrix surfaces. Register export is visible only with `reports.export` and makes no request
until the 012B/012C job contract exists.

## Validation

Focused RED/GREEN evidence is retained. Frontend production build, typecheck, lint, and all 245
tests pass. Backend check/migration sync and all 680 tests pass with 19 expected PostgreSQL-only
SQLite skips; coverage is 93% against the 85% floor. The sandbox denies Vite's localhost listener
with `EPERM`, so no screenshot was fabricated; the genuine visual-evidence attempt log is retained.

## Next Run

Run `007J2-settings-hub-panels-wiring-or-lockdown` using its new delivered-boundary notes. Preserve
the 007J matrix component/service and classify the remaining policy, TAT, template, and user/role
surfaces. Then run the now-concretely-sharpened `008A-document-template-model-and-versioning`.
