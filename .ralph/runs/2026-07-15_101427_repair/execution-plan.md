# Execution Plan

Selected slice: 008K4-current-evidence-and-security-read-closure

## Demonstrated failure

- Preserve the quarantined 008K4 implementation and repair only the independent validation
  failures recorded in the original run.
- The deterministic feedback command is
  `"/Users/amitkallapa/LMS/.ralph/venv/bin/python" sfpcl_credit/manage.py makemigrations --check --dry-run`.
  It fails because `applications.0016` applies two `AddField` operations to
  `applications.ChecklistAction`, while the model is owned by `legal_documents`.
- The independent PostgreSQL acceptance log fails at the same migration before running its five
  predicates. The slice's focused generation races already pass. The remaining artifact failure is
  the unfilled original risk-assessment template.

## Repair sequence

1. Keep the single-migration diff limit and correct the two cross-app migration operations so their
   state and database work target `legal_documents.ChecklistAction` after the declared
   `legal_documents.0012` dependency.
2. Re-run the migration feedback command, apply the full migration chain to a fresh test database,
   and run the focused 008K4 tests using the mandated backend interpreter.
3. Re-run the declared PostgreSQL acceptance/generation race commands when the configured local
   PostgreSQL capability is available; capture exact environment and twice-run results.
4. Run all configured backend and frontend gates. Do not alter the existing 008K4 product behavior
   unless a gate demonstrates a new failure.
5. Replace repair and original-run artifact templates with honest risk, review, changed-file, and
   final summaries; update Ralph state/progress/handoff and the selected slice only after gates pass.
   Verify the already sharpened 008L3 and 008M files remain concrete and dependency-correct.

## Constraints

- No protected/source/frontend changes, no new dependency, no additional migration file, and no git
  add/commit/push.
- Use `apply_patch` for edits and the orchestrator-managed Python interpreter for every backend
  command.
