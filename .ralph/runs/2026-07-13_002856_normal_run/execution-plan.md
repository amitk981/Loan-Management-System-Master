# Execution Plan

Selected slice: 006Z2-portal-application-limit-display-authority

1. Trace the existing PortalAccount boundary, loan-limit calculator/configuration, verified active-member authority, application submission validation, and MP05 transport/rendering contracts.
2. TDD the borrower-scoped read endpoint one behavior at a time: authoritative available projection and redaction, own-account scope, unavailable/stale authority, and server-owned requested-amount advisory. Save focused RED and GREEN logs.
3. TDD the routed portal UI against the shared HTTP transport: one canonical projection GET, existing three-card money display, explicit unavailable/error states, server advisory, review row, submit field error, and canonical post-submit refetch without local synthesis.
4. Implement the smallest backend service/view/URL and frontend API/container changes needed to satisfy those tests, preserving existing visual classes and API envelopes.
5. Run focused suites, then all configured backend/frontend quality gates; save self-contained terminal and visual evidence where the sandbox permits collection.
6. Review permissions, redaction, money authority, protected paths, and diff limits; write run artifacts, mark this slice complete, update state/progress/handoff, and sharpen the next one or two Not Started slices only from already-open requirements.
