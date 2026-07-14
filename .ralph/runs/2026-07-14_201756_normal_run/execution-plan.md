# Execution Plan

Selected slice: 008F2-security-instrument-boundary-and-poa-lifecycle-closure

1. Establish the source-defined `security_instruments` app as the sole model/module/view owner of
   the retained `security_packages` and `power_of_attorneys` tables. Use one state-only migration so
   table names, constraints, primary keys, foreign keys, rows, and public URLs remain unchanged;
   add dependency guards proving that `legal_documents` does not import security policy.
2. Add a narrow approval-owned selector for canonical latest-cycle frozen terminal sanction facts,
   then require that fact plus the matching Stage-4 checklist scope for package reads and refreshes.
   Preserve authority-first handling and nondisclosing absent/wrong-stage/stale/unrelated outcomes.
3. Drive PoA behavior one RED/GREEN tracer at a time through public APIs: Compliance-only draft
   creation/material changes and current-maker handoff; exact-draft Company Secretary activation;
   active terminal replay/downgrade protection; secondary-role attorney resolution; bounded
   affirmative purpose validation; and durable action-envelope identity.
4. Freeze activation evidence for the exact renderer/file, stamp/notary maker-checkers, borrower and
   nominee signatures/makers, PoA maker/checker, and request/network/role/team identities. Guard the
   linked legal stamp/notary/signature mutation seams so an active PoA cannot be invalidated, with
   every rejected mutation remaining atomic.
5. Replace the manual positive fixture with public legal-document generation and retain twice-run
   PostgreSQL changed-activation and downgrade races. Save each meaningful RED/GREEN cycle and the
   scoped/full gate output under this run's `evidence/terminal-logs/`.
6. Run the focused backend tests during development, then Django check, migration sync, the complete
   coverage suite, and all frontend build/typecheck/lint/test gates. Finish the Ralph artifacts:
   changed-files, risk assessment, review packet, final summary, state/progress/handoff, selected
   slice completion, and concrete sharpening/digest updates for the next one or two Not Started
   slices using only source material already opened.
