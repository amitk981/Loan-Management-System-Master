# Effective Period Boundary Matrix

| Calculation date | Approved history | Result |
|---|---|---|
| 2026-07-31 | First version begins 2026-08-01 | Fail closed: no effective rate |
| 2026-08-01 | RATE-2026-01, 9.2500 | RATE-2026-01 |
| 2026-08-31 | RATE-2026-01 closed by successor | RATE-2026-01 |
| 2026-09-01 | RATE-2026-02, 9.7500 | RATE-2026-02 |
| 2027-01-01 | RATE-2026-02 remains open | RATE-2026-02 |

The public resolver returns one immutable `EffectiveRate` value or raises a missing/ambiguous-rate
exception. It does not choose a caller-supplied "current" rate. An open predecessor is closed at the
day before an approved successor, with a separate append-only period-closure history/audit record.
An explicitly closed predecessor accepts only a successor beginning on the immediately following
day, so no gap can be silently filled with a fabricated rate.

Evidence: `terminal-logs/period-closure-history-red.log` and
`terminal-logs/period-closure-history-green.log` retain the RED/GREEN cycle; the complete focused
matrix remains green in `terminal-logs/final-focused-gates.log`.
