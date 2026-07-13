# Review Window Evidence

- Fixed point: `1ff6cb86cbebaf2f66285cc5ccaa2502bf3ab241`
- Diff command: `git diff 1ff6cb8...HEAD`
- Product commits: `b9c8442` (005E4), `0ed9b32` (006H7), `dc5de3a` (006H3), `045f5d2` (006X)
- Excluded repository-only commit: `b2e8ac2` (Ralph retry policy)
- Production files changed by this architecture-review run: none

Evidence spot checks:

- 005E4 trusted browser logs report two passes and nine non-empty screenshots.
- 006H7 changed one shared loan-limit evaluator; its focused frontend test still uses
  `renderToStaticMarkup` and no mounted HTTP container.
- 006H3 `playwright-collection.log` reports `ReferenceError: Cannot access 'title' before
  initialization` and `Total: 0 tests in 0 files`; no screenshot/baseline exists.
- 006X browser spec routes every `/api/v1` request to fixtures; the run packet contains no screenshot.
