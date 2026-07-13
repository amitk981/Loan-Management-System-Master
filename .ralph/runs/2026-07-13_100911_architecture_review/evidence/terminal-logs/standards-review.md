# Standards Review

Independent read-only review of `git diff 1752bcb...HEAD`:

- **Hard — object-scope data leak.** `approvals/views.py` checks only
  `approvals.case.read`; `approval_case_engine.py` returns every routed case unless
  `assigned_to_me=true` and retrieves any routed case without assignment/global-scope enforcement.
  The added test explicitly grants an unassigned reader access. This violates
  `auth-permissions.md` §§24.1, 32.1, and 37.3's explicit “Director views unassigned approval case
  | Denied.”
- **Hard — mutable review facts conflict with snapshot guidance.** Approval detail reads selected
  facts from live application, appraisal, and risk rows, and a test codifies later-row changes in
  the response. API contracts §3 says borrower details, loan limits, sanction terms, and approval
  matrix are snapshotted at decision time. Main-review disposition: retained as a judgment/phase
  boundary because normal appraisal writes are closed after submission, 007C explicitly requires
  owner read-through, and final sanction-decision snapshots belong to 007D; 007C2 must nevertheless
  prove public owners cannot mutate the reviewed facts after routing.
- **Hard — conflict and maker-checker rules are not yet applied.** Enrichment currently stores no
  exclusions and read actions use assignment plus permission only. Main-review disposition: not a
  007B/007C defect because both completed slices explicitly defer conflict population and action
  denial to already-sharpened 007E; the finding remains a required downstream gate.
- **Hard — §25.2 response drift.** The enrichment serializer returns `submission_status`, not the
  source response's `current_status`. This is included in corrective slice 007C2.
- **Hard — schema mismatch.** Approval-case related-entity fields remain nullable and digital
  signature is an unconstrained UUID. Main-review disposition: the nullable case shell is governed
  by A-059 until enrichment and A-077 explicitly defers the signature FK until its owning aggregate;
  neither is an unrecorded current defect.
- **Judgment — shallow/duplicated seam and weak tests.** Sanction handoff and approval-case reads
  have divergent serializers despite codebase-design §13.1/§27.1 assigning the boundary to a deep
  Approval Case Engine. Separately, `test_member_authority_action_matrix.py` repeats one evaluator
  test under ten names without invoking those public actions, contrary to §§26.1 and 42.1.

