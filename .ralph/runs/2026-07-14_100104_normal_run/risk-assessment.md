# Risk Assessment

Risk level: High

- Selected slice: 007T-register-null-contract-and-action-order-closure
- Mode: normal_run
- Standing approval: confirmed; no `[revoked]` entry exists for 007T.
- External side effects: none. No deployment, communication, network service, git write, database
  schema, backend business rule, permission grant, or production data mutation was introduced.

## Material risks and controls

- A valid historical S23 row could crash the register or tempt reconstruction from mutable live
  facts. Control: the DTO admits top-level null, the retained detail uses optional access only, and
  exact component/browser fixtures trace to the retained backend serializer integration test.
- A delayed post-action result could replace a newer S21 queue, detail, total, decision, denial,
  malformed-response, or empty state. Control: action POST/detail/decision/error projections share
  the existing queue/detail generation predicate; public UI tests cover every named outcome.
- Invalid mocked pagination could make ordering proof impossible in production. Control: non-final
  component pages now contain exactly 20 rows and browser pages already compute exact first/middle/
  final counts.
- Local screenshot execution is unavailable because Chromium is denied its macOS Mach-port rendezvous.
  Control: both declared specs collect, no screenshot was fabricated, and the orchestrator's required
  two independent localhost browser runs remain the acceptance authority.

## Residual risk

Low after independent browser acceptance. The change is limited to frontend contract typing,
null-safe rendering, request ordering, fixtures/tests, and Ralph documentation. Owner promotion from
`staging` to `main` remains outside this run.
