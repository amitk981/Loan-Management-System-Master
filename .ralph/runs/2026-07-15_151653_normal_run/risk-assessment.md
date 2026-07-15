# Risk Assessment

Risk level: High (standing approval; no veto)

- Scope: authenticated borrower document upload/download authority, deficiency evidence,
  application lifecycle transition, audit/workflow truth, and trusted-browser interaction.
- Primary risks closed: read/write predicate drift, stale completion reopening, caller-forged
  expiry, signed-token cross-scope/replacement replay, direct lifecycle assignment, shadow
  deficiency state, duplicate file audit semantics, and immediate blob-URL revocation.
- Permission posture: one active portal-account/member/application resolver remains
  nondisclosing for missing, cross-member, internal, and inactive sessions. No internal checklist,
  security, reveal, approval, or file permission is granted to a portal actor.
- Data/security posture: tokens bind current file and full portal scope; content is checksum
  verified and no-store/no-cache. Responses expose no storage keys or protected security values.
- Persistence: no schema or migration change. Immutable document/response successor history is
  retained; invalid and repeated resubmission has one or zero canonical success writes.
- UI: only approved existing modal/drop-zone and portal card/badge patterns were reused. No new
  colour, typography, spacing system, mock fixture path, or client-owned business decision.
- Browser caveat: both specs collect, but the local sandbox lacks the Playwright Chromium binary.
  No screenshot was fabricated; independent twice-run browser acceptance remains authoritative.
- Residual risk: production PostgreSQL lock behavior and real browser rendering are independently
  validated by the orchestrator. Full routine gates otherwise pass at 92% backend coverage.
