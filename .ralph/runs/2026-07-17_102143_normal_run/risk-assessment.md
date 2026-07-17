# Risk Assessment

Risk level: High

The slice changes a financial maker-checker decision, permissions, immutable audit evidence, and a
money-adjacent aggregate. It ran under the owner's standing approval and is not revoked.

## Principal Risks and Controls

- Unauthorized or self-approved payment instruction: the owner reloads and locks an active persisted
  actor, requires active governed `chief_financial_controller` authority plus the Critical explicit
  grant, and rejects the 009E maker as checker.
- Cross-object or stale approval: the owner locks the disbursement, account, application, member,
  both banks, task, initiation audit/workflow, and any terminal evidence; it reconciles the exact
  initiation/readiness/request/comment and current source-bank governance/version/audit tuple.
- Double/opposite decision: a row lock plus database terminal-evidence constraint admits one complete
  winner. Exact coherent replay is zero-write; changed/opposite/concurrent losers conflict.
- Approval presented as transfer success: both decisions retain `bank_transfer_status=pending` and
  leave UTR, disbursed time, balances, account status, advice, register, checklist, repayment,
  schedule, and borrower communication untouched.
- Sensitive-data leakage: the response is five safe fields. Audit/workflow retain safe ids, amount,
  roles/teams, digests, request/network context, and outcome—not bank/member plaintext, PAN/Aadhaar,
  capabilities, signed URLs, or legal/security payloads.
- Historical compatibility: one nullable migration leaves every pre-009F initiated row honestly
  pending; a database constraint requires the core terminal identities together only after decision.

## Residual Risk

The source requires a server-owned next-action state but does not name its wire vocabulary. A-097
records the conservative `record_bank_transfer`/`none` values for later governance. Full backend
coverage and complete-suite ordering remain the independent Ralph orchestrator's authoritative gate.
