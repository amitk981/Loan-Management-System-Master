# Ralph Handoff

## Last Run

2026-07-15_001106_normal_run

## Current Status

008I2 is complete. The full retained PoA workflow now executes from
`security_instruments.modules.power_of_attorney`; `legal_documents` retains only a temporary
policy-free compatibility import for 008I3 to remove. Activation requires the exact current
maker/checker stamp amount of ₹500.00 plus completed notarisation and existing exact signatures.
Missing/null references and ₹1/₹499.99/₹500.01 attempts fail atomically.

Package reads are separate from mutation authority. Canonically scoped Credit Manager,
Compliance, Company Secretary, Senior Manager Finance, CFC, assigned CFO/Director approvers, and
persisted audit-readonly users receive masked metadata only. Unrelated approvers, missing
permission, inactive identities, and read-only mutation attempts fail closed. No read grants
reveal, download, invocation, release, refresh, or readiness.

## Validation

Evidence is in `.ralph/runs/2026-07-15_001106_normal_run/evidence/`. Retained red/green logs cover
module ownership, exact stamp amount, and the read matrix. The PoA activation/downgrade races passed
twice on PostgreSQL with exact winner request/audit/version/workflow identities and zero loser
success evidence. Backend check/migration sync and 829 tests passed at 92% coverage; frontend lint,
typecheck, build, and 293 tests passed.

## Next Run

Run sharpened 008I3, then 008I4 before 008J. I3 must remove the temporary compatibility import and
remaining source-forbidden security-to-legal/approval dependencies through typed top-level evidence
coordination while preserving I2's exact ₹500 rule and scoped masked reads. I4 then centralises
encryption/reveal and fixes nullable pending CDSL evidence. A-101 still blocks the complete real
Term-Sheet path.
