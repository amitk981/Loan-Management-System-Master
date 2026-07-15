# Risk Assessment

Risk level: Medium

- Selected slice: 007I-sanction-workbench-ui
- Mode: normal_run
- Standing approval: active; no veto entry exists.

## Security and integrity assessment

- Resource authority remains server-owned. The UI intersects enabled case actions with current-user
  permissions only for usability and never unions a global grant into case authority. The new
  General Meeting action is likewise projected only on evidence-required cases after the backend's
  canonical case-scope, legal-audience, and exact three-permission decision.
- Frozen review, authority, exception, conflict, meeting, and decision facts come only from the
  selected approval cycle. The workbench does not query live appraisals or registers to reconstruct
  hidden or historical cases, and it keeps 403/404/409 outcomes distinct.
- Legal files use the existing application-scoped upload boundary and the existing §25.11
  documents-owned reference validation. Case/register metadata never enables reference/download.
  A-090 explicitly defers selection of previously uploaded files until a documents-owned projection
  exists rather than accepting arbitrary identifiers.

## Regression and operational risk

- The App route and Approval Panel now use the typed real container; 21 interaction tests cover all
  action bodies, reason validation, field errors, assigned/read-only/unauthorized roles, old/new
  cycles, GM evidence, and terminal states. A raw-source check confirms the owned mock, ₹5 lakh
  matrix, client role-slot matching, and legacy `approve_sanction` gate are gone.
- The backend addition is a read-only action projection with no migration or permission seed change.
  Ordinary cases omit the inapplicable action, preserving the existing action-list contract; all 105
  approval-routing tests and the full suite pass.
- Browser screenshots were not fabricated. Playwright collection succeeds, while the local server
  launch is denied by the sandbox. The declared orchestrator acceptance run remains the final visual
  authority.

## Gate outcome

- Backend: check and migration sync green; 680 tests green with 19 expected skips; 93% coverage.
- Frontend: build, typecheck, lint, and 227 tests green.
- Browser: one deterministic contract collected; sandbox launch denial retained in evidence.
- Diff: no migration or dependency; protected/source paths unchanged; `git diff --check` clean.
- Manual review required: orchestrator independent validation before commit/merge/push.
