# Diagnosis and Red Evidence

## Authoritative independent reproduction

Command run by the orchestrator in the preceding repair:

```text
RALPH_EVIDENCE_DIR=<run-evidence>/screenshots E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/staff-documentation-workspace.e2e.spec.ts
```

The real-Django flow passed login, workspace reads, upload, correction, rejected validation,
tampered-action 404, restricted-download 404, and the first two screenshots, then failed exactly:

```text
ReferenceError: termSheet is not defined
  at e2e/staff-documentation-workspace.e2e.spec.ts:78:79
1 failed
Exit code: 1
```

## Local browser attempt

The same command was run in this coding sandbox with the current run evidence directory. Chromium
was denied before page creation by macOS bootstrap services:

```text
FATAL: mach_port_rendezvous.cc(399)] Check failed: kr == KERN_SUCCESS.
bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer: Permission denied (1100)
Exit code: 1
```

Per the slice's `localhost-e2e-server` contract, this environment denial does not replace the
orchestrator's exact application-level reproduction and no screenshots are fabricated.

## Tight static regression loop (red)

The browser spec is outside the repository's normal `tsconfig.json` include. A focused TypeScript
compile was reduced to an exact verdict for the demonstrated undeclared locator:

```text
output=$(./node_modules/.bin/tsc --noEmit --strict --skipLibCheck --moduleResolution Bundler --module ESNext --target ES2022 --allowSyntheticDefaultImports e2e/staff-documentation-workspace.e2e.spec.ts 2>&1 || true); if printf '%s\n' "$output" | rg -q "Cannot find name 'termSheet'"; then printf "RED: browser spec references undeclared termSheet locator\n"; exit 1; fi; printf "GREEN: browser spec has no undeclared termSheet locator\n"

RED: browser spec references undeclared termSheet locator
Exit code: 1
```

The search minimisation found one `termSheet` use and no declaration. `powerOfAttorney` is the
declared current checklist-row locator and is used throughout the same scenario. This confirms the
correct hypothesis: line 78 retained a stale locator name after the fixture changed from the
already-complete Term Sheet to the pending Power of Attorney.
