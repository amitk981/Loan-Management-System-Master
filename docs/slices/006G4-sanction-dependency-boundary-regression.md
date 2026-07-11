# Slice 006G4: Sanction Dependency Boundary Regression

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Make 006G3's architecture regression prove every import form promised by its slice so the removed
credit/approvals cycle cannot return through package aliases or a new private-module path.

## Depends On
- 006G3

## Source / Review References
- `docs/source/codebase-design.md` §12.3, §13.1, and §36.2
- `docs/adr/ADR-0005-approval-case-module-owns-sanction-handoff.md`
- `docs/slices/006G3-sanction-handoff-dependency-and-evidence-ownership.md`
- `docs/working/REVIEW_FINDINGS.md` entry for architecture review `2026-07-11_135129_architecture_review`

## Scope

- Replace the narrow import-name collector with a package-aware resolver that recognizes
  `import x.y`, `import x.y as z`, `from x import y`, `from x import y as z`, and imports exposed
  through package `__init__` modules.
- Reject every production `credit -> approvals` dependency. On the approvals side, use an explicit
  allowlist of documented public credit handoff interfaces; reject private credit common/error/
  implementation modules rather than checking only one literal module name.
- Add positive and negative synthetic AST fixtures for direct, aliased, package-level, and allowed
  public imports so the guard cannot pass vacuously.
- Preserve 006G3's production dependency graph, sanction behavior, exact case/event identity,
  transaction boundaries, and five PostgreSQL outcomes; no production behavior change is expected.

## Test Cases

- Package/alias fixtures fail for `credit -> approvals` and approvals-to-private-credit imports.
- The documented approvals-to-public-appraisal interface passes.
- Repository scan reports zero production violations and positively observes the intended public
  approvals-to-credit edge.
- Existing sanction module/API/concurrency suites remain green.

## Evidence Required

Failing-first synthetic fixture output, green repository scan, dependency graph, focused sanction
suite, and all configured gates.

## Risk Level
Medium

## Acceptance Criteria

- The dependency guard detects every import syntax named by 006G3 and cannot pass without observing
  the intended public edge.

