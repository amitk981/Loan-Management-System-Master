# Failure Summary

- Run: 2026-07-25_094752_repair
- Mode: repair
- Slice: 012G-critical-e2e-uat-smoke-scenarios
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
backend-impacted-results.md:FAIL: test_authenticated_user_without_tracer_permission_cannot_write_domain_rows (sfpcl_credit.tests.test_tracer_api.TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows)
backend-impacted-results.md:FAILED (failures=1, skipped=4)
```

## Last 50 lines: backend-impacted-results.md

```
Catalogue seeded: 199 permissions, 20 roles, 8 teams, 274 role-permission links.
E2E users seeded: e2e.tracer@sfpcl.example (role e2e_tracer, permission tracer.lifecycle.run); e2e.zero@sfpcl.example (role it_head, no permissions). Credit fixture: LOE2E00601, e2e.credit.finance@sfpcl.example, e2e.credit.manager@sfpcl.example.
........F
======================================================================
FAIL: test_authenticated_user_without_tracer_permission_cannot_write_domain_rows (sfpcl_credit.tests.test_tracer_api.TracerApiTests.test_authenticated_user_without_tracer_permission_cannot_write_domain_rows)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 57, in testPartExecutor
    yield
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 623, in run
    self._callTestMethod(testMethod)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 579, in _callTestMethod
    if method() is not None:
    ^^^^^^^^^^^^^^^^^
  File "/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/sfpcl_credit/tests/test_tracer_api.py", line 273, in test_authenticated_user_without_tracer_permission_cannot_write_domain_rows
    self.assertEqual(response.status_code, 403)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 873, in assertEqual
    assertion_func(first, second, msg=msg)
    ^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/unittest/case.py", line 866, in _baseAssertEqual
    raise self.failureException(msg)
    ^^^^^^^^^^^^^^^^^
AssertionError: 404 != 403

----------------------------------------------------------------------
Ran 1401 tests in 76.065s

FAILED (failures=1, skipped=4)
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Destroying test database for alias 'default'...
Total database setup took 48.986s
  Creating 'default' took 48.889s
  Cloning 'default' took 0.014s
  Cloning 'default' took 0.016s
  Cloning 'default' took 0.016s
  Cloning 'default' took 0.018s
  Cloning 'default' took 0.018s
  Cloning 'default' took 0.015s
Total database teardown took 0.014s
Total run took 125.759s

Duration milliseconds: 126363
Exit code: 1
```

## Authoritative validator diagnostics

These bounded excerpts come from orchestrator-owned trusted validation logs.
They take precedence over agent-authored review packets or evidence narratives.

```
Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-green-1-retry.log
  1) [chromium] › critical-uat-smoke.e2e.spec.ts:28:5 › critical UAT tracer proves the automated public journeys and retains the manual boundary 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-hlvpZA --remote-debugging-pipe --no-startup-window
    <launched> pid=62637
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-hlvpZA --remote-debugging-pipe --no-startup-window
      - <launched> pid=62637



Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-green-1.log
  1) [chromium] › critical-uat-smoke.e2e.spec.ts:28:5 › critical UAT tracer proves the automated public journeys and retains the manual boundary 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-hEb0nM --remote-debugging-pipe --no-startup-window
    <launched> pid=50338
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-hEb0nM --remote-debugging-pipe --no-startup-window
      - <launched> pid=50338
