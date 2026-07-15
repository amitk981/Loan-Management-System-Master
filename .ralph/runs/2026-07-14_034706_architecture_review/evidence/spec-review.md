# Independent Spec Review

Review range: `d106e16...eab8b0d` (007K, 007L, 007M, 007N).

The spec pass independently compared implementation, tests, retained browser evidence, slice
contracts, Epic 007, and cited functional/API/auth/data-model/screen sections.

## Findings

- **Critical:** final approval creates the sanction decision from mutable appraisal-note fields and
  register generation reads mutable application/member/appraisal fields. Existing tests mutate only
  after terminal generation. Corrective: 007O.
- **High:** S23 omits formal entry/folio, loan type/purpose, per-approver dates, rejection reason,
  conditions, and communication date/status. Corrective: 007Q.
- **High:** S25 omits borrower, financial impact, requested-by, and decision date. Corrective: 007Q.
- **High evidence:** genuine two-run browser outputs contain opaque regions or leave claimed right-
  side register evidence outside the viewport; both 007M PNGs are byte-identical. Corrective: 007Q.
- **High:** S21 trusted fixtures accept a non-paginated response and prove neither total nor page
  navigation. Corrective: 007P.
- **Medium:** S71 remains source-partial for rule name, abstention, special-case, and Board-reference
  semantics, but no current API/model owns those facts; no business rule was invented.

M05-FR-007 is reopened pending 007O; M05-FR-006 and M05-FR-009 remain partial pending 007Q/007O.
M05-FR-001..005, 008, and 010..012 remain substantive.
