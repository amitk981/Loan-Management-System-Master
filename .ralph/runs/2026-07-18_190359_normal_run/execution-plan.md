# Execution Plan

Selected slice: 009H8-communications-worker-runtime-and-crash-recovery-closure

1. Copy the architecture-review runtime probe into focused communications tests and make the
   configured Celery app, explicit task registration, periodic schedule, and transactional
   enqueue contract fail first. Save the RED output.
2. Add the pinned Celery application/configuration and a thin task interface. Schedule newly
   created generic/advice jobs only with `transaction.on_commit`, keeping HTTP requests free of
   provider calls and rollback free of task publication.
3. Add one communications migration for a bounded claim lease and durable recovery evidence.
   Deepen `CommunicationDispatcher` so due selection, atomic claim, stale-running recovery,
   legacy-partial exclusion, retry/exhaustion, accepted-evidence replay, and safe operator
   projection remain behind its existing interface.
4. Add tracer-bullet tests one behavior at a time for generic/advice eager execution, retries,
   exhaustion, stale recovery, crash-before-provider, post-acceptance recovery, acknowledgement
   and retry-scheduling failures, and safe legacy/operator evidence. Save focused GREEN output.
5. Extend PostgreSQL acceptance with twice-run five-worker claim and stale-recovery races, then run
   the declared focused race set twice with the Ralph interpreter and save both logs.
6. Run focused backend tests, Django check, migration sync, compilation, and the unchanged frontend
   typecheck/lint/tests/build gates. Do not run the complete backend suite or coverage locally.
7. Record traceability and evidence, update the Epic 009 digest, API/operational contract notes if
   affected, state/progress/handoff/slice status, sharpen the next one or two eligible Not Started
   slices only if their existing requirements are materially incomplete, and delegate commit to
   the orchestrator.
