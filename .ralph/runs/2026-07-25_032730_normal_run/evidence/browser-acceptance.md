# Trusted Browser Acceptance

Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`

The completed four-test contract covers S53-S68 and declares all five required outputs:

- `default-case-workbench.png`
- `recovery-approval-decision.png`
- `closure-readiness-blockers.png`
- `compliance-trackers.png`
- `grievance-resolution.png`

The terminal S68 test proves:

- a Company Secretary receives the grievance navigation and the backend-projected `resolve` action;
- empty status/reason submission is blocked;
- the exact resolution endpoint is the only mutation;
- canonical list state is refetched before success;
- the archive surface contains no mutation controls;
- manifest download performs exactly one audited archive-detail read.

Local execution was attempted twice with separate screenshot destinations. In both attempts Django
and Vite became healthy, then system Chrome aborted during launch before a page or test assertion
existed. Therefore no screenshots were produced or fabricated. Logs:

- `terminal-logs/trusted-browser-acceptance-1.log`
- `terminal-logs/trusted-browser-acceptance-2.log`

The contract is statically discoverable as four Playwright tests. Ralph's trusted independent
validator must rerun it twice in a browser-capable environment and retain the five screenshots from
each passing run.
