# Evidence Index — 009H3BA

- `terminal-logs/red-communications-owner.txt` / `green-communications-owner.txt`: owner seam TDD.
- `terminal-logs/red-outbox-crash-window.txt` /
  `green-outbox-crash-window-attempt-1.txt`: durable pre-provider outbox and accepted-result recovery.
- `terminal-logs/red-outbox-template-drift.txt` / `green-outbox-template-drift.txt`: complete frozen
  template-provenance binding.
- `terminal-logs/green-dispatcher-adapter-contracts.txt`: Manual/Fake/Future identity plus
  rejection, malformed-result, and retry behavior.
- `terminal-logs/red-retained-provider-result.txt` / `green-retained-provider-result.txt`:
  accepted-outbox provider-result revalidation.
- `terminal-logs/green-advice-owner-suite-focused.txt`: complete focused owner/public smoke set.
- `terminal-logs/backend-static-gates.txt`: Django check, migration sync, compile, whitespace,
  protected paths, and diff scope.
- `terminal-logs/diff-and-protected-scope.txt`: exact candidate counts and protected-path result.
- `dependency-graph.md`: one-way executable dependency and retained transitional ownership.

The two RED crash/template logs reproduce the actual failing-first outputs retained by the
slice-cited oversized run `2026-07-18_022416_normal_run`; BA transplanted those exact tests and
re-ran their named GREEN commands in this bounded successor. No screenshot or browser evidence is
required because the slice is backend-only and declares no browser runtime capability.
