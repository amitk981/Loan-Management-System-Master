# Execution Plan

Selected slice: 006Y3-member-registry-and-identity-change-approval-closure

1. Reproduce the trusted-browser failure from the prior run logs and reduce it to the member
   update/history write that raises `TypeError: Object of type date is not JSON serializable`.
2. Add a focused backend regression test that updates a newly created individual member whose
   profile contains `date_of_birth`, proving the public Member Registry/API seam returns 200 and
   stores JSON-safe masked history; save the failing-first output.
3. Make the smallest history-normalization correction needed for date values, then rerun the
   focused test and the declared Playwright contract (or collection if Chromium is sandbox-blocked).
4. Run all required frontend/backend gates, save repair evidence and review artifacts, and update
   Ralph progress/state/handoff without widening the completed slice.
