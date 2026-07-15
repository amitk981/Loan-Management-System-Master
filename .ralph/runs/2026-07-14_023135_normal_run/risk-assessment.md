# Risk Assessment

Risk level: High under the owner's standing approval and veto policy.

- Selected slice: `007L-sanction-workbench-contract-and-browser-closure`
- Mode: `normal_run`
- Approval/veto check: standing approval applies; `HIGH_RISK_APPROVALS.md` lists no vetoed slices.

## Material risks and controls

- Approval confidentiality/authority: incomplete frozen review packages remain nondisclosing; no
  collection count, detail, action, sanction decision, or register fallback was widened. Existing
  backend action enforcement remains authoritative, and React intersects enabled resource actions
  with `/auth/me` permissions only.
- Historical truth: borrower identity joins the credit-owned v2 package at review handoff. No live
  member/appraisal/configuration reconstruction or unproven legacy backfill was added; older partial
  packages fail closed.
- Workflow display: partial approval is derived from the immutable action ledger. Pending age is a
  server-projected elapsed fact labelled honestly; it claims no policy target or breach.
- Document evidence: changed General Meeting submissions require three fresh restricted legal
  uploads tied to the exact application. Case/register metadata ids grant neither reuse nor download.
  Backend document reference validation remains authoritative.
- Frontend transport: auth, bearer headers, FormData construction, standard envelope parsing, and
  normalized errors now have one shared owner. Feature code retains only typed paths/payload fields.
- Browser evidence: the spec collects, but local Chromium was blocked by the known macOS Mach-port
  sandbox denial. No screenshot was fabricated. The declared `localhost-e2e-server` contract causes
  the orchestrator to run all seven screenshots twice outside the sandbox.

## Blast radius

Approval review-package creation/validation and approval-case serialization; sanction API/service,
workbench, shared authenticated transport, and the single sanction Playwright spec. No database
migration, dependency, real communication, deployment, external service, or Git operation occurred.

## Residual risk

The trusted browser gate has not executed inside this sandbox and remains the orchestrator's
independent acceptance decision. Epic 007 register/settings evidence remains intentionally open for
007M/007N.
