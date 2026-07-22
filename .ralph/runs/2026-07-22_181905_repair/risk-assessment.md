# Risk Assessment

Risk level: High

- Selected slice: `011F-recovery-action-execution-shell`
- Mode: repair
- Manual review required: yes; independent Ralph validation owns the authoritative browser and
  High-risk backend lanes.

## Repair scope and controls

- Validation domain stayed limited to trusted browser acceptance. The quarantined backend,
  financial-posting, security-owner, migration, and S57 product candidate was preserved.
- Empty browser fixtures now follow the shared pagination invariant: an empty collection still has
  one logical page. This prevents a malformed-response error from replacing the required blocked UI.
- Canonical `recovery.action.initiate` and `recovery.action.complete` permissions map to the existing
  `manage_defaults` compatibility gate. This changes navigation visibility only; backend authority,
  object scope, and `available_actions` remain the mutation controls.
- No protected file, source document, dependency, migration, styling pattern, external integration,
  or business rule was added.

## Verification and residual risk

- Focused Vitest: 40/40 passed across `authSession.test.ts` and
  `DefaultRecoveryHub.test.tsx`.
- Frontend typecheck, lint, and production build passed.
- The declared Playwright file collects exactly two tests after the repair.
- The agent sandbox cannot launch the macOS system Chrome process. No screenshots were fabricated;
  Ralph's trusted post-agent validation must run the spec twice and verify both declared PNGs.
- Product changed-line accounting is expected to be 1,999 lines: the prior validated 1,997-line
  candidate plus two one-line regression/mapping additions, within the 2,000-line limit.
