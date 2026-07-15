# Validation Interpreter Repair

The first local independent-validator invocation could not find a worktree-local virtual environment
and fell back to a system x86_64 Python. That interpreter attempted to load an arm64 CFFI extension,
so Django check, migration sync, and coverage stopped during JWT import. Frontend gates, artifact
quality, protected paths, status transitions, and queue lint had already passed.

The single repair attempt supplied a temporary worktree-local executable shim that delegated every
backend command to the owner-mandated arm64 project interpreter. The validator then passed Django
check, migration sync, all 773 backend tests with 24 expected skips, 93% coverage, and every frontend
and Ralph gate. The shim was removed immediately after validation; it is not part of the run diff.

This was an execution-environment architecture mismatch, not a dependency, production-code, test,
or review-artifact change.
