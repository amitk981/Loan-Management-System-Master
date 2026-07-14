# Risk Assessment

Risk level: High

## Why this is high risk

The slice changes the authority seam used by every current security-package, PoA, SH-4, and CDSL
route; it also changes shared audit/version/workflow recording and the concurrency semantics of
verified tri-party remark corrections. A mistake could accept stale legal evidence, leak a
sensitive value, lose immutable attribution, weaken maker-checker separation, or break terminal
instrument behavior.

## Controls and residual risk

- Cross-owner facts are re-resolved through one coordinator under the existing security atomic
  transaction and documented lock order. Caller-supplied authority is rejected before lookup.
- AST regression prevents executable security-to-approvals/legal imports; the compatibility alias
  is absent. Historical migrations and string FK labels are unchanged.
- The shared recorder recursively redacts sensitive names and always attributes actor role/team and
  request/network facts. Terminal consumed-document and workflow identities remain explicit.
- Exact ₹500 PoA, scoped masked readers, current legal provenance, maker-checker, terminal replay,
  checklist/package preservation, and no readiness/invocation/disbursement effects passed focused
  public tests.
- Ten authoritative PostgreSQL races passed twice; full backend/frontend gates are green.

Residual risk is concentrated in future extension of the private issuer convention: Python cannot
make a private function cryptographically inaccessible, so repository AST/interface tests and the
public process rejection are the enforcement controls. 008I4 must preserve the seam while replacing
temporary CDSL encryption/reveal behavior.

Standing owner approval applies; the veto list contains no revoked entry for this slice.
