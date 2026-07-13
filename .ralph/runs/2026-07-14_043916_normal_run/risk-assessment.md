# Risk Assessment

Risk level: High (owner standing approval; no veto)

This slice changes an approval/compliance queue's totals, filtering, pagination, and object-scope
work, plus the shared frontend collection parser used by register and matrix clients. A defect
could hide an attributable sanction case, leak a scoped total, or make a malformed success look
authoritative.

Controls applied:

- SQL query shaping uses only coarse actor, indexed assignment, known approval type, and known
  status facts. Every remaining candidate still crosses `approval_case_is_readable` before count,
  pagination, or serialization; stored coherence/index projections never become authority.
- Unknown approval type/status values fail explicitly with the standard validation envelope.
- Instrumented public collection tests distinguish valid, stale-malformed, wrong-actor,
  wrong-type, and wrong-status rows across two pages without pinning SQL text or statement counts.
- The shared frontend interface validates the complete list envelope and internal page/count/flag
  consistency. Authentication and server error envelopes retain their existing codes/statuses.
- S21 retains exact sanction/object-scope filters on every page, uses server totals, and clears
  stale rows and totals on permission or response failure.
- Full frontend/backend gates pass; no database migration, dependency, protected file, source file,
  deployment, real communication, or paid external action is involved.

Residual risk: local Chromium cannot launch inside the macOS sandbox, so the required visual and
interaction proof remains subject to the orchestrator's two independent trusted browser runs. The
spec collects and declares the exact required screenshot; no local screenshot was fabricated.
