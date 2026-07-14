# Slice 008I2: Security PoA Owner and Read Contract Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package
Epic file: `docs/epics/008-documentation-security-package.md`

## Depends On
- 008I

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make `security_instruments` the real implementation owner of Power of Attorney policy, enforce the
source-required PoA stamp amount, and restore the documented read-role contract without changing
retained tables, ids, routes, or terminal evidence.

## Source / Review References

- `docs/source/codebase-design.md` §§8.2, 15.1, 28.1, and 36.1-36.2
- `docs/source/api-contracts.md` §§6-8 and 28.1-28.3
- `docs/source/data-model.md` §§17.1-17.2, 30, and 34
- `docs/source/auth-permissions.md` §§12.8, 14.1, 16.4, and 19.2-19.4
- `docs/source/functional-spec.md` M06-FR-007/M06-FR-008
- Epic 008 digest: V10 p.14 §4.3 and Deck p.7
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_234031_architecture_review`

## Concrete Requirements

1. Move the complete PoA workflow implementation into
   `security_instruments.modules.power_of_attorney`. Remove the module-global
   `bind_security_owner`/`__getattr__` forwarding arrangement. A temporary compatibility import may
   point from `legal_documents` to the security owner only when a retained external caller genuinely
   requires it; it must contain no policy and the dependency direction must be asserted by AST.
2. Preserve the state-only table transfer, retained `security_packages`/`power_of_attorneys` rows,
   model labels, ids, protected relations, v1 routes, exact replay, legacy attribution, terminal
   activation evidence, checklist projection, and public generation tracer.
3. PoA activation requires the exact current adequate maker/checker stamp row to retain
   `stamp_paper_amount == 500.00` in addition to completed notarisation and exact signatures. This
   rule is PoA-specific: do not change the generic stamp recorder or invent the unresolved Loan
   Agreement/ad-valorem rule. Missing, null, ₹1, ₹499.99, and ₹500.01 must fail atomically.
4. Split package read authority from mutation authority. A caller with `security.package.read` and
   canonical object scope may read masked security metadata when the §14.1/§19 matrices allow it,
   including Credit Manager, Senior Manager Finance, CFC, CFO, Director/approver, and Internal
   Auditor. Compliance/CS remain the only preparation/custody actors; read never grants mutation,
   reveal, download, invocation, or release.
5. Preserve authority-first denial and nondisclosure. Add an explicit role/object matrix covering
   allowed readers, unrelated/assigned approvers, missing permission, inactive actors, and mutation
   attempts by read-only users.
6. Rerun exact/changed PoA activation and downgrade races twice on PostgreSQL. Assert one terminal
   winner, zero success evidence for losers, and exact audit/version/workflow/request identities.

## Test Cases

- Module-location/dependency AST checks and retained-table/migration-state regression.
- Public ₹500 success plus missing/low/high amount activation failures with zero writes.
- Full source read-role/object-scope matrix and read-does-not-mutate/reveal/download assertions.
- Existing current-maker, secondary-role attorney, terminal replay/downgrade, consumed-evidence,
  projection rollback, public-generation, legacy, and PostgreSQL race matrices remain green.

## Evidence Required

Failing/green PoA amount and read-role regressions, module/dependency proof, retained migration proof,
public API examples, twice-run PostgreSQL races, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- PoA policy is implemented by the source-defined deep owner without a forwarding shell.
- An active PoA cannot exist without the source-required exact ₹500 stamp and notarisation.
- Every source-authorised read-only role can read only canonically scoped masked metadata.
- All configured and declared capability gates pass.

