# Browser Status

- `--list` collects exactly two tests in the declared spec.
- Local Chromium launch reaches both test registrations, then macOS denies Mach-port registration
  before either body executes. See `terminal-logs/playwright-local-run.log`.
- No screenshot or baseline was fabricated or copied from either failed worktree.
- Trusted run 1 creates absent one-line encoded baselines from current frames and compares them
  immediately. Trusted run 2 decodes and compares those exact bytes. Both must emit all twenty
  declared evidence screenshots.
