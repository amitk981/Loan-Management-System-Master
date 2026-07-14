# Risk Assessment

Risk level: Medium

- Selected slice: 008B-document-generation-shell
- Mode: normal_run
- Change shape: one additive loan-document migration, two new API routes, generated confidential
  file persistence, and frozen-fact projection additions.
- Data risk: non-destructive. New later-workflow fields are nullable, generated rows retain protected
  template/file links, and no existing rows are rewritten or backfilled.
- Security/privacy risk: generated content is confidential, never returned or exposed through this
  slice's list API, and rendered merge content is excluded from audit/workflow evidence and names.
- Concurrency risk: exact replay is enforced by application locking and a database unique constraint;
  the declared PostgreSQL five-request acceptance passes.
- Boundary risk: generation consumes documents-owned source-reference/variant boundaries and
  approval-owned frozen facts; review corrections removed live nominee/witness/shareholding reads.
- External effects: none. No communication, deployment, package install, commit, merge, or push.
- Standing approval: applicable high-risk workflow rules were followed; the slice itself is Medium
  and is not revoked in HIGH_RISK_APPROVALS.md.