```

## Changed files (git status)

```
.ralph/runs/2026-07-25_074057_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-25_074057_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-25_074057_normal_run/backend-check-results.md
.ralph/runs/2026-07-25_074057_normal_run/backend-coverage-results.md
.ralph/runs/2026-07-25_074057_normal_run/backend-impacted-results.md
.ralph/runs/2026-07-25_074057_normal_run/backend-migrations-results.md
.ralph/runs/2026-07-25_074057_normal_run/backend-test-results.md
.ralph/runs/2026-07-25_074057_normal_run/backend-validation-lane-results.md
.ralph/runs/2026-07-25_074057_normal_run/build-results.md
.ralph/runs/2026-07-25_074057_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-25_074057_normal_run/candidate-hash-results.md
.ralph/runs/2026-07-25_074057_normal_run/changed-files.txt
.ralph/runs/2026-07-25_074057_normal_run/codex-settings.md
.ralph/runs/2026-07-25_074057_normal_run/diff-limits-results.md
.ralph/runs/2026-07-25_074057_normal_run/e2e-results.md
.ralph/runs/2026-07-25_074057_normal_run/evidence/critical-uat-scenario-matrix.json
.ralph/runs/2026-07-25_074057_normal_run/evidence/critical-uat-seed-manifest.json
.ralph/runs/2026-07-25_074057_normal_run/evidence/scenario-uat-matrix.md
.ralph/runs/2026-07-25_074057_normal_run/evidence/screenshots/run-1/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_074057_normal_run/evidence/seed-manifest.md
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/backend-check-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/backend-focused-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/backend-focused-green.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/backend-migrations-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-seed-guard-green.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-seed-guard-red.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-seed-preconditions-green.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-seed-preconditions-red.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-seed-production-green.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-seed-production-red.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/critical-uat-red.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/frontend-build-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/frontend-lint-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/frontend-typecheck-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/frontend-typecheck-initial.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/playwright-seed-final-green.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/playwright-seed-final.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/playwright-seed-green.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/playwright-seed-red.log
.ralph/runs/2026-07-25_074057_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_074057_normal_run/execution-plan.md
.ralph/runs/2026-07-25_074057_normal_run/failure-summary.md
.ralph/runs/2026-07-25_074057_normal_run/final-summary.md
.ralph/runs/2026-07-25_074057_normal_run/install-results.md
.ralph/runs/2026-07-25_074057_normal_run/lint-results.md
.ralph/runs/2026-07-25_074057_normal_run/no-op-check-results.md
.ralph/runs/2026-07-25_074057_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_074057_normal_run/preflight-results.md
.ralph/runs/2026-07-25_074057_normal_run/prompt.md
.ralph/runs/2026-07-25_074057_normal_run/protected-paths-check.md
.ralph/runs/2026-07-25_074057_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-25_074057_normal_run/review-packet.md
.ralph/runs/2026-07-25_074057_normal_run/risk-assessment.md
.ralph/runs/2026-07-25_074057_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-25_074057_normal_run/slice-status-transition-check.md
.ralph/runs/2026-07-25_074057_normal_run/test-results.md
.ralph/runs/2026-07-25_074057_normal_run/typecheck-results.md
.ralph/runs/2026-07-25_074057_normal_run/validated-commit-candidate.sha256
.ralph/runs/2026-07-25_082003_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_082003_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_082003_repair/backend-check-results.md
.ralph/runs/2026-07-25_082003_repair/backend-coverage-results.md
.ralph/runs/2026-07-25_082003_repair/backend-impacted-results.md
.ralph/runs/2026-07-25_082003_repair/backend-migrations-results.md
.ralph/runs/2026-07-25_082003_repair/backend-test-results.md
.ralph/runs/2026-07-25_082003_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-25_082003_repair/build-results.md
.ralph/runs/2026-07-25_082003_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_082003_repair/candidate-hash-results.md
.ralph/runs/2026-07-25_082003_repair/changed-files.txt
.ralph/runs/2026-07-25_082003_repair/codex-settings.md
.ralph/runs/2026-07-25_082003_repair/diff-limits-results.md
.ralph/runs/2026-07-25_082003_repair/e2e-results.md
.ralph/runs/2026-07-25_082003_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-25_082003_repair/evidence/screenshots/run-1/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/backend-focused-green.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/browser-infrastructure-probe-current.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/frontend-seed-focused-green.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/subsidiary-precondition-probe.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/tri-party-precondition-green.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/tri-party-precondition-red.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/tri-party-public-api-green.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/tri-party-seeded-probe-green.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_082003_repair/evidence/terminal-logs/trusted-browser-repro-red.log
.ralph/runs/2026-07-25_082003_repair/execution-plan.md
.ralph/runs/2026-07-25_082003_repair/failure-summary.md
.ralph/runs/2026-07-25_082003_repair/final-summary.md
.ralph/runs/2026-07-25_082003_repair/install-results.md
.ralph/runs/2026-07-25_082003_repair/lint-results.md
.ralph/runs/2026-07-25_082003_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_082003_repair/preflight-results.md
.ralph/runs/2026-07-25_082003_repair/prompt.md
.ralph/runs/2026-07-25_082003_repair/protected-paths-check.md
.ralph/runs/2026-07-25_082003_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_082003_repair/review-packet.md
.ralph/runs/2026-07-25_082003_repair/risk-assessment.md
.ralph/runs/2026-07-25_082003_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_082003_repair/slice-status-transition-check.md
.ralph/runs/2026-07-25_082003_repair/test-results.md
.ralph/runs/2026-07-25_082003_repair/typecheck-results.md
.ralph/runs/2026-07-25_082003_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-25_083817_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_083817_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_083817_repair/backend-check-results.md
.ralph/runs/2026-07-25_083817_repair/backend-coverage-results.md
.ralph/runs/2026-07-25_083817_repair/backend-impacted-results.md
.ralph/runs/2026-07-25_083817_repair/backend-migrations-results.md
.ralph/runs/2026-07-25_083817_repair/backend-test-results.md
.ralph/runs/2026-07-25_083817_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-25_083817_repair/build-results.md
.ralph/runs/2026-07-25_083817_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_083817_repair/candidate-hash-results.md
.ralph/runs/2026-07-25_083817_repair/changed-files.txt
.ralph/runs/2026-07-25_083817_repair/codex-settings.md
.ralph/runs/2026-07-25_083817_repair/diff-limits-results.md
.ralph/runs/2026-07-25_083817_repair/e2e-results.md
.ralph/runs/2026-07-25_083817_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-25_083817_repair/evidence/screenshots/run-1/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/critical-uat-spec-collection-green.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/frontend-seed-focused-green.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/subsidiary-replay-contract-green.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_083817_repair/evidence/terminal-logs/trusted-browser-replay-red.log
.ralph/runs/2026-07-25_083817_repair/execution-plan.md
.ralph/runs/2026-07-25_083817_repair/failure-summary.md
.ralph/runs/2026-07-25_083817_repair/final-summary.md
.ralph/runs/2026-07-25_083817_repair/install-results.md
.ralph/runs/2026-07-25_083817_repair/lint-results.md
.ralph/runs/2026-07-25_083817_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_083817_repair/preflight-results.md
.ralph/runs/2026-07-25_083817_repair/prompt.md
.ralph/runs/2026-07-25_083817_repair/protected-paths-check.md
.ralph/runs/2026-07-25_083817_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_083817_repair/review-packet.md
.ralph/runs/2026-07-25_083817_repair/risk-assessment.md
.ralph/runs/2026-07-25_083817_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_083817_repair/slice-status-transition-check.md
.ralph/runs/2026-07-25_083817_repair/test-results.md
.ralph/runs/2026-07-25_083817_repair/typecheck-results.md
.ralph/runs/2026-07-25_083817_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-25_085034_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_085034_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_085034_repair/backend-check-results.md
.ralph/runs/2026-07-25_085034_repair/backend-coverage-results.md
.ralph/runs/2026-07-25_085034_repair/backend-impacted-results.md
.ralph/runs/2026-07-25_085034_repair/backend-migrations-results.md
.ralph/runs/2026-07-25_085034_repair/backend-test-results.md
.ralph/runs/2026-07-25_085034_repair/backend-validation-lane-results.md
.ralph/runs/2026-07-25_085034_repair/build-results.md
.ralph/runs/2026-07-25_085034_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_085034_repair/candidate-hash-results.md
.ralph/runs/2026-07-25_085034_repair/changed-files.txt
.ralph/runs/2026-07-25_085034_repair/codex-settings.md
.ralph/runs/2026-07-25_085034_repair/diff-limits-results.md
.ralph/runs/2026-07-25_085034_repair/e2e-results.md
.ralph/runs/2026-07-25_085034_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-25_085034_repair/evidence/screenshots/run-1/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/backend-check-migrations-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/backend-focused-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/critical-interest-precondition-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/critical-interest-precondition-red.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/critical-uat-spec-collection-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/frontend-build-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/frontend-lint-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/frontend-seed-focused-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/frontend-typecheck-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-acceptance-green-2.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-acceptance-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-repro-red.log
.ralph/runs/2026-07-25_085034_repair/execution-plan.md
.ralph/runs/2026-07-25_085034_repair/failure-summary.md
.ralph/runs/2026-07-25_085034_repair/final-summary.md
.ralph/runs/2026-07-25_085034_repair/install-results.md
.ralph/runs/2026-07-25_085034_repair/lint-results.md
.ralph/runs/2026-07-25_085034_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_085034_repair/preflight-results.md
.ralph/runs/2026-07-25_085034_repair/prompt.md
.ralph/runs/2026-07-25_085034_repair/protected-paths-check.md
.ralph/runs/2026-07-25_085034_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_085034_repair/review-packet.md
.ralph/runs/2026-07-25_085034_repair/risk-assessment.md
.ralph/runs/2026-07-25_085034_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_085034_repair/slice-status-transition-check.md
.ralph/runs/2026-07-25_085034_repair/test-results.md
.ralph/runs/2026-07-25_085034_repair/typecheck-results.md
.ralph/runs/2026-07-25_085034_repair/validated-commit-candidate.sha256
.ralph/runs/2026-07-25_090921_repair/codex-settings.md
.ralph/runs/2026-07-25_090921_repair/evidence/final-summary.md
.ralph/runs/2026-07-25_090921_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-25_090921_repair/evidence/review-packet.md
.ralph/runs/2026-07-25_090921_repair/evidence/risk-assessment.md
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/diagnostic/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/run-1/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-1/critical-uat-permission-negative.png
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-1/critical-uat-scenario-matrix.json
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-1/critical-uat-seed-manifest.json
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-1/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-2/critical-uat-permission-negative.png
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-2/critical-uat-scenario-matrix.json
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-2/critical-uat-seed-manifest.json
.ralph/runs/2026-07-25_090921_repair/evidence/screenshots/trusted-browser-run-2/critical-uat-standard-loan.png
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/auditor-fixture-green-2.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/auditor-fixture-green.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/auditor-fixture-red.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/django-check-final.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/dpd-cutoff-and-seed-green.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/dpd-cutoff-public-contract-red-2.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/dpd-cutoff-public-contract-red.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/focused-backend-final-green.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/frontend-build-final.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/frontend-lint-final.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/frontend-seed-final-green.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/frontend-seed-focused-green.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/frontend-typecheck-final.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/migration-check-final.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/transfer-request-contract-red.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/trusted-browser-acceptance-fixed-1.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/trusted-browser-acceptance-green-1-retry.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/trusted-browser-acceptance-green-1.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/trusted-browser-acceptance-green-2.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/trusted-browser-acceptance-maintainer-1.log
.ralph/runs/2026-07-25_090921_repair/evidence/terminal-logs/trusted-browser-acceptance-maintainer-2.log
.ralph/runs/2026-07-25_090921_repair/evidence/trusted-browser-screenshots-1.sha256
.ralph/runs/2026-07-25_090921_repair/evidence/trusted-browser-screenshots-2.sha256
.ralph/runs/2026-07-25_090921_repair/execution-plan.md
.ralph/runs/2026-07-25_090921_repair/final-summary.md
.ralph/runs/2026-07-25_090921_repair/preflight-results.md
.ralph/runs/2026-07-25_090921_repair/prompt.md
.ralph/runs/2026-07-25_090921_repair/review-packet.md
.ralph/runs/2026-07-25_090921_repair/risk-assessment.md
.ralph/runs/2026-07-25_094752_repair/agent-declared-result-check.md
.ralph/runs/2026-07-25_094752_repair/artifact-quality-check.md
.ralph/runs/2026-07-25_094752_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_094752_repair/changed-files.txt
.ralph/runs/2026-07-25_094752_repair/codex-settings.md
.ralph/runs/2026-07-25_094752_repair/diff-limits-results.md
.ralph/runs/2026-07-25_094752_repair/evidence/repair-diagnosis.md
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/django-check.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/dpd-cutoff-and-seed-green.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/frontend-seed-focused-green.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/migration-check.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/trusted-browser-acceptance-green-1-retry.log
.ralph/runs/2026-07-25_094752_repair/evidence/terminal-logs/trusted-browser-acceptance-green-1.log
.ralph/runs/2026-07-25_094752_repair/execution-plan.md
.ralph/runs/2026-07-25_094752_repair/final-summary.md
.ralph/runs/2026-07-25_094752_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_094752_repair/preflight-results.md
.ralph/runs/2026-07-25_094752_repair/prompt.md
.ralph/runs/2026-07-25_094752_repair/protected-paths-check.md
.ralph/runs/2026-07-25_094752_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_094752_repair/review-packet.md
.ralph/runs/2026-07-25_094752_repair/risk-assessment.md
.ralph/runs/2026-07-25_094752_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_094752_repair/slice-status-transition-check.md
sfpcl-lms/e2e/critical-uat-smoke.e2e.spec.ts
sfpcl-lms/playwright.seed.ts
sfpcl-lms/src/playwright.seed.test.ts
sfpcl_credit/identity/management/commands/seed_critical_uat_e2e_fixture.py
sfpcl_credit/tests/test_production_demo_isolation.py
sfpcl_credit/tests/test_seed_critical_uat_e2e_fixture.py
```
