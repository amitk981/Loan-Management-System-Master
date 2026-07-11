# Slice 006G5: Relative-Import Dependency Guard

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Make 006G4's architecture regression resolve relative imports against each scanned module so no
Python import syntax can reintroduce the forbidden credit/approvals dependency direction.

## Depends On
- 006G4

## Source / Review References
- `docs/source/codebase-design.md` §12.3, §13.1, and §36.2
- `docs/adr/ADR-0005-approval-case-module-owns-sanction-handoff.md`
- `docs/slices/006G4-sanction-dependency-boundary-regression.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_191720_architecture_review`

## Scope

- Resolve `ast.ImportFrom.level` and module/name components against the scanned file's package for
  `from .`, `from ..`, deeper-relative, aliased, package-`__init__`, and wildcard forms.
- Reject relative `credit -> approvals` imports and approvals imports of any private credit package,
  model, common/error, or implementation module. Continue to allow only the ADR-0005 public
  appraisal-workflow handoff.
- Make the repository scan pass each source file's concrete module/package context into the
  resolver and retain the non-vacuous required-public-edge assertion.
- Do not change production imports, sanction behavior, transactions, identities, or outcomes.

## Test Cases

- Failing-first fixtures for `from ..approvals import ...`, `from ... import approvals`, and private
  approvals-to-credit relative imports, including aliases and package exposure.
- Positive fixtures for same-package relative imports that do not cross a business-app boundary and
  the one documented public approvals-to-credit handoff.
- Repository scan reports zero violations and positively observes the exact public edge.
- Existing sanction API, module, rollback, and PostgreSQL acceptance suites remain green.

## Evidence Required

Failing-first relative-import fixture output, green syntax matrix, dependency graph, focused
sanction suite, and all configured gates.

## Risk Level
Medium

## Acceptance Criteria

- Absolute and relative imports receive the same canonical dependency classification.
- The dependency guard cannot miss a forbidden edge because it was written relative to a package.

