# Execution Plan

Selected slice: 006Y3-member-registry-and-identity-change-approval-closure
Mode: repair

## Demonstrated Failure

Independent validation ran `e2e/member-governance-closure.e2e.spec.ts` twice. Both runs stopped on
the obsolete `member-reverification` visual baseline, while the slice declares five different
governance-closure screenshots. Consequently neither run exercised the new create, update,
two-actor identity approval, or denial contract, and the declared evidence files were absent.

## Repair Plan

1. Preserve the existing backend and frontend implementation; change only the stale trusted-browser
   contract and repair-run artifacts.
2. Turn the declared contract into a red-capable Playwright flow using real API-backed sessions:
   create a member, update it with canonical refetch, request a verified-identity correction,
   approve it as a distinct authorized actor, and prove a denied actor cannot mutate governance.
3. Emit exactly the five screenshot filenames declared by the slice. Avoid snapshot bootstrapping or
   self-deleting baselines; the trusted contract must assert behavior and save evidence deterministically.
4. Run Playwright collection and the focused contract locally. If Chromium is sandbox-blocked, retain
   collection/non-browser evidence and defer the authoritative two-run browser verdict to Ralph.
5. Run the required frontend/backend quality gates proportionate to the E2E-only repair, save logs,
   and update changed-files, risk assessment, review packet, final summary, state, progress, handoff,
   and slice status without changing the already-complete product result.

## Scope Guard

No production code, source document, protected file, package, migration, or business rule will be
changed. The next queued slices were already sharpened during the original run and will not be
broadened in repair mode.
