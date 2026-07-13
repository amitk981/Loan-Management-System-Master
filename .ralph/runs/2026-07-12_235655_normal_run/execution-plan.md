# Execution Plan

Selected slice: 006X9-credit-object-scope-isolated-execution-matrix

1. Capture the order-dependence defect by selecting the existing aggregate ledger test alone and
   save its failing output as red evidence.
2. Refactor only `test_credit_action_parity_matrix.py`: remove the process-global ledger and make
   the eight object-scope cases independently selectable tests driven by one explicit action table.
   Each case must execute the real six-field projection, matching public write, exact
   `OBJECT_ACCESS_DENIED` assertion, and complete before/after evidence comparison.
3. Add an isolated completeness contract that rejects deliberately incomplete rows without direct
   bookkeeping mutation, and prove normal/reversed selection produces the same eight substantive
   passing cases.
4. Run each focused row independently, focused HTTP 403 non-disclosure tests, dependency scans,
   backend/full configured gates, and frontend configured gates; save terminal evidence.
5. Update the Epic 006 digest, selected slice status, Ralph state/progress/handoff, and the run's
   changed-files, risk, review, and final-summary artifacts. Sharpen the next one or two Not Started
   slices only if the already-opened source/digest material adds concrete requirements.

No production credit code, API contract, schema, frontend, or dependency change is planned.
