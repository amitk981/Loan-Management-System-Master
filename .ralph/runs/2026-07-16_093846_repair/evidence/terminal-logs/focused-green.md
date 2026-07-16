# Focused Green Evidence

## Exact undeclared-locator regression

```text
output=$(./node_modules/.bin/tsc --noEmit --strict --skipLibCheck --moduleResolution Bundler --module ESNext --target ES2022 --allowSyntheticDefaultImports e2e/staff-documentation-workspace.e2e.spec.ts 2>&1 || true); if printf '%s\n' "$output" | rg -q "Cannot find name 'termSheet'"; then printf "RED: browser spec references undeclared termSheet locator\n"; exit 1; fi; printf "GREEN: browser spec has no undeclared termSheet locator\n"

GREEN: browser spec has no undeclared termSheet locator
Exit code: 0
```

## Playwright contract collection

```text
RALPH_EVIDENCE_DIR=<current-run>/evidence/screenshots E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- --list e2e/staff-documentation-workspace.e2e.spec.ts

Listing tests:
  [chromium] › staff-documentation-workspace.e2e.spec.ts:16:5 › 008M3 executes every staff documentation action through real Django
Total: 1 test in 1 file
Exit code: 0
```

The executable browser run itself is intentionally deferred to independent validation because the
coding sandbox denies Chromium's macOS bootstrap registration before page creation.
