# Execution Plan

Selected slice: 006G3-sanction-handoff-dependency-and-evidence-ownership

1. Add failing static and API/module tests proving there are no production `credit -> approvals`
   imports, approvals does not import credit-private error/access implementations, and create/read
   return the exact workflow event durably linked to the pending case.
2. Move sanction orchestration to the public approvals handoff transaction. Expose the minimum
   reviewed-appraisal preparation/finalization interface from credit, move cross-app errors and
   application-access input to a lower shared module, and keep the HTTP adapter thin.
3. Persist the handoff workflow-event identity on `ApprovalCase` with one migration, create the
   event and case atomically, and serialize only that stored event on submission and reload.
4. Strengthen rollback and PostgreSQL race assertions, run the scoped tests red then green, run
   the five PostgreSQL races twice, and execute every configured backend/frontend quality gate.
5. Save self-contained evidence, changed-files/risk/review/final artifacts, update contracts and
   durable working docs if affected, sharpen the next eligible slices from already-open sources,
   and mark the selected slice/state/progress/handoff complete only after green gates.
