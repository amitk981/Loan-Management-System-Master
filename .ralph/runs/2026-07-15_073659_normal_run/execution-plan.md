# Execution Plan

Selected slice: 008L2-member-portal-deficiency-response-and-resubmission

1. Freeze the source-backed interface and scope: active `PortalAccount.member_id` is the only
   authority; borrower reads expose correction text but no staff remarks; the canonical core
   lifecycle returns `incomplete_returned` to `submitted`, with resubmission identified by portal
   audit/workflow facts and therefore visible in the existing staff completeness queue.
2. Add one failing backend HTTP tracer for the own-member returned application: list/detail the open
   deficiency, upload a bounded PDF through a deficiency-owned immutable relation, respond, and
   resubmit atomically. Save the RED output before adding production code, then implement the
   smallest deep portal-deficiency module and route set to make that tracer green.
3. Repeat narrow red/green cycles for cross-member/session nondisclosure and denied-action audit,
   multipart category/sensitivity/type/size validation, mandatory-response blocking, invalid-state
   blocking, immutable re-upload provenance, authenticated content download, and the no-Stage-4-
   mutation regression. Keep uploads as intake evidence only and reuse the central document
   storage helper without reusing `PortalDocumentationSubmission`.
4. Update the working API contract and Epic 005 digest with exact endpoints, request/response
   shapes, status semantics, validation, audit/workflow events, scope, and nondisclosure behavior.
5. Add failing frontend transport and MP10/MP11 interaction tests for list/detail, upload progress,
   validation/auth/error/empty states, remarks, all-mandatory response gating, success, and one
   canonical refetch. Wire the existing portal application status screen using its established card,
   alert, badge, button, and responsive patterns; add no mock business data or new styling system.
6. Run focused backend and frontend tests during implementation, then migration sync, Django check,
   frontend lint/typecheck/tests/build, and the full backend coverage gate with the mandated Python
   interpreter. Save all terminal evidence and attempt local mobile browser capture without
   fabricating screenshots if sandboxed services cannot bind or Chromium cannot launch.
7. Review the diff against source, permissions, audit, design, mock-ratchet, cross-boundary, and
   diff-limit rules. Save API examples, changed-files, risk assessment, review packet, and final
   summary; update assumptions, digest, progress, handoff, state, and selected-slice status, then
   sharpen the next one or two Not Started slices using only already-opened source material.
