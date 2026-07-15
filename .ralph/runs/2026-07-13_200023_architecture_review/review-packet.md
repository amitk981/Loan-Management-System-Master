# Review Packet: 2026-07-13_200023_architecture_review

## Result

Complete; findings are recorded, corrective slices are queued, and configured gates pass.

## Slice

architecture-review

## Review Window

`b32559c...78d912f`: 007E2, 007F, 007G, and 007H. The later docs-only `ac1846c` CR-004 intake
commit was excluded from completed product findings.

## Standards Review

- Critical: a real 007F exception enrichment persists an incoherent case because the projection
  compares the distinct approval and Exception Register business reasons for equality. Canonical
  selectors then hide the case and actions cannot route it.
- High: sanction-decision and Credit Sanction Register views turn named permissions into global
  object access, including unscoped counts and pagination.
- High: General Meeting recording accepts arbitrary existing document ids after only a global
  download permission check, without document-owned application/sensitivity scope.
- Medium architecture: appraisal `post_save` still mutates approval coherence/read projections,
  leaving a hidden cross-module writer after 007E2's explicit seam work.

## Spec Review

- Critical: the exception predicate trusts `exception_required_flag` even when the recommended
  amount is below the frozen eligible amount; the existing test blesses that contradiction.
- High: pending/rejected General Meeting outcomes are absent from canonical case detail until a
  final action is attempted.
- Medium: 007G's promised per-document access is not satisfied by global permission plus existence.

No material scope creep was found. Immutable register generation, conflict replacement/history,
final General Meeting gating, and terminal register references are otherwise substantive.

## Corrective Ownership

1. `007F2-exception-routing-coherence-and-explicit-projection-closure`
2. `007G2-general-meeting-current-evidence-and-document-scope-closure`
3. `007H2-sanction-decision-and-register-object-scope-closure`

007I now depends on 007H2; 007I/007J carry run-ahead contracts for current/frozen meeting evidence
and scoped register/sanction reads. No ADR was added because existing source/slice rules decide the
behavior. A-085 remains for 007G2.

## Traceability

- M05-FR-003/006 remain partial until 007F2; M05-FR-012 remains partial until 007G2.
- M05-FR-009 generation is substantive, but read confidentiality remains partial until 007H2.
- Auth §§15.9/19.2/32.1/37.3 require object scope before direct reads, counts, and pagination.
- API §§25.4/25.8/25.9/25.11 and data-model §§15.2-15.8 define the current/frozen evidence and
  register surfaces; codebase-design §§26/42 require public acceptance and explicit ownership.

## Validation

Independent Standards and Spec review evidence is retained. Frontend build/typecheck/lint and 208
tests pass. Backend check/migration sync pass; the full 669-test suite completes with 19 expected
PostgreSQL-only SQLite skips and 93% coverage. Queue/dependency lint, state JSON parsing, diff
whitespace, blocked-slice inspection, and changed-path checks pass. No production, protected, or
source file changed.

## Recommended Next Action

Run 007F2, then 007G2 and 007H2. Resume 007I only after the corrective chain completes.
