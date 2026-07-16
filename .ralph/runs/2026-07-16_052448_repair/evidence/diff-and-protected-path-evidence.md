# Diff and Protected-Path Evidence

- Tracked non-`.ralph` additions/deletions: 172 + 43 = 215 lines.
- Untracked Finance package: 700 lines.
- Untracked 009A test module: 562 lines.
- Measured implementation/documentation total: 1,477 lines.
- Configured maximum: 2,000 lines.
- Remaining budget: 523 lines.
- `git diff --check`: pass.
- Protected-path scan across tracked and untracked paths: no matches.
- Debug-marker scan across the Finance package and 009A tests: no matches.
- Slice-queue dependency/status lint: pass under Bash (the shell expected by the Ralph library).

Ralph run artifacts and the expected `.ralph/state.json`/`.ralph/progress.md` bookkeeping are not
included in the implementation diff budget.
