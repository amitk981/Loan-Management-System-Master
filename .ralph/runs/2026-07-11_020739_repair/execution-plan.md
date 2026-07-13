# Execution Plan

Selected slice: `006H2-workbench-action-contract-hardening` (repair)

1. Use the newest failed run summary and leftover worktree to reproduce the exact artifact failure,
   verify the prior gated implementation, and compare its changes with this fresh worktree.
2. Restore the focused interaction and API regression tests first, then run the narrow Vitest
   command to capture RED against the current production code.
3. Restore only the selected slice's implementation: writable response-to-draft projection,
   shared authenticated envelope handling, canonical sanction-case reload/state, and backend
   action plus current-user usability gating. Run the focused command to GREEN.
4. Verify the real Workbench action matrix, exact request bodies, malformed/field/stale errors,
   one-call `409`, sanction UUID/status reload, and static no-mock/no-formula protections.
5. Run all configured frontend and backend gates, using
   `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command, and save logs under
   this run's `evidence/terminal-logs/`.
6. Replace every run-artifact template completely, scan for placeholder markers, record changed
   files and honest High-risk controls, update slice/state/progress/handoff/digest, and sharpen the
   next one or two Not Started slices only if existing opened material adds concrete requirements.
7. Confirm protected files are untouched and configured file/line/dependency/migration limits are
   respected. Do not commit, add, push, install dependencies, or modify source documents.
