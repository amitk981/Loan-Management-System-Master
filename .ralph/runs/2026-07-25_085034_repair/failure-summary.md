# Failure Summary

- Run: 2026-07-25_085034_repair
- Mode: repair
- Slice: 012G-critical-e2e-uat-smoke-scenarios
- Failed checks: 1

Repair mode: diagnose from this file first; open the full gate logs in this run
folder only when a tail below is insufficient.

## All FAIL markers

```
e2e-results.md:- FAIL: first trusted slice-specific browser run did not pass.
e2e-results.md:- FAIL: first run screenshot evidence or manifest is incomplete.
e2e-results.md:- FAIL: second run screenshot evidence or manifest is incomplete.
```

## Last 50 lines: e2e-results.md

```
# e2e Results

- PASS: slice-specific trusted browser contract is valid.
- PASS: README E2E command resolves the shared venv through Git's common directory.
- PASS: Playwright pins the dashboard baseline timezone to Asia/Kolkata.
- FAIL: first trusted slice-specific browser run did not pass.
- SKIP: second trusted slice-specific browser run deferred because the first run failed.
- FAIL: first run screenshot evidence or manifest is incomplete.
- FAIL: second run screenshot evidence or manifest is incomplete.

Declared specs:
- e2e/critical-uat-smoke.e2e.spec.ts
Declared screenshots:
- critical-uat-standard-loan.png
- critical-uat-permission-negative.png
```

## Authoritative validator diagnostics

These bounded excerpts come from orchestrator-owned trusted validation logs.
They take precedence over agent-authored review packets or evidence narratives.

```
Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-1.log
  1) [chromium] › critical-uat-smoke.e2e.spec.ts:27:5 › critical UAT tracer proves the automated public journeys and retains the manual boundary › UAT-014/015/016/017: direct/subsidiary receipts, interest, DPD, and replay safety 

    Error: expect(received).toMatchObject(expected)

    - Expected  - 1
    + Received  + 1


Duration milliseconds: 79471
Exit code: 1
Screenshot evidence exit code: 1
Screenshot manifest: /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_074057_normal_run/.ralph/runs/2026-07-25_085034_repair/evidence/trusted-browser-screenshots-1.sha256

Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-green-2.log
  1) [chromium] › critical-uat-smoke.e2e.spec.ts:27:5 › critical UAT tracer proves the automated public journeys and retains the manual boundary 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-nZ6Bv1 --remote-debugging-pipe --no-startup-window
    <launched> pid=37531
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-nZ6Bv1 --remote-debugging-pipe --no-startup-window
      - <launched> pid=37531



Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-green.log
  1) [chromium] › critical-uat-smoke.e2e.spec.ts:27:5 › critical UAT tracer proves the automated public journeys and retains the manual boundary 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-u0rfn2 --remote-debugging-pipe --no-startup-window
    <launched> pid=36992
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-u0rfn2 --remote-debugging-pipe --no-startup-window
      - <launched> pid=36992
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
.ralph/runs/2026-07-25_085034_repair/candidate-fast-check-results.md
.ralph/runs/2026-07-25_085034_repair/changed-files.txt
.ralph/runs/2026-07-25_085034_repair/codex-settings.md
.ralph/runs/2026-07-25_085034_repair/diff-limits-results.md
.ralph/runs/2026-07-25_085034_repair/evidence/repair-diagnosis.md
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
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-acceptance-green-2.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-acceptance-green.log
.ralph/runs/2026-07-25_085034_repair/evidence/terminal-logs/trusted-browser-repro-red.log
.ralph/runs/2026-07-25_085034_repair/execution-plan.md
.ralph/runs/2026-07-25_085034_repair/final-summary.md
.ralph/runs/2026-07-25_085034_repair/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_085034_repair/preflight-results.md
.ralph/runs/2026-07-25_085034_repair/prompt.md
.ralph/runs/2026-07-25_085034_repair/protected-paths-check.md
.ralph/runs/2026-07-25_085034_repair/ralph-artifact-validation.md
.ralph/runs/2026-07-25_085034_repair/review-packet.md
.ralph/runs/2026-07-25_085034_repair/risk-assessment.md
.ralph/runs/2026-07-25_085034_repair/slice-queue-lint.md
.ralph/runs/2026-07-25_085034_repair/slice-status-transition-check.md
sfpcl-lms/e2e/critical-uat-smoke.e2e.spec.ts
sfpcl-lms/playwright.seed.ts
sfpcl-lms/src/playwright.seed.test.ts
sfpcl_credit/identity/management/commands/seed_critical_uat_e2e_fixture.py
sfpcl_credit/tests/test_production_demo_isolation.py
sfpcl_credit/tests/test_seed_critical_uat_e2e_fixture.py
```
