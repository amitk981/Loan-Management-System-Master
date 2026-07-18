# Execution Plan

Selected slice: 009H9C-communication-channel-interface-and-provider-evidence-closure

## Boundary and permissions

- Work only in `sfpcl_credit/communications`, the thin `sfpcl_credit/processes` entrypoints,
  focused backend tests, the one permitted communications migration, API-contract/digest docs,
  and this run's evidence folder. These paths are allowed by `.ralph/permissions.json`.
- Do not change frontend code, protected files, source documents, state/progress/status bookkeeping,
  or unrelated future slices. No new dependency is expected.
- Preserve the H6/H8/H9B provenance, lease, recovery, exception-queue, and acyclic process seams.

## TDD tracer bullets

1. Copy the failing SMS-through-email behavior into the maintained communications tests and prove
   RED. Add a distinct SMS payload/result/adapter seam, channel/template/recipient validation, and
   fail-closed phone/courier handling until Email and SMS dispatch through only their own adapters.
2. Add one public-interface behavior at a time for malformed recipients, mismatched templates,
   forbidden SMS variables/rendered sensitive values, and manual/fake/future/no-provider modes;
   retain red/green terminal logs for each focused cycle.
3. Add public facade/replay tests proving production HTTP and worker callers cross
   `CommunicationDispatcher`, exact replays return the source §45.2 wrapper, and changed,
   cross-actor/object/channel key reuse remains zero-write.
4. Add generic provider-evidence tests, then one communications migration and implementation that
   freezes singular immutable accepted evidence bound to job, communication, channel, payload,
   key, result, and actor. Prove tamper rejection and crash replay without provider re-entry.
5. Move due-job iteration and task-safe evidence shaping behind the dispatcher so Celery tasks are
   thin wrappers; add static/runtime boundary tests while retaining H8/H9B behavior.

## Verification and evidence

- Run each focused Django test label with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, saving RED and GREEN output under
  `evidence/terminal-logs/`.
- Run the impacted communications/advice/worker/migration tests, `manage.py check`, and
  `makemigrations --check`; do not run the complete backend suite or coverage locally.
- Run the declared generic Email/SMS five-caller and five-worker PostgreSQL races twice if the
  local runtime permits them, saving both executions. Record any sandbox limitation honestly.
- Update `docs/working/API_CONTRACTS.md` and the selected epic digest with current asynchronous,
  replay, channel, and provider-evidence truth.
- Inspect targeted diffs and run a standards/spec review of the working-tree candidate. Finish
  `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; leave commit/state/status work
  to the orchestrator.
