# Risk Assessment

Risk: High.

This slice changes the implementation owner and authorization boundary for legal/security metadata,
plus a terminal Power of Attorney compliance rule. A defect could expose security metadata,
permit mutation by a read-only role, or activate inadequate legal evidence.

The change is bounded by unchanged database schema/tables/UUIDs/protected relations/routes, an
atomic exact-₹500 guard inside activation, action-permission-first denial, canonical latest-cycle
Stage-4 scope, assigned/persisted approver and auditor scope, and explicit separation of masked read
from every mutation/reveal/download/invocation/release permission. Missing/null references and
₹1/₹499.99/₹500.01 attempts produce zero success writes. PostgreSQL activation and downgrade races
passed twice with exact winner and zero-loser success identities.

The temporary legal compatibility import is honest but remains architecture debt; sharpened 008I3
must remove it alongside remaining security-to-legal/approval imports through the source-defined
top-level evidence seam. No schema migration, frontend surface, external call, protected file,
`docs/source`, or git metadata changed. Standing High-risk approval applies and the veto list is
empty.
