# PostgreSQL Five-Caller Advice Race

The declared PostgreSQL capability was exercised locally after SQLite collection. The first run
found and retained a genuine PostgreSQL lock error caused by locking a nullable joined terms row.
The repair narrowed the lock to `LoanAccount` itself while retaining the related terms read.

After repair, two independent PostgreSQL executions each ran both five-caller methods successfully.
Every method asserts one logical provider call/identity, one protected communication using the
stable pending UUID, one sent intent/link, one audit, and one workflow event, with all callers
receiving the same communication identity.

- RED: `terminal-logs/postgresql-advice-race-1.log`
- GREEN 1: `terminal-logs/postgresql-advice-race-green-1.log`
- GREEN 2: `terminal-logs/postgresql-advice-race-green-2.log`

