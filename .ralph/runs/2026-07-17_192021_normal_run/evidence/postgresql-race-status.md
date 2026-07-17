# PostgreSQL Race Status

The transfer race test module collects two PostgreSQL-only methods. Each method runs five changed
transfer-success contenders and then five changed checklist-signature contenders, asserting one
complete winner and four clean conflicts for each phase, including one transfer, register update,
pending advice intent, activation history, audit/workflow chain, and checklist action.

The local SQLite run collected both methods and skipped them as declared. No screenshots or race
results were fabricated. The slice declares `postgresql-five-race-acceptance`; the Ralph
orchestrator runs the authoritative PostgreSQL contract twice outside this sandbox.

Collection evidence: `terminal-logs/transfer-module-with-race-collection.txt`.
