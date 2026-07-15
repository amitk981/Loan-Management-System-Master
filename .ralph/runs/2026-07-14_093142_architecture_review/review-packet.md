# Review Packet: 2026-07-14_093142_architecture_review

## Result

Success

## Slice and Range

Architecture review of `git diff 220f3038...e1698e87`, covering completed slices 007R, 007S,
008A2, and 008B. No production code changed.

## Standards

The independent Standards pass found that 008B places application/approval-aware generation in the
foundation documents app, reversing the source-defined legal-documents dependency direction. It
also found view-only generation/template authority that direct callers can bypass, collection query
and pagination work in the business module instead of a selector, and a raw UUID loan-account field
where the data model requires relational integrity. Corrective 008B2 owns these issues.

## Spec

The independent Spec pass found that 007R's exact legacy response returns top-level null purpose and
risk while 007S types/dereferences objects and masks the mismatch in tests. It also found an older
post-action refresh able to replace a newer S21 state and impossible pagination fixtures. Corrective
007T owns these issues. For 008B, PDF assertions prove metadata rather than parseable content and a
text file named DOCX stands in for a Word package; corrective 008B3 owns genuine bounded rendering
proof. A-101 records that real M05 decisions lack governed values for several mandatory Term Sheet
facts, so the real path must remain blocked rather than be claimed by a populated direct fixture.

## Traceability and Architecture Outcome

- Codebase-design §§6.3, 7.2, 14.1, and 36.2 already decide module authority, selector ownership,
  and legal-documents dependency direction; no new ADR is required.
- Data-model §16.3/§34 requires loan-account relational integrity; 008B2 permits only an honest
  database-enforced null deferral until the Epic 009 owner exists.
- API §§25.3/25.9 and 007R's public test establish the exact legacy-null register shape; 007T makes
  the UI/test/browser contract consume it without reconstruction.
- Functional §15.1 and M06-FR-013 require an actual legal document, so 008B3 extracts/asserts genuine
  Word and PDF content and separately preserves the missing-real-term blocker.
- 008C now depends on 008B3 and is sharpened to use an explicit atomic orchestration seam without
  making approvals depend on legal_documents. 008D consumes legal authority and never infers
  stamp/notary evidence from rendered output.

## Validation

- Frontend: build, typecheck, lint, and 287/287 tests pass.
- Backend: Django check and migration sync pass; 722 tests pass with 22 expected skips and 93%
  coverage, exceeding the 85% floor.
- Focused evidence: exact backend legacy-null test passes; 41 register/workbench component tests
  pass, demonstrating the current fixture mismatch remains hidden by the existing suite.
- Integrity: corrective runtime declarations, queue drain, state JSON, `git diff --check`, protected
  paths, and review-only scope pass.

## Recommended Next Action

Run 007T, then 008B2, then 008B3. Only then continue to sharpened 008C.
