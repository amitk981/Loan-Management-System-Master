# Execution Plan

Selected slice: 009H9C-communication-channel-interface-and-provider-evidence-closure

## Repair boundary and permissions

- Preserve the quarantined 009H9C implementation and fix only the independently demonstrated
  `NotificationApiTests.test_send_communication_creates_staff_notification_for_user_recipient`
  regression (`400` instead of `200`).
- Work only in the already changed communications/process/test scope and this repair run's evidence
  folder. These paths are allowed by `.ralph/permissions.json`; do not touch protected files,
  source documents, frontend code, state/progress/status bookkeeping, or unrelated slices.
- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command. Do not run the full
  backend suite or coverage locally; Ralph owns the authoritative complete revalidation.

## Diagnosis and TDD loop

1. Run the exact failing notification API test and save its RED output under
   `evidence/terminal-logs/`; this is the deterministic regression loop for the reported symptom.
2. Inspect only that test's request fixture and the changed public communications validation/send
   path. Rank falsifiable causes, then probe the smallest seam that distinguishes them.
3. Reuse the existing failing test as the regression test and apply the smallest fix that preserves
   009H9C channel/template/recipient coherence and zero-write validation guarantees.
4. Re-run the exact test GREEN, then run the focused notification and communication-channel test
   labels that cover the changed seam. Save all results in this repair run.

## Completion and evidence

- Run Django system check and migration sync only if the fix touches production behavior; do not
  duplicate the complete backend coverage gate.
- Inspect targeted diff hunks and confirm no protected, forbidden, or unrelated paths changed.
- Replace the repair placeholders in `risk-assessment.md`, `review-packet.md`, and
  `final-summary.md` with the diagnosis, verification, residual risk, and independent-validation
  handoff. Leave commit, merge, push, slice status, state, progress, and mechanical handoff to Ralph.
