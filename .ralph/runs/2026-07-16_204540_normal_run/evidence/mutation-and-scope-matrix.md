# Mutation, Scope, Query, and Zero-Write Evidence

## Exact owner mutations

- Changed checklist completion version body -> `documentation_complete` fails.
- Changed Company Secretary audit body -> Company Secretary and dependent ordered approvals fail.
- Open mismatch row -> `signature_mismatch_resolved` fails.
- Canonical but document-inappropriate PoA witness -> `signature_mismatch_resolved` fails.
- Rolled-back checklist status with retained actions -> all three ordered approval checks fail.
- Changed PoA renderer checksum evidence -> `poa_complete` and `security_package_complete` fail.
- Mutable `security_status=complete` without terminal evidence -> `security_package_complete` fails.
- Blank/cancelled cheque evidence is mandatory regardless of mutable package flags.
- Empty or forged well-formed SAP completion digest, forged delivery checksum, or a newer incomplete
  request -> `sap_customer_code_present` fails.
- Inactive SAP assignee and cross-member SAP lookup fail the public owner decision.

## Loan scope

- Active Senior Manager Finance with permission and the newest exact SAP assignment can read.
- Application `received_by_user` assignment is ignored.
- Wrong role, missing permission, inactive actor, unrelated SAP assignment, and absent id fail
  nondisclosing.
- CFC remains nondisclosing until 009E creates the canonical initiated-disbursement relation.
- Cross-member account and SAP-assignment coherence failures remain nondisclosing.

## Read-only/query evidence

- The bounded incomplete public projection remains at or below 30 SQL queries.
- Readiness assertions compare audit/workflow counts before and after; owner ledgers remain unchanged.
- No payment, CFC decision, transfer, UTR, balance, activation, task, or communication truth is added.
