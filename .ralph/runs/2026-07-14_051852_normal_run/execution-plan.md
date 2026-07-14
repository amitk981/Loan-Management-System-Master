# Execution Plan

Selected slice: 007Q-register-source-fields-and-visual-evidence-closure

1. Extend the credit-owned `approval-review-v2` snapshot with folio and requested loan type so S23
   never reconstructs them from mutable member/application rows. Add public API tests first for the
   complete S23 projection, terminal null semantics, frozen action/communication evidence, and S25
   borrower/impact/requester/date facts; save each failing and passing run under
   `evidence/terminal-logs/`.
2. Add one approvals migration and the minimum model/service changes needed to persist the new
   immutable register facts. Generate the terminal team communication before the S23 row inside the
   existing transaction and copy its pending/sent facts into the register; preserve zero-write
   rollback behavior. Keep A-079-owned values explicitly null/empty.
3. Extend the shared frontend DTOs and existing S23/S25 register composition. Reuse the current
   card/table/detail styling, placing formal/source facts, immutable approver comments/times, and
   supporting metadata in vertically readable row-detail blocks while retaining strict shared
   pagination and never deriving document download actions.
4. Update component tests and the two declared Playwright specs test-first. Generate exactly
   `credit-sanction-register-source-fields.png`, `exception-register-source-evidence.png`, and
   `exception-register-document-denied.png`; assert the evidence blocks are within 1280x720 and add
   pixel-level rejection of large opaque/blank capture corruption. Collect the specs locally and
   attempt the trusted browser run without fabricating screenshots if Chromium is sandbox-blocked.
5. Update the API contract/digest traceability, run all configured backend/frontend gates, review
   the diff against the slice and design rules, then write the Ralph evidence/artifacts and update
   the selected slice, state, progress, and handoff. Sharpen the next one or two Not Started slices
   only from source material already opened.

Risk controls: no live-row reconstruction, no register mutation endpoint, no inferred document
action, one migration maximum, no new dependency, no protected/source-file edits, and stay below
the configured 30-file/2,000-line diff limits.
