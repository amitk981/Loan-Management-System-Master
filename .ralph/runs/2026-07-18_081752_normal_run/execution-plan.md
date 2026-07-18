# Execution Plan

Selected slice: 009H3BA-communications-dispatcher-outbox-freeze

1. Preserve `DisbursementWorkflow.send_advice` and the public HTTP contract while moving template
   resolution, exact variable/sensitive-value validation, rendering, outbox reconciliation,
   adapter dispatch, and provider-result validation behind the deep
   `communications.modules.communication_dispatcher` interface. Disbursements will retain
   authority, locked financial context, and the existing final-ledger transaction through a
   frozen primitive context; communications will not import disbursement code or save supplied
   disbursement objects.
2. TDD tracer bullet: add the ownership test first and capture the named RED output. Implement the
   module/seam just far enough to make ownership green, removing duplicate executable template,
   render, outbox, and dispatch policy from `disbursement_advice`.
3. Add the provider-acceptance crash-window test next. Capture RED, then make the unchanged 009H3A
   outbox commit before dispatch, retain accepted provider truth there, and recover an exact retry
   with a fresh adapter without another logical message.
4. Add template-provenance drift coverage next. Capture RED, then freeze and reconcile template
   identity/name/type/language/audience/version/approval/effective range/declared variables/source
   templates/checksum plus recipient, render, payload, and related entity before redispatch.
5. Complete focused Manual/Fake/Future contract coverage for exact replay, changed payload,
   rejection/retry, malformed results, accepted-result recovery, and stable provider identity.
   Preserve existing final receipt/Communication/audit/workflow behavior as the bounded
   disbursement-owned consumer that 009H3BB will remove.
6. Run focused communications/advice tests, Django check, migration sync, dependency/static checks,
   protected-path inspection, and diff-limit review with the mandated Ralph Python interpreter.
   Do not run the complete backend suite or frontend gates because no frontend change is planned.
7. Finish evidence and Ralph artifacts: changed files, risk assessment, review packet, final
   summary, slice status, state, progress, handoff, and Epic 009 digest. Recheck the next one or two
   Not Started slices already covered by the opened digest and sharpen only if incomplete. Leave
   commit, merge, and push to the orchestrator.
