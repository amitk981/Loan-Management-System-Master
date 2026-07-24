# Failure Summary

- Run: 2026-07-25_032730_normal_run
- Mode: normal_run
- Slice: 011PE-grievance-audit-archive-frontend-wiring
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
- e2e/default-closure-compliance-staff.e2e.spec.ts
Declared screenshots:
- default-case-workbench.png
- recovery-approval-decision.png
- closure-readiness-blockers.png
- compliance-trackers.png
- grievance-resolution.png
```

## Authoritative validator diagnostics

These bounded excerpts come from orchestrator-owned trusted validation logs.
They take precedence over agent-authored review packets or evidence narratives.

```
Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-1.log
  1) [chromium] › default-closure-compliance-staff.e2e.spec.ts:124:5 › S58-S61 show named server readiness blockers and keep NOC blocked 

    Error: locator.click: Error: strict mode violation: getByRole('button', { name: 'Archive' }) resolved to 2 elements:
        1) <button class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group bg-green-50 text-green-700 ">…</button> aka getByRole('button', { name: 'Closure & Archive' })
        2) <button type="button" class="px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors border-transparent text-slate-500 hover:text-slate-700">Archive</button> aka getByRole('button', { name: 'Archive', exact: true })

    Call log:
      - waiting for getByRole('button', { name: 'Archive' })


      144 |   await page.getByRole('button', { name: 'Security Return / Unpledge' }).click();
      145 |   await expect(page.getByText('Security return remains blocked until the backend creates a financially-closed loan identity.')).toBeVisible();
    > 146 |   await page.getByRole('button', { name: 'Archive' }).click();
          |                                                       ^
      147 |   await expect(page.getByText('Archive remains blocked until financial closure is recorded.')).toBeVisible();
      148 |   expect(mutations).toEqual([]);
      149 |   await page.screenshot({
        at /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_032730_normal_run/sfpcl-lms/e2e/default-closure-compliance-staff.e2e.spec.ts:146:55


Duration milliseconds: 66380
Exit code: 1
Screenshot evidence exit code: 1
Screenshot manifest: /Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_032730_normal_run/.ralph/runs/2026-07-25_032730_normal_run/evidence/trusted-browser-screenshots-1.sha256

Authoritative source: evidence/terminal-logs/trusted-browser-acceptance-2.log
  1) [chromium] › default-closure-compliance-staff.e2e.spec.ts:68:5 › S53-S57 render governed notes, record the decision, and open canonical recovery execution 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-Shp4Xa --remote-debugging-pipe --no-startup-window
    <launched> pid=45498
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-Shp4Xa --remote-debugging-pipe --no-startup-window
      - <launched> pid=45498


  2) [chromium] › default-closure-compliance-staff.e2e.spec.ts:124:5 › S58-S61 show named server readiness blockers and keep NOC blocked 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-21Ho6F --remote-debugging-pipe --no-startup-window
    <launched> pid=45500
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-21Ho6F --remote-debugging-pipe --no-startup-window
      - <launched> pid=45500


  3) [chromium] › default-closure-compliance-staff.e2e.spec.ts:156:5 › S62-S67 show canonical compliance trackers and keep auditor access read-only 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-6f2LwV --remote-debugging-pipe --no-startup-window
    <launched> pid=45502
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-6f2LwV --remote-debugging-pipe --no-startup-window
      - <launched> pid=45502


  4) [chromium] › default-closure-compliance-staff.e2e.spec.ts:187:5 › S68 resolves a canonical grievance and reads archive manifests without mutation controls 

    Error: browserType.launch: Target page, context or browser has been closed
    Browser logs:

    <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-7OeMs5 --remote-debugging-pipe --no-startup-window
    <launched> pid=45504
    [pid=45504] <process did exit: exitCode=null, signal=SIGABRT>
    [pid=45504] starting temporary directories cleanup
    Call log:
      - <launching> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome --disable-field-trial-config --disable-background-networking --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-back-forward-cache --disable-breakpad --disable-client-side-phishing-detection --disable-component-extensions-with-background-pages --disable-component-update --no-default-browser-check --disable-default-apps --disable-dev-shm-usage --disable-extensions --disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker --allow-pre-commit-input --disable-hang-monitor --disable-ipc-flooding-protection --disable-popup-blocking --disable-prompt-on-repost --disable-renderer-backgrounding --force-color-profile=srgb --metrics-recording-only --no-first-run --enable-automation --password-store=basic --use-mock-keychain --no-service-autorun --export-tagged-pdf --disable-search-engine-choice-screen --unsafely-disable-devtools-self-xss-warnings --enable-use-zoom-for-dsf=false --use-angle --headless --hide-scrollbars --mute-audio --blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4 --no-sandbox --user-data-dir=/var/folders/zq/3s8051dx39q0tk8whcqx44y00000gn/T/playwright_chromiumdev_profile-7OeMs5 --remote-debugging-pipe --no-startup-window
      - <launched> pid=45504
      - [pid=45504] <process did exit: exitCode=null, signal=SIGABRT>
      - [pid=45504] starting temporary directories cleanup
