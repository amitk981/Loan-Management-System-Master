# Execution Plan

Selected slice: 008L2-member-portal-deficiency-response-and-resubmission

## Demonstrated failures

1. Two focused portal-deficiency tests expect a fabricated application reference even though the
   returned application fixture correctly has no reference before completeness passes.
2. The prior run's risk assessment is an unfilled template.
3. The slice changes 2,433 lines against a 2,000-line limit.

## Repair steps

1. Preserve the completed implementation and keep the focused two-test command as the deterministic
   feedback loop.
2. Align the two incorrect assertions with the source-defined pre-reference returned state: the API
   projects a null reference and the borrower-safe note falls back to the application UUID.
3. Reduce test-source verbosity while retaining the nine behavioral cases and their security,
   lifecycle, immutability, and Stage-4 non-interference assertions until the diff is within limits.
4. Fill both the quarantined normal-run and repair-run risk/review/summary artifacts, refresh
   changed-files evidence, and retain red/green terminal evidence.
5. Run the focused backend and frontend suites, then the required backend/frontend quality gates;
   record any sandbox-only browser limitation without fabricating screenshots.
