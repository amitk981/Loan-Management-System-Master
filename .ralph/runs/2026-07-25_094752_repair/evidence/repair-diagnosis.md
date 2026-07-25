# Critical UAT DPD Cutoff Repair Diagnosis

## Authoritative symptom

The orchestrator-owned trusted-browser run launched Chrome, completed the public disbursement,
direct repayment, subsidiary repayment, and interest-invoice actions, then failed at the DPD
assertion. For `as_of_date=2026-07-01`, the API returned `principal_overdue_amount=400000.00`
while the scenario expected `300000.00`.

The later retained Chrome failures ended during `browserType.launch` before a page existed. They
are infrastructure evidence and do not override the first post-launch application assertion.

## Tight feedback loop

The exact existing regression
`DpdPaymentTimingApiTests.test_later_posted_repayment_does_not_reduce_earlier_snapshot` exercises
the public DPD calculation after a repayment posted later than the requested cutoff. It proves
that a later posting cannot reduce an earlier snapshot.

The critical-UAT seed tests additionally exercise the guarded deterministic seed and its public
subsidiary-repayment and interest-invoice preconditions.

Current evidence: `terminal-logs/dpd-cutoff-and-seed-green.log` — 3 tests passed.

## Ranked hypotheses

1. **Stale E2E cutoff expectation — confirmed.** Both repayments are dated `2026-07-25`; neither
   can reduce principal paid as of `2026-07-01`. The correct overdue amount is the full scheduled
   `400000.00`.
2. **Production DPD cutoff bug — disproved.** The canonical public-API timing regression passes and
   requires the later repayment to affect only the later snapshot.
3. **Incorrect seeded principal/schedule — disproved.** The seed regression requires a
   `400000.00` schedule, and the public direct-repayment response separately proves that the later
   allocation reduces current principal to `300000.00`.
4. **Browser infrastructure caused the authoritative failure — disproved.** The authoritative run
   reached the application assertion. Current retries and `e2e:probe` fail before page creation and
   are therefore a separate infrastructure condition.

## Repair retained in the candidate

The E2E scenario now:

- expects `400000.00` overdue at `2026-07-01`;
- asserts the schedule line has `400000.00` principal due and `0.00` principal paid as of that
  cutoff; and
- retains the independent assertion that the `2026-07-25` direct allocation reduces current
  principal to `300000.00`.

No production financial logic, endpoint, permission, model, migration, or UI behavior changed.

## Verification

- Focused backend DPD/seed behavior: `terminal-logs/dpd-cutoff-and-seed-green.log`
- Frontend seed selection: `terminal-logs/frontend-seed-focused-green.log`
- TypeScript: `terminal-logs/frontend-typecheck.log`
- ESLint: `terminal-logs/frontend-lint.log`
- Production build: `terminal-logs/frontend-build.log`
- Django system check: `terminal-logs/django-check.log`
- Migration drift: `terminal-logs/migration-check.log`
- Exact browser attempts: `terminal-logs/trusted-browser-acceptance-green-1.log` and
  `terminal-logs/trusted-browser-acceptance-green-1-retry.log`
- Browser infrastructure probe: `terminal-logs/browser-infrastructure-probe.log`

The current browser attempts all ended before page creation, so this run did not fabricate or
claim new screenshots. Independent trusted validation owns the required two fresh browser runs and
screenshot manifests.
