# Execution Plan

Selected slice: `CR-010-backend-pending-age-parallel-ci-flake`

1. Make the two known approval-routing regressions deterministically cross a one-second boundary
   while retaining their current whole-payload assertions; run only those tests serially and save
   the expected RED output.
2. Change the assertions to remove only each response's live `pending_age`, compare every stable
   detail/queue/pagination field exactly, and assert the age label/display/monotonic elapsed values
   separately.
3. Add a backend-infrastructure regression for traceback pickling support, capture its RED result
   against the unpinned development requirements, then pin the already-available `tblib` version and
   capture GREEN output.
4. Run the focused approval-routing class serially, the impacted backend-infrastructure class,
   Django check, and migration-sync check with the mandated Ralph Python interpreter. Do not run the
   complete suite or any coding-agent parallel probe.
5. Save terminal evidence and required Ralph artifacts; inspect the diff and protected paths;
   sharpen the next one or two Not Started slices only if the already-opened digest adds concrete
   requirements not already present; update selected slice status, state, progress, and handoff.

TDD behaviors:

- Stable approval-case detail and assigned-queue fields remain exact across an advancing clock and
  live policy edit.
- Pending age remains a valid live, monotonically non-decreasing projection.
- Parallel test failure events retain the original assertion exception and traceback after
  serialization.
