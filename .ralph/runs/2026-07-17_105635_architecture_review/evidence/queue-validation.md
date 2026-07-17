# Queue and Guardrail Validation

- PASS: `ralph_slice_queue_lint docs/slices` reports a parseable dependency graph that drains.
- PASS: first grabbable slice is `009E3-disbursement-amount-and-source-bank-governance-closure`.
- PASS: execution order is 009E3 -> 009F2 -> 009G.
- PASS: 009E3, 009F2, and 009G runtime capability declarations are valid.
- PASS: `.ralph/state.json` parses as JSON.
- PASS: `git diff --check` reports no whitespace errors.
- PASS: changed paths are limited to `.ralph/progress.md`, `.ralph/state.json`, this run packet,
  `docs/slices/**`, and `docs/working/**`; no protected or production path changed.
- PASS: no `Blocked` slice exists with a stale completed prerequisite.

