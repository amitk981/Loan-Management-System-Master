# Execution Plan

Selected slice: 010MB-interest-and-monitoring-frontend-wiring
Mode: same-worktree repair

1. Preserve the existing candidate and use the prior trusted-browser log as the bounded failure signal.
2. Reproduce the failing S44 allocation assertion and S50-S52 Monitoring navigation scenario with
   narrow Playwright runs, then inspect only the declared spec and the existing navigation/UI seams
   needed to distinguish stale assertions from candidate defects.
3. Fix only the demonstrated trusted-browser validation domain. Do not change unrelated product
   behavior or broaden the selected slice.
4. Rerun the exact declared Playwright spec until it passes, retaining both declared screenshots;
   repeat the full contract for the second independent pass.
5. Save repair evidence, record the browser-contract risk assessment, and set the review packet
   result exactly to `Ready for independent validation`.
