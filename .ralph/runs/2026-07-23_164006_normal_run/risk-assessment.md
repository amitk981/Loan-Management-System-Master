# Risk Assessment

Risk level: Medium.

- Selected slice: 011N-grievance-workflow
- Mode: normal_run
- Data and privacy: member scope is enforced for every staff mutation/read and borrower scope is
  derived from an active portal account. Borrower projections omit staff history, owner, notes, and
  document identities.
- Evidence integrity: grievance documents require one immutable upload-provenance audit bound to the
  same member; cross-member and unproven references fail closed and denied cross-object access is audited.
- Workflow integrity: owner/due date are explicit, transitions are monotonic, history is append-only,
  resolution is idempotent, and escalation never resolves a grievance.
- Communication truth: a queued notice does not set borrower-informed truth; both a sent timestamp and
  `delivery_status=sent` are required.
- Concurrency: the declared two-test PostgreSQL class is present and locally discovers exactly two
  tests. SQLite skips them as designed; Ralph's trusted PostgreSQL lane remains the authoritative race
  gate.
- Residual operational dependency: approved grievance email/SMS templates and a governed member
  destination must exist before resolution can queue notice. This is the fail-closed A-166 contract.
