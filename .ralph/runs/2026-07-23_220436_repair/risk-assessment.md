# Risk Assessment

Risk level: Medium (inherited slice); Low repair delta.

## Repair scope

- Selected slice: `011O-auditor-read-only-views`
- Mode: same-worktree repair
- Demonstrated validation domain: backend complete-suite coverage
- Repair delta: one legacy test fixture now creates the auditor's required active
  `audit_readonly` scope grant
- Production, schema, routing, frontend, dependency, and source-document changes in this repair:
  none

## Demonstrated failure and mitigation

The authoritative coverage run failed in the `internal_auditor` row of the global compliance-search
permission matrix. Slice 011O correctly added a persisted-scope guard to compliance reads, but the
pre-existing test constructed a fresh auditor role with read permissions and omitted the now-binding
`ApprovalCaseReadScopeGrant`.

The repair grants `SCOPE_AUDIT_READONLY` to that exact test actor's role. It does not bypass or weaken
the production guard. Adjacent tests continue to prove that an auditor with an inactive scope receives
403 responses.

## Residual risks

- Future test actors that model Internal Auditor reads must create both the relevant read permissions
  and the persisted `audit_readonly` scope. Omitting either should continue to fail closed.
- The macOS Codex shell runs under Rosetta while the pinned virtualenv extensions are arm64.
  Multiprocessing coverage therefore requires the established `PYTHONEXECUTABLE` wrapper handoff.
  This affects local validator execution only; the unchanged authoritative script and arguments passed.

## Verification

- Exact failing behavior test RED, then GREEN.
- Adjacent global-search and 011O auditor scope matrix: 11 tests passed.
- Exact six-worker backend coverage validator: 1,728 tests passed, 175 skipped, 0 failures/errors.
- Coverage: 89%, above the required 85% floor.
- `git diff --check`: passed.