```

## Changed files (git status)

```
.ralph/runs/2026-07-25_032730_normal_run/agent-declared-result-check.md
.ralph/runs/2026-07-25_032730_normal_run/artifact-quality-check.md
.ralph/runs/2026-07-25_032730_normal_run/candidate-fast-check-results.md
.ralph/runs/2026-07-25_032730_normal_run/changed-files.txt
.ralph/runs/2026-07-25_032730_normal_run/codex-settings.md
.ralph/runs/2026-07-25_032730_normal_run/diff-limits-results.md
.ralph/runs/2026-07-25_032730_normal_run/e2e-results.md
.ralph/runs/2026-07-25_032730_normal_run/evidence/011p-five-owner-mock-removal-matrix.md
.ralph/runs/2026-07-25_032730_normal_run/evidence/011pe-role-action-blocker-matrix.md
.ralph/runs/2026-07-25_032730_normal_run/evidence/browser-acceptance.md
.ralph/runs/2026-07-25_032730_normal_run/evidence/review-summary.md
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/011pe-final-focused.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/011pe-frontend-green.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/011pe-frontend-red.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/backend-check.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/backend-migrations-check.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/browser-infrastructure-probe.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/codex-summary.md
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/frontend-build.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/frontend-full-tests.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/frontend-lint.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/frontend-typecheck.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/orchestrator-backend-deps.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/orchestrator-frontend-deps.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/terminal-logs/trusted-browser-acceptance-2.log
.ralph/runs/2026-07-25_032730_normal_run/evidence/test-summary.md
.ralph/runs/2026-07-25_032730_normal_run/execution-plan.md
.ralph/runs/2026-07-25_032730_normal_run/final-summary.md
.ralph/runs/2026-07-25_032730_normal_run/no-op-check-results.md
.ralph/runs/2026-07-25_032730_normal_run/orchestrator-ownership-check.md
.ralph/runs/2026-07-25_032730_normal_run/preflight-results.md
.ralph/runs/2026-07-25_032730_normal_run/prompt.md
.ralph/runs/2026-07-25_032730_normal_run/protected-paths-check.md
.ralph/runs/2026-07-25_032730_normal_run/ralph-artifact-validation.md
.ralph/runs/2026-07-25_032730_normal_run/review-packet.md
.ralph/runs/2026-07-25_032730_normal_run/risk-assessment.md
.ralph/runs/2026-07-25_032730_normal_run/slice-queue-lint.md
.ralph/runs/2026-07-25_032730_normal_run/slice-status-transition-check.md
sfpcl-lms/e2e/default-closure-compliance-staff.e2e.spec.ts
sfpcl-lms/src/pages/compliance/AuditArchiveHub.test.tsx
sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx
sfpcl-lms/src/pages/compliance/GrievancesHub.test.tsx
sfpcl-lms/src/pages/compliance/GrievancesHub.tsx
sfpcl-lms/src/services/authSession.test.ts
sfpcl-lms/src/services/authSession.ts
sfpcl-lms/src/services/recoveryApi.test.ts
sfpcl-lms/src/services/recoveryApi.ts
```
