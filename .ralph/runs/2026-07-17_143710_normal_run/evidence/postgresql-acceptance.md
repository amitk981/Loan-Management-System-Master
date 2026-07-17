# PostgreSQL Acceptance

The test module declares two independent five-caller methods in
`DisbursementAdviceRaceTests`. Each requires five simultaneous exact advice attempts to return one
retained communication id while recording exactly one adapter acceptance, communication, audit, and
workflow event.

The local attempt collected both tests but the managed sandbox denied the PostgreSQL Unix socket
with `Operation not permitted`; see `terminal-logs/postgresql-five-race-run-1.log`. No screenshot or
result was fabricated. The slice declares `postgresql-five-race-acceptance`, so the orchestrator must
run the class twice outside the sandbox and treat that independent gate as authoritative.
