# Execution Plan

Selected slice: 011PD-compliance-frontend-wiring

## Scope

Wire the existing S62-S67 Compliance Dashboard to the backend-owned Epic 011 staff API seam,
remove its final mock-data dependency and inline business fixtures, preserve the approved prototype
layout, and extend the declared trusted-browser scenario and screenshot.

## Permission Check

- Allowed product scope: `sfpcl-lms/src/**` and the existing `sfpcl-lms/e2e/**` acceptance spec.
- Allowed evidence scope: `.ralph/runs/2026-07-25_025600_normal_run/**`.
- Documentation edits, if contract traceability requires them, are limited to unprotected
  `docs/working/**`.
- Forbidden/protected paths will not be edited, including `docs/source/**`, scripts, Ralph config
  and permissions, workflow policy, frontend design rules, and Git metadata.
- No package installation, backend schema/code change, or dependency change is planned.

## Public Seam and Behaviours

Use the established Epic 011 staff frontend API module as the interface. Keep server-owned
calculations, tracker state, role/action projection, and blocker truth behind that seam.

1. RED -> GREEN: the shared staff API requests the control, Section 186, NBFC, KYC/re-KYC,
   money-lending, and stamp-duty projections and preserves canonical refetch after review.
2. RED -> GREEN: the dashboard renders loading, success, empty, error, unauthorized, validation,
   and blocked states from that public seam without mock or inline business fixtures.
3. RED -> GREEN: projected compliance review actions execute and refetch canonical state, while an
   Internal Auditor receives the same reads with no mutation controls.
4. Extend the localhost trusted-browser contract for deterministic seeded values, read-only auditor
   behavior, and `compliance-trackers.png`, retaining both contract-run outputs.

## Verification and Evidence

- Save each focused RED and GREEN frontend command under `evidence/terminal-logs/`.
- Run focused API/request/action/render and reverse-consumer tests after each behavior.
- Run impacted frontend tests, then typecheck, lint, and build.
- Run the exact trusted-browser spec twice and retain its screenshot and both logs; if local
  Chromium infrastructure is unavailable, retain the honest probe/failure for trusted validation.
- Confirm `ComplianceDashboard.tsx` has no `mockData` import or inline compliance business fixture.
- Inspect targeted diff hunks and diff stats, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md`. Set the review result exactly to
  `Ready for independent validation`.
