# Ralph Handoff

## Last Run

2026-07-14_134809_normal_run

## Current Status

Corrective 008C2 is complete. Public approval actions no longer accept a terminal completion hook;
direct final approval is zero-write, while the private sanction-completion coordinator atomically
creates the sanction decision, checklist, eleven items, and evidence. Checklist authority now
recomputes the canonical latest frozen terminal package instead of trusting the cached coherence
flag. Complete subsidiary flags and unanimous verified cheque mismatch rows are required; missing,
pending, malformed, partial, or conflicting facts stay visibly blocked.

Refresh preserves completion, verifier, time, remarks, checklist status, signature facts, and
creation-time presentation metadata. Completed-evidence applicability reversals conflict atomically.
Applicability and current-provenance linkage use separate action-specific audit projections with
request, IP, user agent, role, and team attribution. One approval-owned resolver handles permission,
A-104 pre-sanction compatibility, absent-parent nondisclosure, and sanctioned application/case scope
before any legal checklist query. No frontend or schema changes were needed.

## Validation

Evidence is in `.ralph/runs/2026-07-14_134809_normal_run/evidence/`. Focused RED/GREEN suites pass;
the genuine five-worker PostgreSQL final-sanction race passes twice. Django check and migration sync
pass; all 758 backend tests pass with 23 expected PostgreSQL-only skips and 93% coverage against the
85% floor. Frontend build, typecheck, lint, and all 293 tests pass. Independent Standards and Spec
reviews report no remaining findings.

## Next Run

Run 008D next. It is sharpened to accept only exact 008B4 current-provenance targets and use a narrow
status projection seam without invoking applicability refresh or changing completion evidence. 008E
is also sharpened to publish verified mismatch truth through the application-owned seam. The real
M05-to-full-Term-Sheet path remains configuration-blocked under A-101.
