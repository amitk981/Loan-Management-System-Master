# Risk Assessment

Risk level: Medium (matches the selected slice).

- Selected slice: 005I4-application-detail-backend-state-hardening
- Mode: normal_run
- Manual review required: normal orchestrator review before commit/merge.

## Risks and controls
- Additive API risk: `assigned_owner` and object-shaped `available_actions` are added only to staff
  GET detail; mutation and portal response shapes remain unchanged. Backend contract tests cover
  owner/action shape and submitted-state neutral actions.
- Workflow risk: the frontend no longer infers stage history, owner departments, SAP progress,
  disbursement readiness, or payment actions. Only backend actions are rendered; current `submit`
  delegates to the existing guarded API.
- Sensitive-data risk: nominee rendering is metadata-only and tests exclude PAN/Aadhaar labels,
  tokens, hashes, and reveal controls.
- Visual risk: existing classes, cards, tabs, badges, alerts, and stepper are reused. A-050 records
  why the mock-backed `DocumentChecklist` cannot be used for real API rows.
- Evidence limitation: the in-app browser list was empty and localhost binding was denied, so PNG
  capture was impossible. Two built-CSS-inlined, self-contained HTML renders are saved instead.

No dependency, migration, external service, deployment, or real-data risk was introduced.
