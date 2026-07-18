# Risk Assessment

Risk level: High

The slice changes the external-communication idempotency seam. A defect could duplicate borrower
advice after provider acceptance, reuse stale recipient/template/content facts, fabricate sent truth
from a malformed provider result, leak protected financial content, or introduce a communications
to disbursements dependency cycle.

Controls and evidence:

- The unchanged 009H3A outbox is committed pending before the provider call and uniquely binds the
  stable communication/key, canonical recipient/digest, full template-provenance checksum, rendered
  snapshots, canonical payload digest, and related entity.
- Accepted provider result is validated and committed to the outbox before the transitional final
  receipt/Communication transaction. The forced crash test proves an exact fresh-adapter retry uses
  the same logical identity; changed recipient and template facts conflict with no extra call.
- Rejection and malformed results remain pending and retryable with no receipt, Communication,
  disbursement sent state, audit, or workflow truth.
- Only masked bank reference enters the merge context; the dispatcher rejects protected values in
  merge/rendered content. Existing audit masking and zero-financial-side-effect public tests remain
  green.
- Static AST tests and the dependency graph prove communications imports no disbursement code and
  the legacy module defines no duplicate template/render/payload/provider policy.
- No model, migration, dependency, frontend, public wire contract, financial state, or downstream
  lifecycle changed. Focused tests, Django check, migration sync, compile, protected-path, and diff
  checks pass.

Residual risks:

- 009H3BB still owns moving receipt/Communication/audit/workflow finalization fully into
  communications and proving both final crash windows under twice-run PostgreSQL five-caller races.
- A future real provider must honor the supplied idempotency key; the Future adapter preserves that
  obligation but this offline MVP run does not claim external-provider sandbox proof.

Standing High-risk owner approval applies. No veto/revocation is recorded, and no manual approval is
required before independent orchestrator validation.
