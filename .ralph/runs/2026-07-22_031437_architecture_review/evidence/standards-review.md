# Standards Review

Reviewed `git diff fff95e9d...71fd80df` independently against `AGENTS.md`, the decision and
frontend rules, codebase-design §§26/42, API contracts, and the terminal owner contracts.

- High: `servicingApi.ts` accepts capture-only composite-command responses and performs separate
  SAP/allocation mutations in React, violating the sole backend financial owner.
- High: `security_instruments/search_facade.py` discards actor and bypasses the canonical Stage-4
  package/object decision; prefix routing also omits valid arbitrary SAP/CDSL identifiers.
- Medium: acceptance tests cover the happy composite response and generic pagination helpers but
  not the compatibility fallback, cross-page identity stability, or out-of-scope security records.
- Low: the coordinator retains an unused cross-domain model alias solely for an old probe patch
  target; this weakens the public facade seam.

No tooling-enforced style issue was counted as an architecture finding.
