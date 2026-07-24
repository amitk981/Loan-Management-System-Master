# Execution Plan

Selected slice: 012E2-tracer-and-demo-route-production-isolation

## Scope and permissions

- Work only in `sfpcl_credit/**`, `sfpcl-lms/src/**`, allowed working documentation, and this run folder.
- Do not edit protected configuration, scripts, source documents, orchestrator-owned state/progress,
  the selected slice status, or Git metadata.
- Preserve the existing development tracer proof while making production settings/builds fail closed.

## Behavior-first implementation

1. Add one backend production-settings behavior test proving tracer URLs are unregistered, then
   minimally centralize the demo-surface setting and gate the tracer app/URL import.
2. Add the next backend behavior test proving predictable demo/E2E seeds refuse under production
   settings, then make both commands consume the centralized non-production setting.
3. Add frontend behavior tests proving production mode cannot render tracer navigation/route,
   demo role switching, or portal demo fallback, while development mode retains explicitly enabled
   tracer/demo behavior.
4. Move tracer/demo imports behind the centralized frontend environment module so a production Vite
   build can eliminate those modules; retain a route/navigation guard for defense in depth.
5. Run focused backend and frontend red/green tests, backend checks/migration sync, frontend
   typecheck/lint/build, and inspect the production bundle for tracer APIs/demo identities.
6. Update A-011 and the current run’s evidence, risk assessment, review packet, and final summary.
   Set the review result exactly to `Ready for independent validation`.

## Required evidence

- Focused backend RED/GREEN logs.
- Focused frontend RED/GREEN logs.
- Development tracer regression output.
- Production build/static exclusion output.
- Check/typecheck/lint/build outputs and a concise inventory/traceability review packet.
