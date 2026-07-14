# Slice 008I3: Security-Legal Evidence Seam and Race Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008I2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Restore the source dependency direction between legal documents and security instruments while
preserving exact terminal PoA/SH-4/CDSL evidence and making every promised race assertion real.

## Source / Review References

- `docs/source/codebase-design.md` §§6.3-6.4, 9.1-9.3, 15, 28.1, and 36.1-36.2
- `docs/source/api-contracts.md` §§6-8 and 28.1-28.5
- `docs/source/data-model.md` §§16-17, 30, and 34
- `docs/source/auth-permissions.md` §§18-19 and 26.4
- `docs/slices/008F2-security-instrument-boundary-and-poa-lifecycle-closure.md`
- `docs/slices/008H-sh-4-physical-share-security-workflow.md`
- `docs/slices/008I-cdsl-pledge-workflow.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_234031_architecture_review`

## Concrete Requirements

1. Make the §36.2 app graph executable: `security_instruments` must not import approvals or
   `legal_documents` models, selectors, modules, serializers, or views. `legal_documents` may
   consume security metadata. When one atomic action needs both owners, use one top-level process
   coordinator, following `processes.sanction_completion`, that locks owners in a single documented
   order and passes immutable typed evidence facts through narrow interfaces. Remove I2's temporary
   `legal_documents.modules.power_of_attorney` compatibility import after migrating every retained
   caller to the security owner; the legal package must contain no PoA alias or policy shell.
2. Keep policy local: security modules own applicability, member/share, maker-checker, custody,
   pledge, and terminal-state decisions; legal modules own renderer, stamp, notary, signature, and
   checklist truth. The coordinator may compose the two decisions but may not become a duplicate
   workflow engine or let caller-supplied snapshots become authority.
3. Preserve all public §28 routes, request fields, response/action/error contracts, retained tables,
   checklist/package projections, exact replay, terminal consumed-evidence guards, audit/version/
   workflow facts, and zero readiness/invocation/disbursement side effects. Preserve I2's exact
   ₹500.00 PoA activation rule and its scoped masked reader matrix (including assigned-versus-
   unrelated approvers); the coordinator must not turn read scope into mutation or evidence access.
4. Replace the inverted import test with both-direction AST assertions matching §36.2 and executable
   interface tests proving direct security callers cannot bypass legal evidence validation through
   a forged DTO or alternate call path.
5. Deepen repeated security audit/version/workflow recording behind one internal interface with
   mandatory redaction and request/role/team attribution. Do not layer a second ledger or alter
   retained event shapes.
6. Strengthen 008G2/008F2/008H/008I five-worker tests: different payloads must yield exactly one
   material terminal winner (exact replay remains separately tested), zero loser success evidence,
   and exact winner/loser audit, version, workflow, actor, and request identities. Run every declared
   security/legal race twice on PostgreSQL.

## Test Cases

- AST dependency graph and top-level coordinator atomic rollback/lock-order tests.
- No compatibility alias remains; all retained imports resolve directly to the security PoA owner.
- Forged/missing/stale/cross-application legal evidence DTO denial for PoA, SH-4, and CDSL.
- Existing public success, replay, maker-checker, terminal immutability, projections, and package
  scope remain unchanged.
- Twice-run changed PoA, SH-4, CDSL, and tri-party races with complete evidence identities.

## Evidence Required

RED/GREEN dependency and bypass regressions, interface diagram/contract examples, focused impacted
suites, twice-run PostgreSQL output, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The source app dependency graph is enforced, not inverted by a wrapper or selector import.
- Cross-owner legal/security actions remain atomic and cannot accept caller-forged truth.
- Promised race evidence proves exact winner and zero-success-loser identities.
- All configured and declared capability gates pass.

## Done Checklist

- [x] Execution plan written
- [x] Dependency and forged-evidence regressions written RED first
- [x] Top-level evidence coordinator and security-local policy implemented
- [x] Compatibility alias removed and executable dependency graph enforced
- [x] Shared redacting audit/version/workflow recorder implemented
- [x] PoA, tri-party, SH-4, and CDSL PostgreSQL races passed twice
- [x] Backend/frontend configured gates passed
- [x] Evidence, risk assessment, review packet, state, progress, and handoff updated
- [ ] Commit created only after passing independent gates (Ralph orchestrator owned)
